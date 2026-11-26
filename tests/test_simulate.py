import json
import os
import re
import shutil
import tempfile
import unittest

from _load import ROOT, SKILLS_DIR, load, example

reviews = load("checker-customers", "reviews")
sim = load("checker-simulate", "simulate")


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class Panel(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        reviews.main(["--reviews", example("checker-customers", "reviews.example.csv"),
                      "--survey", example("checker-customers", "survey.example.csv"), "--out", self.d])
        self.customers = os.path.join(self.d, "customers.json")
        self.actuals = example("checker-health", "example.json")

    def tearDown(self):
        shutil.rmtree(self.d)

    def panel(self, *extra):
        rc = sim.main(["panel", "--customers", self.customers, "--actuals", self.actuals, "--out", self.d] + list(extra))
        self.assertEqual(rc, 0)
        with open(os.path.join(self.d, "panel.json"), encoding="utf-8") as fh:
            return json.load(fh)

    def test_default_is_thirty_grounded_in_the_evidence(self):
        p = self.panel()
        self.assertTrue(p["simulated"])
        self.assertIn("SIMULATED", p["label"])
        self.assertEqual(p["n"], 30)
        self.assertEqual(len(p["personas"]), 30)
        self.assertEqual((p["current"], p["lapsed"]), (15, 15))
        with open(self.customers, encoding="utf-8") as fh:
            c = json.load(fh)
        real_themes = {t["theme"] for t in c["review_tally"]["complaints"]} | {"pujian"}
        real_reasons = {r["reason"] for r in c["survey"]["reasons"]}
        for q in p["personas"]:
            self.assertIn(q["concern"], real_themes if q["status"] == "current" else real_reasons)
            self.assertIn(q["channel"], p["channels"])
        # the channel mix follows the real sales: walk-in is the biggest
        chans = [q["channel"] for q in p["personas"]]
        self.assertEqual(max(set(chans), key=chans.count), "walk-in")
        # concerns follow how often each came up: lama (3 reviews) gets more personas than kemasan (1)
        cur = [q["concern"] for q in p["personas"] if q["status"] == "current"]
        self.assertGreater(cur.count("lama"), cur.count("kemasan"))
        self.assertEqual(sorted(set(cur)), sorted(real_themes))

    def test_any_size(self):
        for n in (1, 7, 100, 250):
            p = self.panel("--n", str(n))
            self.assertEqual(len(p["personas"]), n)
            self.assertEqual(len({q["id"] for q in p["personas"]}), n)

    def test_same_seed_same_panel(self):
        self.assertEqual(self.panel()["personas"], self.panel()["personas"])

    def test_needs_real_customers(self):
        empty = write(self.d, "c.json", "{}")
        with self.assertRaisesRegex(sim.DataError, "checker-customers"):
            sim.build_panel(json.load(open(empty)), None)

    def test_no_survey_means_no_lapsed(self):
        with open(self.customers, encoding="utf-8") as fh:
            c = json.load(fh)
        del c["survey"]
        p = sim.build_panel(c, None, 12)
        self.assertEqual(p["lapsed"], 0)
        self.assertEqual(len(p["personas"]), 12)


class Tally(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        reviews.main(["--reviews", example("checker-customers", "reviews.example.csv"),
                      "--survey", example("checker-customers", "survey.example.csv"), "--out", self.d])
        with open(os.path.join(self.d, "customers.json"), encoding="utf-8") as fh:
            self.panel = sim.build_panel(json.load(fh), None, 10)
        self.panel_path = write(self.d, "panel.json", json.dumps(self.panel))
        self.ids = [p["id"] for p in self.panel["personas"]]

    def tearDown(self):
        shutil.rmtree(self.d)

    def answers(self, a_yes, b_yes, b_maybe=0):
        rows = ["persona,variant,decision,reason,would_pay"]
        for i, pid in enumerate(self.ids):
            rows.append("%s,A,%s,%s," % (pid, "ya" if i < a_yes else "tidak", "" if i < a_yes else "harga"))
            if i < b_yes:
                rows.append("%s,B,ya,,Rp25.000" % pid)
            elif i < b_yes + b_maybe:
                rows.append("%s,B,boleh juga,lihat dulu," % pid)
            else:
                rows.append("%s,B,tidak,porsi," % pid)
        return write(self.d, "answers-1.csv", "\n".join(rows) + "\n")

    def test_mungkin_is_a_no_and_files_are_labelled(self):
        rc = sim.main(["tally", "--panel", self.panel_path, "--answers", self.answers(3, 6, 3), "--out", self.d])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.d, "simulate.json"), encoding="utf-8") as fh:
            r = json.load(fh)
        self.assertTrue(r["simulated"])
        self.assertEqual(r["variants"]["B"]["answers"], {"ya": 6, "mungkin": 3, "tidak": 1})
        self.assertEqual(r["variants"]["B"]["rate"], 0.6)
        self.assertEqual(r["variants"]["B"]["median_would_pay"], 25000)
        self.assertEqual(r["lead"]["best"], "B")
        self.assertEqual(r["lead"]["points"], 0.3)
        self.assertTrue(r["lead"]["too_close"])  # 10 personas is a thin panel
        with open(os.path.join(self.d, "simulate-data.md"), encoding="utf-8") as fh:
            md = fh.read()
        self.assertIn("SIMULATED", md.splitlines()[2])
        self.assertIn("a mungkin is a no", md)

    def test_every_persona_answers_every_variant(self):
        p = write(self.d, "a.csv", "persona,variant,decision,reason,would_pay\n%s,A,ya,,\n" % self.ids[0])
        with self.assertRaisesRegex(sim.DataError, "no answer from 9"):
            sim.tally(self.panel, sim._rows(p))

    def test_bad_rows(self):
        cases = [("P99,A,ya,,", "not in the panel"), ("%s,A,entah,,", "ya, mungkin or tidak"),
                 ("%s,A,tidak,,", "reason code"), ("%s,A,ya,,dua puluh", "Rupiah"), ("%s,,ya,,", "variant")]
        for row, msg in cases:
            p = write(self.d, "a.csv", "persona,variant,decision,reason,would_pay\n" + row.replace("%s", self.ids[0]) + "\n")
            with self.assertRaisesRegex(sim.DataError, msg):
                sim.tally(self.panel, sim._rows(p))


class Fenced(unittest.TestCase):
    """The simulation never reaches the verdict: the health check, board, report and dashboard do not read it."""

    def test_nothing_real_reads_the_simulation(self):
        paths = [os.path.join(SKILLS_DIR, "checker-health", "health.py"),
                 os.path.join(SKILLS_DIR, "checker-health", "SKILL.md"),
                 os.path.join(SKILLS_DIR, "checker-board", "SKILL.md"),
                 os.path.join(SKILLS_DIR, "checker-board", "lenses.md"),
                 os.path.join(SKILLS_DIR, "checker-report", "SKILL.md"),
                 os.path.join(SKILLS_DIR, "checker-report", "compile.py"),
                 os.path.join(ROOT, "gui", "state.py")]
        for path in paths:
            with open(path, encoding="utf-8") as fh:
                self.assertNotRegex(fh.read(), re.compile(r"simulate", re.I), os.path.relpath(path, ROOT))


if __name__ == "__main__":
    unittest.main()
