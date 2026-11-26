import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

report = load("checker-report", "compile")


class Compile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, name, text):
        with open(os.path.join(self.d, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_nothing_is_incomplete(self):
        v, text = report.compile_report(self.d)
        self.assertEqual(v, "Incomplete")
        self.assertIn("Run /checker-intake", text)

    def test_example_report(self):
        shutil.copy(example("checker-health", "example.json"), os.path.join(self.d, "actuals.json"))
        self.write("business.md", "# Bakso Mas Yono\n\n- What it is: a bakso stall.\n")
        self.write("health.md", "# stale\n\nVerdict: Sehat\n")
        v, text = report.compile_report(self.d)
        self.assertEqual(v, "Waspada")
        self.assertTrue(text.startswith("# Bakso Mas Yono · Business check-up"))
        self.assertIn("## The top 3 fixes", text)
        self.assertIn("1. **Up to Rp3.521.061 a month.**", text)
        self.assertNotIn("stale", text)  # the numbers section is rebuilt, never copied
        self.assertEqual(text.count("**Verdict:"), 1)
        self.assertIn("- What customers say: run /checker-customers", text)
        self.assertNotIn("$", text)

    def test_compliance_gap_makes_it_kritis(self):
        shutil.copy(example("checker-health", "example.json"), os.path.join(self.d, "actuals.json"))
        self.write("compliance.json", json.dumps({"items": [
            {"item": "BPOM MD", "status": "missing", "severity": "blocks_sales"}]}))
        v, text = report.compile_report(self.d)
        self.assertEqual(v, "Kritis")
        self.assertIn("✗ Missing what selling needs: BPOM MD.", text)
        self.assertEqual(report.main(["--dir", self.d, "--check"]), 2)
        self.assertEqual(report.main(["--dir", self.d]), 0)
        self.assertTrue(os.path.exists(os.path.join(self.d, "report.md")))


if __name__ == "__main__":
    unittest.main()
