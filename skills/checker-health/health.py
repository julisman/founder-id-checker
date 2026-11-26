#!/usr/bin/env python3
"""The health check for founder-id-checker. Standard library only, no network.

Reads the real monthly numbers of a business that is already open
(checker/actuals.json, written by checker-intake) and computes every check, the
verdict and the fixes ranked by Rupiah a month. The verdict is computed, never
written by hand:

    Sehat       every check that has data passes
    Waspada     at least one check is a warning, none is critical
    Kritis      at least one check is critical
    Incomplete  there are no months of numbers yet

The checks (each one ok, warn or bad, or skipped when its data is missing):
    margin        net profit as a share of net sales
    breakeven     recent net sales against the break-even
    trend         the last 3 months against the 3 before
    direct_cost   direct cost (food cost, COGS, materials) against the target
    labour        labour against the target
    owner         what the owner takes against what the business earns
    owner_pay     the profit after paying for the owner's own work, if owner_fair_salary is given
    debt          the monthly debt payment against the profit
    cash          the cash on hand against the weekly operating cost, and the runway if cash is shrinking
    platforms     how much of gross sales goes through apps and marketplaces
    customers     the listings' own overall rating     (checker/customers.json, from checker-customers)
    compliance    the permits, certificates and taxes  (checker/compliance.json, from checker-compliance)

A failed customers check shows as failed but makes the verdict Waspada at most:
a poor rating is a warning about sales to come, not a verdict on the money.

    python3 health.py checker/actuals.json                 # writes checker/health.md and checker/health.json
    python3 health.py checker/actuals.json --check         # print the verdict; exit 0 Sehat, 1 Waspada, 2 Kritis, 3 Incomplete
    python3 health.py checker/actuals.json --channels      # print the channel table only
"""

import argparse
import json
import os
import re
import sys

WEEKS_PER_MONTH = 4.33
TYPES = ("fnb", "retail", "online", "service", "other")
# Default targets by business type: (direct cost %, labour %). None = no default, the owner must give one.
DEFAULT_TARGETS = {
    "fnb": (0.35, 0.25),
    "retail": (0.70, 0.15),
    "online": (0.65, 0.15),
    "service": (0.30, 0.40),
    "other": (None, None),
}
DEFAULT_NET_MARGIN = 0.10
BAD_POINTS = 0.05          # a cost this many points over target is critical, not just a warning
PLATFORM_WARN_SHARE = 0.60  # apps and marketplaces together above this share of gross sales
MONEY_FIELDS = ("direct_cost", "labour", "fixed_costs")
OPTIONAL_MONEY = ("discounts", "pph_final", "other_costs", "owner_drawings", "debt_payment")
WARN_ONLY = ("customers",)  # checks whose failure caps the verdict at Waspada
MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
PLATFORM_MIN_RATE = 0.05  # a channel whose fees are above this share of gross is an app or marketplace, not QRIS or a card
COMPLIANCE_STATUS = ("ok", "missing", "expired", "unknown")
COMPLIANCE_SEVERITY = ("blocks_sales", "penalty", "advised")
STATUS_MARK = {"ok": "✓", "warn": "!", "bad": "✗"}


class ActualsError(ValueError):
    pass


def money(v):
    """Rp1.250.000: no decimals, dots for thousands."""
    sign = "-" if v < 0 else ""
    return "%sRp%s" % (sign, "{:,.0f}".format(abs(round(v))).replace(",", "."))


def pct(v, digits=1):
    return ("%." + str(digits) + "f%%") % (v * 100)


def _num(x, where, allow_negative=False):
    if isinstance(x, bool):
        raise ActualsError("%s is not a number: %r" % (where, x))
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise ActualsError("%s is not a number: %r" % (where, x))
    if v < 0 and not allow_negative:
        raise ActualsError("%s is negative: %r" % (where, x))
    return v


