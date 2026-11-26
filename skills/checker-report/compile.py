#!/usr/bin/env python3
"""Compiles the business check-up for founder-id-checker. Standard library only, no network.

Reads everything the checker skills wrote into checker/ and assembles one
document, checker/report.md, with the verdict at the top. The verdict and the
ranked fixes come from health.py (checker-health), never from a person:

    Sehat       healthy: every check that has data passes
    Waspada     watch out: at least one warning, nothing critical
    Kritis      critical: at least one check fails badly
    Incomplete  there are no real numbers yet (run checker-intake first)

    python3 compile.py                      # reads ./checker, writes ./checker/report.md
    python3 compile.py --dir path/to/checker
    python3 compile.py --check              # print the verdict; exit 0 Sehat, 1 Waspada, 2 Kritis, 3 Incomplete
"""

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [  # (file in checker/, heading, which skill writes it)
    ("summary.md", "Summary", "checker-report"),
    ("plan-90.md", "The next 90 days", "checker-report"),
    ("board.md", "What the board said", "checker-board"),
    ("health.md", "The numbers", "checker-health"),
    ("channels.md", "Channels", "checker-channels"),
    ("customers.md", "What customers say", "checker-customers"),
    ("competitors.md", "The competition now", "checker-competitors"),
    ("compliance.md", "Permits, certificates and tax", "checker-compliance"),
]
VERDICT_LINE = {
    "Sehat": "Healthy. Keep the routine and grow from here.",
    "Waspada": "Watch out. The business works, but something is slipping.",
    "Kritis": "Critical. Fix these before spending on anything else.",
    "Incomplete": "Not enough real numbers yet.",
}
MARK = {"ok": "✓", "warn": "!", "bad": "✗"}


def _health():
    path = os.path.join(HERE, "..", "checker-health", "health.py")
    spec = importlib.util.spec_from_file_location("checker_health", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return None


def _json(path):
    raw = _read(path)
    return json.loads(raw) if raw else None


def _strip_h1(text):
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(("#" + l) if l.startswith("#") else l for l in lines).strip()


def assess(d):
    """Run the health check on <d>/actuals.json with whatever customers and compliance data exist."""
    H = _health()
    actuals = _json(os.path.join(d, "actuals.json"))
    if actuals is None:
        return H, {"business": None, "verdict": "Incomplete", "checks": [], "fixes": [], "months": [], "estimates": []}
    return H, H.analyse(actuals, _json(os.path.join(d, "customers.json")), _json(os.path.join(d, "compliance.json")))


def business_name(d, h):
    text = _read(os.path.join(d, "business.md"))
    if text and text.splitlines()[0].startswith("# "):
        return text.splitlines()[0][2:].strip()
    return h.get("business") or "Your business"


def compile_report(d):
    H, h = assess(d)
    name = business_name(d, h)
    v = h["verdict"]
    L = ["# %s · Business check-up" % name, "", "**Verdict: %s.** %s" % (v, VERDICT_LINE[v]), ""]
    for c in h["checks"]:
        L.append("- %s %s" % (MARK[c["status"]], c["text"]))
    if v == "Incomplete":
        L.append("- No real numbers yet. Run /checker-intake, then compile again.")
    L.append("")
    if h["months"]:
        M = H.money
        R = h["recent"]
        L += ["| key number | a month |", "| --- | ---: |",
              "| Net sales | %s |" % M(R["net_sales"]),
              "| Net profit | %s (%s) |" % (M(R["net_profit"]), H.pct(R["net_profit"] / R["net_sales"])),
              "| Break-even | %s |" % (M(h["breakeven_month"]) if h["breakeven_month"] else "never at these prices"),
              "| Kept after the owner and the debt | %s |" % M(R["kept"])]
        if h.get("cash"):
            L.append("| Cash on hand | %s (%.1f weeks of running costs) |" % (M(h["cash"]["balance"]), h["cash"]["weeks_covered"] or 0))
        L += ["", "_From %d month%s of real numbers, %s to %s%s._" % (
            len(h["months"]), "s" if len(h["months"]) > 1 else "", h["months"][0]["month"], h["months"][-1]["month"],
            "; %d estimate%s listed under The numbers" % (len(h["estimates"]), "s" if len(h["estimates"]) > 1 else "") if h["estimates"] else ""), ""]
    if h["fixes"]:
        L += ["## The top 3 fixes", ""]
        for i, f in enumerate(h["fixes"][:3], 1):
            L.append("%d. **Up to %s a month.** %s Next: /%s" % (i, H.money(f["rupiah_per_month"]), f["text"], f["skill"]))
        L += ["", "_Ranked by Rupiah a month, each on its own. They overlap, so do not add them up._", ""]
    biz = _read(os.path.join(d, "business.md"))
    if biz:
        L += ["## The business", "", _strip_h1(biz), ""]
    missing = []
    for fname, heading, skill in SECTIONS:
        text = _read(os.path.join(d, fname))
        if fname == "health.md" and h["months"]:
            text = H.health_md(h, full=False)  # always fresh, so the numbers match the verdict above
        if text:
            L += ["## %s" % heading, "", _strip_h1(text), ""]
        else:
            missing.append((heading, skill))
    if missing:
        L += ["## Not done yet", ""] + ["- %s: run /%s" % (hd, sk) for hd, sk in missing] + [""]
    L.append("_Every number comes from the owner's own records, and estimates are marked as estimates. Reviews and"
             " survey answers are from real customers, with links. Not financial, legal or tax advice: an accountant"
             " or konsultan pajak confirms the numbers and the tax._")
    return v, "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="checker")
    ap.add_argument("--check", action="store_true", help="print the verdict only")
    ap.add_argument("--out", help="default: <dir>/report.md")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.dir):
        print("error: no %s/ folder here. Run /checker-intake first." % a.dir, file=sys.stderr)
        return 4
    try:
        H, h = assess(a.dir)
        v, text = compile_report(a.dir)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 4
    if a.check:
        print("Verdict: %s" % v)
        for c in h["checks"]:
            print("  %s %s" % (MARK[c["status"]], c["text"]))
        return {"Sehat": 0, "Waspada": 1, "Kritis": 2}.get(v, 3)
    out = a.out or os.path.join(a.dir, "report.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Verdict: %s. Wrote %s" % (v, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
