#!/usr/bin/env python3
"""Builds and tallies a simulated customer panel, for founder-id-checker. Standard library only, no network.

Everything this tool touches is SIMULATED and labelled so. It exists to try a
planned change (a new price, a menu item, a bundle, a message to lapsed
customers) on a panel before the owner spends money testing it for real. It
never feeds the health check, the board or the report.

The panel is not invented from a target market: it is drawn from the
business's own evidence.

  panel   builds the persona slots from checker/customers.json (the real
          complaint themes and the real reasons lapsed customers gave) and
          checker/actuals.json (the real channel mix and average ticket):

    python3 simulate.py panel --customers checker/customers.json --actuals checker/actuals.json \
                              --n 30 --out checker/simulate/<run>

          Writes <out>/panel.json. --n is any whole number from 1 (default 30).

  tally   counts the answers the persona sub-agents wrote:

    python3 simulate.py tally --panel checker/simulate/<run>/panel.json \
                              --answers checker/simulate/<run>/answers-*.csv --out checker/simulate/<run>

          answers CSV: persona,variant,decision,reason,would_pay
          (decision is ya / mungkin / tidak; a mungkin counts as a no.)
          Writes <out>/simulate.json and <out>/simulate-data.md.
"""

import argparse
import csv
import json
import os
import random
import re
import sys
from collections import OrderedDict

DEFAULT_N = 30
THIN_PANEL = 20      # under this many personas per variant, say the panel is thin
THIN_GROUP = 5       # a segment with fewer personas than this is marked thin
CLOSE_CALL = 0.10    # variants closer than 10 points are too close to call
ANSWER_COLS = ("persona", "variant", "decision", "reason", "would_pay")
YES = {"ya", "yes", "y", "iya", "mau", "beli"}
MAYBE = {"mungkin", "maybe", "nanti", "nanti deh", "lihat dulu", "boleh", "boleh juga"}
NO = {"tidak", "no", "nggak", "ga", "gak", "enggak", "tdk", "skip"}
LABEL = "SIMULATED: a what-if panel, not real customers. Confirm with a real test before acting."


class DataError(ValueError):
    pass


def _json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def quotas(weights, n):
    """Split n slots across keys in proportion to their weights (largest remainder)."""
    weights = [(k, float(w)) for k, w in weights if w > 0]
    if not weights or n <= 0:
        return []
    total = sum(w for _, w in weights)
    raw = [(k, n * w / total) for k, w in weights]
    counts = OrderedDict((k, int(x)) for k, x in raw)
    left = n - sum(counts.values())
    for k, _ in sorted(raw, key=lambda kx: -(kx[1] - int(kx[1])))[:left]:
        counts[k] += 1
    out = []
    for k, c in counts.items():
        out += [k] * c
    return out


def channel_mix(actuals, months=3):
    """Gross sales and average ticket per channel over the last few months."""
    agg = OrderedDict()
    for m in (actuals.get("months") or [])[-months:]:
        for name, ch in (m.get("channels") or {}).items():
            a = agg.setdefault(name, {"gross": 0, "orders": 0})
            a["gross"] += ch.get("gross") or 0
            a["orders"] += ch.get("orders") or 0
    return OrderedDict((k, {"share": v["gross"], "avg_ticket": int(round(v["gross"] / v["orders"])) if v["orders"] else None})
                       for k, v in agg.items() if v["gross"] > 0)


