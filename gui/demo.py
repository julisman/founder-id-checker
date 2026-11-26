#!/usr/bin/env python3
"""Builds a demo project to try the dashboard on, from the example files in skills/.

Everything in it is the example business (Bakso Mas Yono, Depok) and is marked
as a demo: example links point at example.com, and the board memos say they are
samples. Standard library only, no network.

    python3 gui/demo.py /tmp/checker-demo          # then: python3 gui/serve.py --dir /tmp/checker-demo
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(HERE, "..", "skills")

BUSINESS = """# Bakso Mas Yono

_Demo business: the example in founder-id-checker. Not a real business._

- What it is: a bakso stall with six tables and delivery. Open since March 2024.
- Type: fnb.
- Where: Margonda, Depok, one outlet.
- Channels: walk-in about 60%, GoFood/GrabFood about 37%, ShopeeFood about 3%. Apps pay out in 1 to 3 days.
- Legal form and NIB: individual with an NIB.
- Team: 4 staff (2 kitchen, 1 cashier, 1 helper). Owner's salary: none, takes cash as needed.
- Records: POS export, GoBiz and ShopeeFood reports, purchase notes, June to November 2026. No stock count.
- The owner's worry: "Ramai terus tapi uangnya tidak pernah cukup."
- The owner's goal: fix.
"""

COMPLIANCE = {"checked": "2026-11-26", "items": [
    {"item": "NIB", "status": "ok", "severity": "blocks_sales", "note": "Demo: KBLI 56102 (warung makan)", "source": "https://oss.go.id"},
    {"item": "PPh Final 0.5% paid monthly", "status": "ok", "severity": "penalty", "note": "Paid on gross turnover through Coretax", "source": "https://pajak.go.id"},
    {"item": "BPJS Ketenagakerjaan for all staff", "status": "unknown", "severity": "penalty", "note": "The owner is not sure the helper is registered", "source": "https://bpjsketenagakerjaan.go.id"},
    {"item": "Halal certificate", "status": "missing", "severity": "advised", "note": "Micro business: required by 17 October 2028; free self-declare route", "source": "https://halal.go.id"},
    {"item": "Trademark search on PDKI", "status": "missing", "severity": "advised", "note": "Not searched yet", "source": "https://pdki-indonesia.dgip.go.id"},
]}

MEMOS = {
    "money": ("6", "FIX", "Profit is real even after paying for the owner's work, but direct cost has climbed six months running and cash covers under two weeks."),
    "customer": ("6", "FIX", "Regulars praise the broth. The lapsed customers name smaller portions and slow app orders."),
    "position": ("7", "GROW", "The broth and the location are hard to copy; the app channel is the weak flank."),
    "local-market": ("6", "FIX", "Build a THR buffer before Lebaran 2027 and confirm BPJS for every worker."),
}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    project = os.path.abspath(argv[0])
    d = os.path.join(project, "checker")
    if os.path.exists(d) and os.listdir(d):
        print("error: %s already has files; pick an empty folder" % d, file=sys.stderr)
        return 2
    os.makedirs(os.path.join(d, "customers"), exist_ok=True)
    os.makedirs(os.path.join(d, "board"), exist_ok=True)
    shutil.copy(os.path.join(SKILLS, "checker-health", "example.json"), os.path.join(d, "actuals.json"))
    for name in ("listings", "reviews", "survey"):
        shutil.copy(os.path.join(SKILLS, "checker-customers", "%s.example.csv" % name), os.path.join(d, "customers", "%s.csv" % name))
    with open(os.path.join(d, "business.md"), "w", encoding="utf-8") as fh:
        fh.write(BUSINESS)
    with open(os.path.join(d, "compliance.json"), "w", encoding="utf-8") as fh:
        json.dump(COMPLIANCE, fh, indent=2)
    for lens, (score, vote, line) in MEMOS.items():
        with open(os.path.join(d, "board", "%s.md" % lens), "w", encoding="utf-8") as fh:
            fh.write("# %s lens\nScore: %s | Vote: %s\n\n_Sample memo for the demo._\n\n## What is working\n\n%s\n" % (
                lens.replace("-", " ").title(), score, vote, line))
    with open(os.path.join(d, "board.md"), "w", encoding="utf-8") as fh:
        fh.write("# The board\n\n_Sample summary for the demo._\n\n**3 fix, 1 grow**, average score 6.25.\n\n"
                 "- Bring direct cost back to 35% before anything new.\n- Build two weeks of cash, then the THR buffer.\n")
    run = lambda *a: subprocess.run([sys.executable] + list(a), check=True, stdout=subprocess.DEVNULL)
    run(os.path.join(SKILLS, "checker-customers", "reviews.py"), "--listings", os.path.join(d, "customers", "listings.csv"),
        "--reviews", os.path.join(d, "customers", "reviews.csv"), "--survey", os.path.join(d, "customers", "survey.csv"), "--out", d)
    run(os.path.join(SKILLS, "checker-health", "health.py"), os.path.join(d, "actuals.json"))
    run(os.path.join(SKILLS, "checker-report", "compile.py"), "--dir", d)
    print("Demo project in %s. Open it with: python3 %s --dir %s" % (project, os.path.join(HERE, "serve.py"), project))
    return 0


if __name__ == "__main__":
    sys.exit(main())