def load(path):
    with open(path, encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as e:
            raise ActualsError("%s is not valid JSON: %s" % (path, e))


def _read_optional(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None


# ---------------------------------------------------------------- one month

def month_numbers(m, i):
    where = "months[%d] (%s)" % (i, m.get("month", "?"))
    if not MONTH_RE.match(str(m.get("month", ""))):
        raise ActualsError("%s: month must be YYYY-MM, like 2026-09" % where)
    chans = m.get("channels")
    if not isinstance(chans, dict) or not chans:
        raise ActualsError("%s has no channels: give at least one, e.g. {\"walk-in\": {\"gross\": ...}}" % where)
    channels = {}
    for name, c in chans.items():
        if not isinstance(c, dict) or "gross" not in c:
            raise ActualsError("%s channel %r needs a gross" % (where, name))
        channels[name] = {
            "gross": _num(c["gross"], "%s channel %r gross" % (where, name)),
            "commission": _num(c.get("commission", 0), "%s channel %r commission" % (where, name)),
            "orders": _num(c["orders"], "%s channel %r orders" % (where, name)) if c.get("orders") is not None else None,
        }
        if "platform" in c and not isinstance(c["platform"], bool):
            raise ActualsError("%s channel %r: platform must be true or false" % (where, name))
        if "platform" in c:
            channels[name]["platform"] = c["platform"]
        if channels[name]["commission"] > channels[name]["gross"]:
            raise ActualsError("%s channel %r: commission is more than gross sales" % (where, name))
    for f in MONEY_FIELDS:
        if f not in m:
            raise ActualsError("%s is missing %s (write 0 if there truly was none)" % (where, f))
    n = {"month": m["month"], "channels": channels}
    for f in MONEY_FIELDS:
        n[f] = _num(m[f], "%s %s" % (where, f))
    for f in OPTIONAL_MONEY:
        n[f] = _num(m.get(f, 0) or 0, "%s %s" % (where, f))
    n["days_open"] = _num(m.get("days_open", 30), "%s days_open" % where)
    if n["days_open"] <= 0:
        raise ActualsError("%s days_open must be above 0" % where)
    gross = sum(c["gross"] for c in channels.values())
    commission = sum(c["commission"] for c in channels.values())
    net = gross - n["discounts"] - commission
    if net <= 0:
        raise ActualsError("%s: net sales are %s; check gross, discounts and commission" % (where, money(net)))
    n["gross"] = gross
    n["commission"] = commission
    n["net_sales"] = net
    n["net_profit"] = net - n["direct_cost"] - n["labour"] - n["fixed_costs"] - n["pph_final"] - n["other_costs"]
    # money the business keeps after the owner and the debt: the cash it adds (or loses) in a month
    n["kept"] = n["net_profit"] - n["owner_drawings"] - n["debt_payment"]
    # cash that leaves in a month to keep the doors open (not counting the owner or the debt)
    n["operating_out"] = n["direct_cost"] + n["labour"] + n["fixed_costs"] + n["pph_final"] + n["other_costs"]
    return n


def _month_no(month):
    y, m = month.split("-")
    return int(y) * 12 + int(m) - 1


def missing_months(months):
    """The calendar months between the first and the last that have no numbers."""
    have = set(_month_no(m["month"]) for m in months)
    lo, hi = min(have), max(have)
    return ["%04d-%02d" % (n // 12, n % 12 + 1) for n in range(lo, hi + 1) if n not in have]


def _span(months):
    return months[0]["month"] if len(months) == 1 else "%s to %s" % (months[0]["month"], months[-1]["month"])


def _avg(months, key):
    return sum(m[key] for m in months) / float(len(months))


# ---------------------------------------------------------------- the whole business

def analyse(actuals, customers=None, compliance=None):
    """Return a dict with the numbers, the checks, the fixes and the verdict."""
    if not isinstance(actuals, dict):
        raise ActualsError("actuals must be a JSON object")
    btype = actuals.get("type", "other")
    if btype not in TYPES:
        raise ActualsError("type must be one of %s, not %r" % (", ".join(TYPES), btype))
    raw_months = actuals.get("months") or []
    months = sorted((month_numbers(m, i) for i, m in enumerate(raw_months)), key=lambda m: m["month"])
    seen = set()
    for m in months:
        if m["month"] in seen:
            raise ActualsError("month %s appears twice" % m["month"])
        seen.add(m["month"])
    out = {"missing_months": missing_months(months) if months else [], "business": actuals.get("business") or "The business", "type": btype, "months": months,
           "estimates": list(actuals.get("estimates") or []), "checks": [], "fixes": []}
    if not months:
        out["verdict"] = "Incomplete"
        return out

    targets = actuals.get("targets") or {}
    d_dc, d_lab = DEFAULT_TARGETS[btype]
    t_dc = targets.get("direct_cost_pct", d_dc)
    t_lab = targets.get("labour_pct", d_lab)
    t_margin = targets.get("net_margin_pct", DEFAULT_NET_MARGIN)
    out["targets"] = {
        "direct_cost_pct": t_dc, "labour_pct": t_lab, "net_margin_pct": t_margin,
        "source": {k: ("owner" if k in targets else ("default" if k == "net_margin_pct" else "default for %s" % btype))
                   for k in ("direct_cost_pct", "labour_pct", "net_margin_pct")},
    }

    recent = months[-3:]
    R = {k: _avg(recent, k) for k in ("gross", "commission", "discounts", "net_sales", "direct_cost", "labour",
                                       "fixed_costs", "pph_final", "other_costs", "net_profit", "owner_drawings",
                                       "debt_payment", "kept", "operating_out", "days_open")}
    out["recent"] = R
    out["recent_months"] = [m["month"] for m in recent]
    net = R["net_sales"]
    variable = R["direct_cost"] + R["pph_final"]
    ratio = (net - variable) / net  # what each Rp1 of net sales leaves to pay labour, fixed costs and profit
    out["contribution_ratio"] = ratio
    fixed_like = R["labour"] + R["fixed_costs"] + R["other_costs"]
    be = fixed_like / ratio if ratio > 0 else None
    out["breakeven_month"] = be
    out["breakeven_day"] = be / R["days_open"] if be is not None else None
    out["channels"] = channel_table(recent)
    checks, fixes = out["checks"], out["fixes"]

    # Every sentence comes in English and Indonesian: (en, id). The English one is "text", the Indonesian "text_id".
    def check(cid, status, text, **extra):
        c = {"id": cid, "status": status, "text": text[0], "text_id": text[1]}
        c.update(extra)
        checks.append(c)

    def fix(cid, rupiah, text, skill):
        if rupiah > 0:
            fixes.append({"id": cid, "rupiah_per_month": round(rupiah), "text": text[0], "text_id": text[1], "skill": skill})

    def J(*parts):  # join (en, id) pairs with a space
        return (" ".join(p[0] for p in parts if p[0]), " ".join(p[1] for p in parts if p[1]))

    P = pct
    Pi = lambda v, d=1: pct(v, d).replace(".", ",")  # 23,6% in Indonesian
    label = ("the last %d months" % len(recent), "%d bulan terakhir" % len(recent)) if len(recent) > 1 else (recent[0]["month"],) * 2

    # margin
    margin = R["net_profit"] / net
    out["net_margin"] = margin
    if margin < 0:
        check("margin", "bad", ("The business LOSES %s a month (%s of net sales) over %s." % (money(-R["net_profit"]), P(margin), label[0]),
                                "Usaha RUGI %s sebulan (%s dari penjualan bersih) selama %s." % (money(-R["net_profit"]), Pi(margin), label[1])))
    elif margin < t_margin:
        check("margin", "warn", (
            "Net profit is %s a month, %s of net sales: under the %s a healthy business keeps." % (money(R["net_profit"]), P(margin), P(t_margin, 0)),
            "Laba bersih %s sebulan, %s dari penjualan bersih: di bawah %s yang wajar untuk usaha sehat." % (
                money(R["net_profit"]), Pi(margin), Pi(t_margin, 0))))
    else:
        check("margin", "ok", ("Net profit is %s a month, %s of net sales." % (money(R["net_profit"]), P(margin)),
                               "Laba bersih %s sebulan, %s dari penjualan bersih." % (money(R["net_profit"]), Pi(margin))))

    # break-even
    if be is None:
        check("breakeven", "bad", ("Direct cost and tax take more than net sales: no volume of sales breaks even at these prices.",
                                   "Biaya bahan dan pajak lebih besar dari penjualan bersih: berapa pun yang terjual, harga ini tidak akan balik modal."))
        fix("breakeven", R["net_profit"] * -1, ("Prices are below what each sale costs to make. Reprice before anything else.",
                                                "Harga jual di bawah biaya membuatnya. Perbaiki harga sebelum yang lain."), "checker-competitors")
    else:
        cover = net / be
        days = "{:g}".format(round(R["days_open"], 1))
        txt = ("Net sales %s a month against a break-even of %s (%s a day over %s open days)." % (
                   money(net), money(be), money(out["breakeven_day"]), days),
               "Penjualan bersih %s sebulan, titik impas (BEP) %s (%s sehari, %s hari buka)." % (
                   money(net), money(be), money(out["breakeven_day"]), days.replace(".", ",")))
        if cover < 1:
            check("breakeven", "bad", J(txt, ("Below break-even by %s." % money(be - net), "Kurang %s dari titik impas." % money(be - net))), cover=cover)
            fix("breakeven", (be - net) * ratio, (
                "Close the gap to break-even: %s more net sales a month, or cut fixed costs and labour by %s." % (money(be - net), money((be - net) * ratio)),
                "Tutup selisih ke titik impas: tambah penjualan bersih %s sebulan, atau pangkas biaya tetap dan gaji %s." % (
                    money(be - net), money((be - net) * ratio))), "checker-customers")
        elif cover < 1.1:
            check("breakeven", "warn", J(txt, ("Only %s above it: one slow month turns it into a loss." % P(cover - 1, 0),
                                               "Hanya %s di atasnya: satu bulan sepi bisa jadi rugi." % Pi(cover - 1, 0))), cover=cover)
        else:
            check("breakeven", "ok", J(txt, ("%s above it." % P(cover - 1, 0), "%s di atasnya." % Pi(cover - 1, 0))), cover=cover)

    # trend
    if len(months) >= 4:
        k = min(3, len(months) // 2)
        last, before = months[-k:], months[-2 * k:-k]
        a, b = _avg(last, "net_sales"), _avg(before, "net_sales")
        change = (a - b) / b
        out["trend"] = {"last": [m["month"] for m in last], "before": [m["month"] for m in before], "change": change}
        txt = ("Net sales %s %s: %s a month over %s against %s over %s." % (
                   "fell" if change < 0 else "rose", P(abs(change)), money(a), _span(last), money(b), _span(before)),
               "Penjualan bersih %s %s: %s sebulan pada %s dibanding %s pada %s." % (
                   "turun" if change < 0 else "naik", Pi(abs(change)), money(a), _span(last).replace(" to ", " s.d. "),
                   money(b), _span(before).replace(" to ", " s.d. ")))
        if out["missing_months"]:
            gap = ", ".join(out["missing_months"])
            txt = J(txt, ("No numbers for %s, so these are not all back-to-back months." % gap,
                          "Tidak ada angka untuk %s, jadi bulannya tidak berurutan." % gap))
        if change <= -0.15:
            check("trend", "bad", J(txt, ("Check the calendar (Ramadan, rainy season) before blaming the business.",
                                          "Cek kalender dulu (Ramadan, musim hujan) sebelum menyalahkan usahanya.")), change=change)
        elif change <= -0.05:
            check("trend", "warn", J(txt, ("Check the calendar before reading too much into it.",
                                           "Cek kalender dulu sebelum menarik kesimpulan.")), change=change)
        else:
            check("trend", "ok", txt, change=change)
        if change <= -0.05:
            fix("trend", (b - a) * ratio, ("Win back the %s a month of net sales lost since %s." % (money(b - a), before[-1]["month"]),
                                           "Kembalikan penjualan bersih %s sebulan yang hilang sejak %s." % (money(b - a), before[-1]["month"])),
                "checker-customers")

    # direct cost and labour
    SRC_ID = {"owner": "target pemilik", "default": "standar"}
    TYPE_ID = {"fnb": "makanan dan minuman", "retail": "toko", "online": "online", "service": "jasa", "other": "lainnya"}
    for cid, key, target, name, how, skill in (
            ("direct_cost", "direct_cost", t_dc, ("Direct cost (food cost, COGS, materials)", "Biaya bahan (food cost, HPP)"),
             ("Check supplier prices, portions and waste", "Cek harga pemasok, porsi dan bahan terbuang"), "checker-health"),
            ("labour", "labour", t_lab, ("Labour", "Biaya karyawan"),
             ("Match the roster to the busy hours", "Sesuaikan jadwal shift dengan jam ramai"), "checker-health")):
        if target is None:
            continue
        share = R[key] / net
        src = out["targets"]["source"][key + "_pct"]
        src_id = SRC_ID.get(src) or "standar usaha %s" % TYPE_ID.get(btype, btype)
        txt = ("%s is %s of net sales against a target of %s (%s)." % (name[0], P(share), P(target, 0), src),
               "%s %s dari penjualan bersih, targetnya %s (%s)." % (name[1], Pi(share), Pi(target, 0), src_id))
        check(cid, "bad" if share > target + BAD_POINTS else ("warn" if share > target else "ok"), txt, share=share)
        if share > target:
            fix(cid, (share - target) * net, (
                "%s: bring %s from %s back to %s." % (how[0], name[0].split(" (")[0].lower(), P(share), P(target, 0)),
                "%s: turunkan %s dari %s ke %s." % (how[1], name[1].split(" (")[0].lower(), Pi(share), Pi(target, 0))), skill)

    # what the owner takes
    if R["owner_drawings"] > 0:
        spare = R["net_profit"] - R["debt_payment"]
        txt = ("The owner takes %s a month; the business earns %s after debt payments." % (money(R["owner_drawings"]), money(spare)),
               "Pemilik mengambil %s sebulan; usaha menghasilkan %s setelah cicilan utang." % (money(R["owner_drawings"]), money(spare)))
        if spare <= 0:
            check("owner", "bad", J(txt, ("Every Rupiah taken comes out of the business's cash.",
                                          "Setiap Rupiah yang diambil mengurangi kas usaha.")))
        elif R["owner_drawings"] > spare:
            more = money(R["owner_drawings"] - spare)
            check("owner", "warn", J(txt, ("The owner takes %s a month more than it earns." % more,
                                           "Pemilik mengambil %s sebulan lebih banyak dari hasilnya." % more)))
        else:
            check("owner", "ok", txt)
        if R["owner_drawings"] > max(spare, 0):
            fix("owner", R["owner_drawings"] - max(spare, 0), (
                "Pay the owner a fixed salary the business can afford; stop taking cash from the till.",
                "Gaji pemilik tetap yang sanggup dibayar usaha; berhenti mengambil uang dari laci kas."), "checker-health")

    # the owner's own work: a profit that exists only because the owner is not paid is a wage, not a profit
    fair = actuals.get("owner_fair_salary")
    if fair is not None:
        fair = _num(fair, "owner_fair_salary")
        out["profit_after_owner_pay"] = R["net_profit"] - fair
        left = money(abs(R["net_profit"] - fair))
        txt = ("Paying someone to do the owner's work would cost about %s a month; after that the business %s %s." % (
                   money(fair), "makes" if R["net_profit"] >= fair else "loses", left),
               "Menggaji orang untuk mengerjakan pekerjaan pemilik butuh sekitar %s sebulan; setelah itu usaha %s %s." % (
                   money(fair), "masih untung" if R["net_profit"] >= fair else "rugi", left))
        if R["net_profit"] < fair:
            check("owner_pay", "warn", J(txt, ("It runs on the owner's unpaid work: the owner would earn more as an employee.",
                                               "Usaha ini jalan karena pemilik tidak digaji: jadi karyawan pun penghasilannya lebih besar.")))
        else:
            check("owner_pay", "ok", txt)

    # debt
    if R["debt_payment"] > 0:
        txt = ("Debt payments are %s a month against a net profit of %s." % (money(R["debt_payment"]), money(R["net_profit"])),
               "Cicilan utang %s sebulan, laba bersih %s." % (money(R["debt_payment"]), money(R["net_profit"])))
        if R["debt_payment"] > R["net_profit"]:
            check("debt", "bad", J(txt, ("The profit does not cover them.", "Labanya tidak cukup untuk membayarnya.")))
        elif R["debt_payment"] > 0.5 * R["net_profit"]:
            check("debt", "warn", J(txt, ("They take more than half of it.", "Cicilan memakan lebih dari separuh laba.")))
        else:
            check("debt", "ok", txt)

    # cash
    cash = actuals.get("cash") or {}
    if cash.get("balance") is not None:
        bal = _num(cash["balance"], "cash.balance", allow_negative=True)
        weekly = (R["operating_out"] + R["debt_payment"]) / WEEKS_PER_MONTH
        weeks = bal / weekly if weekly > 0 else None
        out["cash"] = {"balance": bal, "as_of": cash.get("as_of"), "weekly_out": weekly, "weeks_covered": weeks}
        asof = " (%s)" % cash["as_of"] if cash.get("as_of") else ""
        w = "{:.1f}".format(weeks or 0)
        txt = ("Cash on hand %s%s covers %s weeks of running costs (%s a week)." % (money(bal), asof, w, money(weekly)),
               "Kas %s%s cukup untuk %s minggu biaya operasional (%s seminggu)." % (money(bal), asof, w.replace(".", ","), money(weekly)))
        status = "bad" if weeks is not None and weeks < 1 else ("warn" if weeks is not None and weeks < 2 else "ok")
        if R["kept"] < 0:
            months_left = bal / -R["kept"] if bal > 0 else 0
            out["cash"]["months_left"] = months_left
            ml = "{:.1f}".format(months_left)
            txt = J(txt, ("Cash shrinks by %s a month after the owner and the debt: at this rate it lasts %s months." % (money(-R["kept"]), ml),
                          "Kas berkurang %s sebulan setelah diambil pemilik dan bayar utang: dengan laju ini habis dalam %s bulan." % (
                              money(-R["kept"]), ml.replace(".", ","))))
            status = "bad" if months_left < 3 else ("warn" if status == "ok" else status)
        check("cash", status, txt)

    # platforms
    plat = sum(c["gross"] for c in out["channels"] if c["platform"])
    if plat > 0:
        share = plat / R["gross"] if R["gross"] else 0
        comm = sum(c["commission"] for c in out["channels"] if c["platform"])
        txt = ("%s of gross sales go through apps and marketplaces, which keep %s a month (%s of what goes through them)." % (
                   P(share, 0), money(comm), P(comm / plat)),
               "%s penjualan kotor lewat aplikasi dan marketplace, yang memotong %s sebulan (%s dari penjualan di sana)." % (
                   Pi(share, 0), money(comm), Pi(comm / plat)))
        if share > PLATFORM_WARN_SHARE:
            check("platforms", "warn", J(txt, ("One fee change or algorithm change hits most of the business.",
                                               "Satu kenaikan komisi atau perubahan algoritma memukul sebagian besar usaha.")), share=share)
        else:
            check("platforms", "ok", txt, share=share)
        fix("platforms", 0.2 * comm, (
            "Scenario: move 1 in 5 app orders to direct orders (WhatsApp, the counter, pick-up). Saves the commission on them, minus whatever the switch costs.",
            "Skenario: pindahkan 1 dari 5 pesanan aplikasi ke pesanan langsung (WhatsApp, kasir, ambil sendiri). Hemat komisinya, dikurangi biaya peralihannya."),
            "checker-channels")

    # customers
    if customers and customers.get("rating_avg") is not None:
        r = round(_num(customers["rating_avg"], "customers.rating_avg"), 1)  # judged as the owner sees it, to one decimal
        n = int(customers.get("reviews", 0))
        per = ", ".join("%s %.1f" % (s["source"], s["rating"]) for s in customers.get("listings", []))
        nn = "{:,}".format(n).replace(",", ".")
        txt = ("Listing rating %.1f across %s reviews%s." % (r, nn, " (%s)" % per if per else ""),
               "Rating %s dari %s ulasan%s." % (("%.1f" % r).replace(".", ","), nn, " (%s)" % per.replace(".", ",") if per else ""))
        if n < 10:
            check("customers", "warn", J(txt, ("Too few to judge; ask happy customers to review.",
                                               "Terlalu sedikit untuk dinilai; minta pelanggan yang puas memberi ulasan.")))
        elif r < 3.5:
            check("customers", "bad", J(txt, ("Below 3.5, many buyers scroll past.", "Di bawah 3,5 banyak pembeli melewatkannya.")))
        elif r < 4.2:
            check("customers", "warn", J(txt, ("Under 4.2: the top complaint is costing sales.",
                                               "Di bawah 4,2: keluhan utama sedang menggerus penjualan.")))
        else:
            check("customers", "ok", txt)

    # compliance
    if compliance and compliance.get("items"):
        items = compliance["items"]
        for i, it in enumerate(items):
            if it.get("status") not in COMPLIANCE_STATUS:
                raise ActualsError("compliance item %d (%s): status must be one of %s, not %r" % (
                    i, it.get("item", "?"), ", ".join(COMPLIANCE_STATUS), it.get("status")))
            if it.get("severity") not in COMPLIANCE_SEVERITY:
                raise ActualsError("compliance item %d (%s): severity must be one of %s, not %r" % (
                    i, it.get("item", "?"), ", ".join(COMPLIANCE_SEVERITY), it.get("severity")))
        gaps = [i for i in items if i.get("status") in ("missing", "expired")]
        unknown = [i for i in items if i.get("status") == "unknown" and i.get("severity") in ("blocks_sales", "penalty")]
        blocking = [i for i in gaps if i.get("severity") == "blocks_sales"]
        penalty = [i for i in gaps if i.get("severity") == "penalty"]
        names = lambda xs: ", ".join(i.get("item", "?") for i in xs)
        if blocking:
            check("compliance", "bad", ("Missing what selling needs: %s." % names(blocking),
                                        "Belum ada yang wajib untuk berjualan: %s." % names(blocking)))
        elif penalty or unknown:
            en, idn = [], []
            if penalty:
                en.append("missing, with a fine or sanction: %s" % names(penalty))
                idn.append("belum ada, bisa kena denda atau sanksi: %s" % names(penalty))
            if unknown:
                en.append("not yet checked: %s" % names(unknown))
                idn.append("belum dicek: %s" % names(unknown))
            check("compliance", "warn", ("Permits and tax: %s." % "; ".join(en), "Izin dan pajak: %s." % "; ".join(idn)))
        else:
            advised = [i for i in gaps if i.get("severity") not in ("blocks_sales", "penalty")]
            check("compliance", "ok", (
                "%d permit, certificate and tax items checked: nothing that blocks sales or carries a fine is missing.%s" % (
                    len(items), " Advised: %s." % names(advised) if advised else ""),
                "%d item izin, sertifikat dan pajak sudah dicek: tidak ada yang menghambat penjualan atau berisiko denda.%s" % (
                    len(items), " Disarankan: %s." % names(advised) if advised else "")))

    # Reviews alone never make a business critical: they show as failed, but cap at Waspada.
    critical = [c for c in checks if c["status"] == "bad" and c["id"] not in WARN_ONLY]
    out["verdict"] = "Kritis" if critical else ("Waspada" if any(c["status"] != "ok" for c in checks) else "Sehat")
    fixes.sort(key=lambda f: -f["rupiah_per_month"])
    return out


def channel_table(months):
    names = []
    for m in months:
        for k in m["channels"]:
            if k not in names:
                names.append(k)
    n = float(len(months))
    total = sum(m["gross"] for m in months) / n
    rows = []
    for k in names:
        g = sum(m["channels"].get(k, {}).get("gross", 0) for m in months) / n
        c = sum(m["channels"].get(k, {}).get("commission", 0) for m in months) / n
        orders = [m["channels"][k]["orders"] for m in months if k in m["channels"]]
        flags = [m["channels"][k]["platform"] for m in months if k in m["channels"] and "platform" in m["channels"][k]]
        o = sum(orders) / n if orders and None not in orders else None
        rows.append({"channel": k, "gross": g, "commission": c, "share": g / total if total else 0,
                     "commission_rate": c / g if g else 0, "kept_per_100k": (g - c) / g * 100000 if g else 0,
                     "orders": o, "avg_order": g / o if o else None,
                     "platform": flags[-1] if flags else (g > 0 and c / g > PLATFORM_MIN_RATE)})
    rows.sort(key=lambda r: -r["gross"])
    return rows


# ---------------------------------------------------------------- output

def channels_md(rows):
    L = ["| channel | gross a month | share | commission | kept from every Rp100.000 | orders | average order |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        L.append("| %s | %s | %s | %s (%s) | %s | %s | %s |" % (
            r["channel"], money(r["gross"]), pct(r["share"], 0), money(r["commission"]), pct(r["commission_rate"]),
            money(r["kept_per_100k"]), "{:,.0f}".format(r["orders"]).replace(",", ".") if r["orders"] else "?",
            money(r["avg_order"]) if r["avg_order"] else "?"))
    return "\n".join(L)


def health_md(h, full=True):
    """full=False leaves out the title, the verdict and the checks (the report shows them at the top)."""
    L = ["# %s · Health check" % h["business"], ""]
    L.append("**Verdict: %s**%s" % (h["verdict"], " (includes estimates)" if h["estimates"] and h["verdict"] != "Incomplete" else ""))
    L.append("")
    if h["verdict"] == "Incomplete":
        L += ["No months of numbers yet. Run /checker-intake first.", ""]
        return "\n".join(L) + "\n"
    L.append("From %d month%s of real numbers (%s to %s); the checks use %s." % (
        len(h["months"]), "s" if len(h["months"]) > 1 else "", h["months"][0]["month"], h["months"][-1]["month"],
        "the average of " + ", ".join(h["recent_months"]) if len(h["recent_months"]) > 1 else h["recent_months"][0]))
    L.append("")
    for c in h["checks"]:
        L.append("- %s %s" % (STATUS_MARK[c["status"]], c["text"]))
    L.append("")
    if not full:
        L = L[L.index("") + 1:]
        L = [l for l in L if not l.startswith("**Verdict") and not l.startswith("- ")]
    R = h["recent"]
    net = R["net_sales"]
    L += ["## A month, in Rupiah", "",
          "| | a month | of net sales |", "| --- | ---: | ---: |",
          "| Gross sales | %s | |" % money(R["gross"]),
          "| Discounts | %s | |" % money(R["discounts"]),
          "| Apps' and marketplaces' commission and fees | %s | |" % money(R["commission"]),
          "| **Net sales** | **%s** | 100%% |" % money(net)]
    for k, name in (("direct_cost", "Direct cost"), ("labour", "Labour"), ("fixed_costs", "Fixed costs"),
                    ("pph_final", "PPh Final"), ("other_costs", "Other costs")):
        if R[k] or k in ("direct_cost", "labour", "fixed_costs"):
            L.append("| %s | %s | %s |" % (name, money(R[k]), pct(R[k] / net)))
    L.append("| **Net profit** | **%s** | **%s** |" % (money(R["net_profit"]), pct(R["net_profit"] / net)))
    if R["owner_drawings"]:
        L.append("| Taken by the owner (prive) | %s | |" % money(R["owner_drawings"]))
    if R["debt_payment"]:
        L.append("| Debt payments | %s | |" % money(R["debt_payment"]))
    L.append("| **Kept by the business** | **%s** | |" % money(R["kept"]))
    L.append("")
    per = 100000.0 / net
    L += ["In plain words: of every Rp100.000 of net sales, %s goes on direct cost, %s on wages, %s on rent and bills, %s on tax. %s." % (
        money(R["direct_cost"] * per), money(R["labour"] * per), money((R["fixed_costs"] + R["other_costs"]) * per),
        money(R["pph_final"] * per),
        "%s is profit" % money(R["net_profit"] * per) if R["net_profit"] >= 0 else "The business loses %s" % money(-R["net_profit"] * per)), ""]
    L += ["## Month by month", "", "| month | net sales | direct cost | labour | net profit | kept |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for m in h["months"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (m["month"], money(m["net_sales"]), pct(m["direct_cost"] / m["net_sales"]),
                                                     pct(m["labour"] / m["net_sales"]), money(m["net_profit"]), money(m["kept"])))
    if h["missing_months"]:
        L += ["", "_No numbers for %s._" % ", ".join(h["missing_months"])]
    L += ["", "## Channels", "", channels_md(h["channels"]), ""]
    if h["fixes"]:
        L += ["## Fixes, biggest first", ""]
        for i, f in enumerate(h["fixes"], 1):
            L.append("%d. **%s a month**: %s Next: /%s" % (i, money(f["rupiah_per_month"]), f["text"], f["skill"]))
        L += ["", "_Fixes overlap: do not add them up. The Rupiah is the most each one is worth alone._", ""]
    if h["estimates"]:
        L += ["## Estimates in these numbers", ""] + ["- %s" % e for e in h["estimates"]] + [""]
    t = h["targets"]
    L.append("_Targets: direct cost %s, labour %s, net margin %s (%s). Change them in checker/actuals.json under targets._" % (
        pct(t["direct_cost_pct"], 0) if t["direct_cost_pct"] is not None else "not set",
        pct(t["labour_pct"], 0) if t["labour_pct"] is not None else "not set", pct(t["net_margin_pct"], 0),
        "; ".join("%s: %s" % (k.replace("_pct", "").replace("_", " "), v) for k, v in t["source"].items())))
    return "\n".join(L) + "\n"


def to_json(h):
    keep = {k: v for k, v in h.items() if k != "months"}
    keep["months"] = [{k: v for k, v in m.items() if k != "channels"} for m in h["months"]]
    return json.dumps(keep, indent=2, ensure_ascii=False)


def run(actuals_path, out_dir=None):
    d = out_dir or os.path.dirname(os.path.abspath(actuals_path))
    h = analyse(load(actuals_path), _read_optional(os.path.join(d, "customers.json")),
                _read_optional(os.path.join(d, "compliance.json")))
    return h, d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("actuals", nargs="?", default="checker/actuals.json")
    ap.add_argument("--out-dir", help="default: the folder that holds the actuals file")
    ap.add_argument("--check", action="store_true", help="print the verdict and the checks only")
    ap.add_argument("--channels", action="store_true", help="print the channel table only")
    a = ap.parse_args(argv)
    try:
        h, d = run(a.actuals, a.out_dir)
    except FileNotFoundError:
        print("error: %s not found. Run /checker-intake first." % a.actuals, file=sys.stderr)
        return 4
    except ActualsError as e:
        print("error: %s" % e, file=sys.stderr)
        return 4
    if a.channels:
        print(channels_md(h["channels"]) if h["months"] else "No months yet.")
        return 0
    if a.check:
        print("Verdict: %s" % h["verdict"])
        for c in h["checks"]:
            print("  %s %s" % (STATUS_MARK[c["status"]], c["text"]))
        return {"Sehat": 0, "Waspada": 1, "Kritis": 2}.get(h["verdict"], 3)
    with open(os.path.join(d, "health.md"), "w", encoding="utf-8") as fh:
        fh.write(health_md(h))
    with open(os.path.join(d, "health.json"), "w", encoding="utf-8") as fh:
        fh.write(to_json(h) + "\n")
    print("Verdict: %s. Wrote %s and health.json" % (h["verdict"], os.path.join(d, "health.md")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