def build_panel(customers, actuals=None, n=DEFAULT_N, lapsed_share=0.5, seed=1):
    if n < 1:
        raise DataError("the panel needs at least 1 persona, not %d" % n)
    rv = customers.get("review_tally")
    sv = customers.get("survey")
    if not rv and not sv:
        raise DataError("customers.json has no reviews and no survey: run /checker-customers first, "
                        "the panel is drawn from what real customers said")
    notes = []
    if not sv:
        lapsed_share = 0.0
        notes.append("no lapsed-customer survey: every persona is a current customer")
    if not rv:
        lapsed_share = 1.0
        notes.append("no reviews read: every persona is a lapsed customer")
    n_lapsed = int(round(n * lapsed_share))
    n_current = n - n_lapsed

    themes = [(t["theme"], t["count"]) for t in rv["complaints"]] if rv else []
    if rv and rv.get("praise"):
        themes.append(("pujian", rv["praise"]["count"]))
    quotes = {}
    if rv:
        for t in rv["complaints"] + ([rv["praise"]] if rv.get("praise") else []):
            quotes[t["theme"]] = [{"quote": q["quote"], "source": q.get("source") or "", "url": q["url"]}
                                  for q in t.get("quotes", [])]
    reasons = [(r["reason"], r["count"]) for r in sv["reasons"]] if sv else []

    current = quotas(themes, n_current) or ["-"] * n_current
    lapsed = quotas(reasons, n_lapsed) or ["-"] * n_lapsed
    status = [("current", c) for c in current] + [("lapsed", r) for r in lapsed]

    mix = channel_mix(actuals) if actuals else OrderedDict()
    if mix:
        channels = quotas([(k, v["share"]) for k, v in mix.items()], n)
    else:
        channels = ["?"] * n
        notes.append("no actuals.json: ask the owner which channel each persona orders on")

    rng = random.Random(seed)
    rng.shuffle(channels)
    width = max(2, len(str(n)))
    used = {}
    personas = []
    for i, ((st, concern), ch) in enumerate(zip(status, channels), 1):
        qs = quotes.get(concern) or []
        # prefer a quote read on this persona's own channel (a GoFood review for a GoFood buyer)
        own = [x for x in qs if x["source"] and x["source"].lower().split("/")[0] in ch.lower()]
        pool = own or qs
        q = pool[used.get(concern, 0) % len(pool)] if pool else None
        used[concern] = used.get(concern, 0) + 1
        personas.append({"id": "P%0*d" % (width, i), "status": st, "concern": concern, "channel": ch,
                         "avg_ticket": mix[ch]["avg_ticket"] if ch in mix else None,
                         "grounded_in": q})
    return {"simulated": True, "label": LABEL, "n": n, "seed": seed, "lapsed": n_lapsed, "current": n_current,
            "channels": {k: {"avg_ticket": v["avg_ticket"]} for k, v in mix.items()},
            "notes": notes, "personas": personas}


def _rows(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip().lower() for h in (reader.fieldnames or [])]
        missing = [c for c in ANSWER_COLS if c not in header]
        if missing:
            raise DataError("%s is missing the column(s): %s" % (path, ", ".join(missing)))
        out = []
        for i, row in enumerate(reader, 2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            if any(row.values()):
                row["_where"] = "%s line %d" % (path, i)
                out.append(row)
        return out


def decision(v):
    v = (v or "").strip().lower()
    if v in YES:
        return "ya"
    if v in MAYBE:
        return "mungkin"
    if v in NO:
        return "tidak"
    return None


def rupiah(text, where):
    t = (text or "").strip()
    if not t:
        return None
    digits = re.sub(r"(?i)^rp\.?\s*|[.\s]", "", t).split(",")[0]
    if not digits.isdigit():
        raise DataError("%s: would_pay must be a Rupiah amount like 25000 or Rp25.000, not %r" % (where, text))
    return int(digits)


def _group(items, key):
    g = OrderedDict()
    for it in items:
        b = g.setdefault(key(it), {"n": 0, "ya": 0})
        b["n"] += 1
        b["ya"] += it["decision"] == "ya"
    return [{"group": k, "n": v["n"], "ya": v["ya"], "rate": round(v["ya"] / float(v["n"]), 3), "thin": v["n"] < THIN_GROUP}
            for k, v in sorted(g.items(), key=lambda kv: -kv[1]["n"])]


def tally(panel, rows):
    people = {p["id"]: p for p in panel["personas"]}
    seen = set()
    variants = OrderedDict()
    for r in rows:
        w = r["_where"]
        pid, var = r["persona"].upper(), r["variant"].upper()
        if pid not in people:
            raise DataError("%s: persona %r is not in the panel" % (w, r["persona"]))
        if not var:
            raise DataError("%s: every answer needs its variant (A, B, ...)" % w)
        if (pid, var) in seen:
            raise DataError("%s: %s already answered variant %s" % (w, pid, var))
        seen.add((pid, var))
        d = decision(r["decision"])
        if d is None:
            raise DataError("%s: decision must be ya, mungkin or tidak, not %r" % (w, r["decision"]))
        if d != "ya" and not r["reason"]:
            raise DataError("%s: every mungkin or tidak needs its reason code" % w)
        variants.setdefault(var, []).append(dict(people[pid], decision=d, reason=(r["reason"] or "").lower(),
                                                 would_pay=rupiah(r["would_pay"], w)))
    if not variants:
        raise DataError("no answers")
    out = OrderedDict()
    for var, items in variants.items():
        missing = sorted(set(people) - {i["id"] for i in items})
        if missing:
            raise DataError("variant %s has no answer from %d persona(s): %s" % (var, len(missing), ", ".join(missing[:10])))
        n = len(items)
        c = {k: sum(1 for i in items if i["decision"] == k) for k in ("ya", "mungkin", "tidak")}
        why = OrderedDict()
        for i in items:
            if i["decision"] != "ya":
                why[i["reason"]] = why.get(i["reason"], 0) + 1
        pays = sorted(i["would_pay"] for i in items if i["decision"] == "ya" and i["would_pay"])
        out[var] = {"n": n, "answers": c, "rate": round(c["ya"] / float(n), 3), "thin": n < THIN_PANEL,
                    "by_status": _group(items, lambda i: i["status"]),
                    "by_channel": _group(items, lambda i: i["channel"]),
                    "by_concern": _group(items, lambda i: i["concern"]),
                    "why_not": [{"reason": k, "count": v} for k, v in sorted(why.items(), key=lambda kv: -kv[1])],
                    "median_would_pay": pays[len(pays) // 2] if pays else None}
    ranked = sorted(out, key=lambda v: -out[v]["rate"])
    result = {"simulated": True, "label": LABEL, "n": panel["n"], "variants": out, "ranked": ranked}
    if len(ranked) > 1:
        gap = round(out[ranked[0]]["rate"] - out[ranked[1]]["rate"], 3)
        result["lead"] = {"best": ranked[0], "over": ranked[1], "points": gap,
                          "too_close": gap < CLOSE_CALL or out[ranked[0]]["thin"]}
    return result


def _pct(x):
    return "%.0f%%" % (x * 100)


def data_md(res):
    L = ["# Simulated panel: the data", "", "**%s**" % res["label"], ""]
    if "lead" in res:
        ld = res["lead"]
        L += ["Best: variant %s, %s points above %s%s." % (ld["best"], round(ld["points"] * 100), ld["over"],
                                                          " (too close to call)" if ld["too_close"] else ""), ""]
    for var, v in res["variants"].items():
        a = v["answers"]
        L += ["## Variant %s" % var, "",
              "%d personas: %d ya, %d mungkin, %d tidak. Would buy: %s (a mungkin is a no)%s." % (
                  v["n"], a["ya"], a["mungkin"], a["tidak"], _pct(v["rate"]), "; the panel is thin" if v["thin"] else "")]
        if v["median_would_pay"]:
            L.append("Median price the yes personas named: Rp%s." % "{:,}".format(v["median_would_pay"]).replace(",", "."))
        for title, key in (("status", "by_status"), ("channel", "by_channel"), ("concern they came in with", "by_concern")):
            L += ["", "| %s | personas | ya | would buy | |" % title, "| --- | ---: | ---: | ---: | --- |"]
            L += ["| %s | %d | %d | %s | %s |" % (g["group"], g["n"], g["ya"], _pct(g["rate"]), "thin" if g["thin"] else "")
                  for g in v[key]]
        if v["why_not"]:
            L += ["", "Why not:"] + ["- %s (%d)" % (w["reason"], w["count"]) for w in v["why_not"]]
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("panel")
    p.add_argument("--customers", default="checker/customers.json")
    p.add_argument("--actuals")
    p.add_argument("--n", type=int, default=DEFAULT_N)
    p.add_argument("--lapsed-share", type=float, default=0.5)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", required=True)
    t = sub.add_parser("tally")
    t.add_argument("--panel", required=True)
    t.add_argument("--answers", nargs="+", required=True)
    t.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        if a.cmd == "panel":
            if not 0 <= a.lapsed_share <= 1:
                raise DataError("--lapsed-share must be from 0 to 1")
            actuals = _json(a.actuals) if a.actuals else None
            res = build_panel(_json(a.customers), actuals, a.n, a.lapsed_share, a.seed)
            os.makedirs(a.out, exist_ok=True)
            with open(os.path.join(a.out, "panel.json"), "w", encoding="utf-8") as fh:
                json.dump(res, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            print("SIMULATED panel: %d personas (%d current, %d lapsed)%s. Wrote %s" % (
                res["n"], res["current"], res["lapsed"], "; " + "; ".join(res["notes"]) if res["notes"] else "",
                os.path.join(a.out, "panel.json")))
            return 0
        panel = _json(a.panel)
        rows = []
        for path in a.answers:
            rows += _rows(path)
        res = tally(panel, rows)
    except FileNotFoundError as e:
        print("error: %s not found" % e.filename, file=sys.stderr)
        return 2
    except (DataError, json.JSONDecodeError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "simulate.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(a.out, "simulate-data.md"), "w", encoding="utf-8") as fh:
        fh.write(data_md(res))
    print("SIMULATED: %s. Wrote simulate.json and simulate-data.md in %s" % (
        ", ".join("%s %s" % (k, _pct(v["rate"])) for k, v in res["variants"].items()), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
