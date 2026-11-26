import copy
import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

health = load("checker-health", "health")


def actuals():
    with open(example("checker-health", "example.json"), encoding="utf-8") as fh:
        return json.load(fh)


def status(h, cid):
    return next(c["status"] for c in h["checks"] if c["id"] == cid)


def one_month(**change):
    m = {"month": "2026-11", "days_open": 30,
         "channels": {"walk-in": {"gross": 60000000, "commission": 0}},
         "direct_cost": 18000000, "labour": 12000000, "fixed_costs": 8000000, "pph_final": 300000}
    m.update(change)
    return {"business": "Test", "type": "fnb", "months": [m]}


class Example(unittest.TestCase):
    """The numbers the README quotes."""

    def setUp(self):
        self.h = health.analyse(actuals())

    def test_verdict_is_waspada(self):
        self.assertEqual(self.h["verdict"], "Waspada")
        self.assertEqual([c["id"] for c in self.h["checks"] if c["status"] != "ok"], ["trend", "direct_cost", "cash"])
        self.assertEqual(health.money(self.h["profit_after_owner_pay"]), "Rp11.516.067")

    def test_readme_numbers(self):
        R = self.h["recent"]
        self.assertEqual(health.money(R["net_profit"]), "Rp17.516.067")
        self.assertEqual(health.money(R["kept"]), "Rp4.616.067")
        self.assertAlmostEqual(self.h["trend"]["change"], -0.0723, places=3)
        self.assertEqual(health.pct(R["direct_cost"] / R["net_sales"]), "38.5%")
        self.assertAlmostEqual(self.h["cash"]["weeks_covered"], 1.56, places=2)
        fixes = [(f["id"], health.money(f["rupiah_per_month"])) for f in self.h["fixes"]]
        self.assertEqual(fixes, [("trend", "Rp3.521.061"), ("direct_cost", "Rp2.594.110"), ("platforms", "Rp1.442.333")])

    def test_net_profit_adds_up(self):
        for m in self.h["months"]:
            self.assertAlmostEqual(m["net_sales"], m["gross"] - m["discounts"] - m["commission"])
            self.assertAlmostEqual(m["net_profit"], m["net_sales"] - m["direct_cost"] - m["labour"] - m["fixed_costs"]
                                   - m["pph_final"] - m["other_costs"])

    def test_breakeven_leaves_zero_profit(self):
        R, be = self.h["recent"], self.h["breakeven_month"]
        profit_at_be = be * self.h["contribution_ratio"] - R["labour"] - R["fixed_costs"] - R["other_costs"]
        self.assertAlmostEqual(profit_at_be, 0, places=2)

    def test_report_text(self):
        md = health.health_md(self.h)
        self.assertTrue(md.startswith("# Bakso Mas Yono · Health check"))
        self.assertIn("**Verdict: Waspada** (includes estimates)", md)
        self.assertIn("| **Kept by the business** | **Rp4.616.067** | |", md)
        self.assertNotIn("$", md)


class Verdicts(unittest.TestCase):
    def test_no_months_is_incomplete(self):
        self.assertEqual(health.analyse({"business": "x", "type": "fnb", "months": []})["verdict"], "Incomplete")

    def test_a_healthy_month_is_sehat(self):
        h = health.analyse(one_month())
        self.assertEqual(h["verdict"], "Sehat", [c["text"] for c in h["checks"]])

    def test_a_loss_is_kritis(self):
        h = health.analyse(one_month(fixed_costs=40000000))
        self.assertEqual(h["verdict"], "Kritis")
        self.assertEqual(status(h, "margin"), "bad")
        self.assertEqual(status(h, "breakeven"), "bad")

    def test_owner_taking_more_than_profit(self):
        h = health.analyse(one_month(owner_drawings=30000000))
        self.assertEqual(status(h, "owner"), "warn")
        self.assertEqual(h["fixes"][0]["id"], "owner")

    def test_shrinking_cash_with_little_left_is_kritis(self):
        # profit Rp21.700.000, owner takes Rp40.000.000: cash shrinks Rp18.300.000 a month
        a = one_month(owner_drawings=40000000)
        a["cash"] = {"balance": 25000000}
        h = health.analyse(a)
        self.assertGreater(h["cash"]["weeks_covered"], 2)  # enough this week...
        self.assertEqual(status(h, "cash"), "bad")         # ...but gone in under 3 months
        self.assertAlmostEqual(h["cash"]["months_left"], 25000000 / 18300000.0)
        a["cash"] = {"balance": 250000000}
        self.assertEqual(status(health.analyse(a), "cash"), "warn")

    def test_cost_five_points_over_target_is_critical(self):
        # net sales are Rp60.000.000; the fnb target is 35%, critical above 40%
        self.assertEqual(status(health.analyse(one_month(direct_cost=24500000)), "direct_cost"), "bad")  # 40.8%
        self.assertEqual(status(health.analyse(one_month(direct_cost=22000000)), "direct_cost"), "warn")  # 36.7%
        self.assertEqual(status(health.analyse(one_month(direct_cost=21000000)), "direct_cost"), "ok")  # 35.0%

    def test_owner_target_wins_over_default(self):
        a = one_month(direct_cost=24000000)
        a["targets"] = {"direct_cost_pct": 0.42}
        h = health.analyse(a)
        self.assertEqual(status(h, "direct_cost"), "ok")
        self.assertEqual(h["targets"]["source"]["direct_cost_pct"], "owner")

    def test_other_type_has_no_cost_targets(self):
        a = one_month()
        a["type"] = "other"
        ids = [c["id"] for c in health.analyse(a)["checks"]]
        self.assertNotIn("direct_cost", ids)
        self.assertNotIn("labour", ids)

    def test_bad_reviews_cap_at_waspada(self):
        h = health.analyse(one_month(), customers={"rating_avg": 3.1, "reviews": 40})
        self.assertEqual(status(h, "customers"), "bad")
        self.assertEqual(h["verdict"], "Waspada")

    def test_compliance(self):
        items = lambda *s: {"items": [{"item": "x%d" % i, "status": st, "severity": sev} for i, (st, sev) in enumerate(s)]}
        self.assertEqual(health.analyse(one_month(), compliance=items(("missing", "blocks_sales")))["verdict"], "Kritis")
        self.assertEqual(health.analyse(one_month(), compliance=items(("unknown", "penalty")))["verdict"], "Waspada")
        h = health.analyse(one_month(), compliance=items(("ok", "blocks_sales"), ("missing", "advised")))
        self.assertEqual(h["verdict"], "Sehat")
        self.assertIn("Advised: x1.", h["checks"][-1]["text"])

    def test_rating_is_judged_as_shown(self):
        # 4.18 shows as 4.2 on the page, so it passes the 4.2 line
        h = health.analyse(one_month(), customers={"rating_avg": 4.18, "reviews": 1647})
        self.assertEqual(status(h, "customers"), "ok")
        self.assertIn("1.647 reviews", h["checks"][-1]["text"])

    def test_profit_that_is_only_the_owners_unpaid_work(self):
        a = one_month()  # net profit Rp21.700.000
        a["owner_fair_salary"] = 25000000
        h = health.analyse(a)
        self.assertEqual(status(h, "owner_pay"), "warn")
        self.assertEqual(h["verdict"], "Waspada")
        a["owner_fair_salary"] = 6000000
        self.assertEqual(status(health.analyse(a), "owner_pay"), "ok")

    def test_qris_fees_are_not_a_platform(self):
        h = health.analyse(one_month(channels={"walk-in": {"gross": 60000000, "commission": 300000}}))
        self.assertNotIn("platforms", [c["id"] for c in h["checks"]])
        h = health.analyse(one_month(channels={"B2B": {"gross": 60000000, "commission": 300000, "platform": True}}))
        self.assertIn("platforms", [c["id"] for c in h["checks"]])

    def test_small_dip_gives_no_win_back_fix(self):
        a = one_month()
        base = a["months"][0]
        a["months"] = []
        for i, gross in enumerate((60000000, 60000000, 59000000, 59000000)):
            m = copy.deepcopy(base)
            m["month"] = "2026-%02d" % (8 + i)
            m["channels"] = {"walk-in": {"gross": gross}}
            a["months"].append(m)
        h = health.analyse(a)
        self.assertEqual(status(h, "trend"), "ok")
        self.assertNotIn("trend", [f["id"] for f in h["fixes"]])

    def test_missing_months_are_named(self):
        a = one_month()
        later = copy.deepcopy(a["months"][0])
        later["month"] = "2027-02"
        a["months"].append(later)
        self.assertEqual(health.analyse(a)["missing_months"], ["2026-12", "2027-01"])

    def test_platform_dependence(self):
        h = health.analyse(one_month(channels={"walk-in": {"gross": 20000000}, "GoFood": {"gross": 50000000, "commission": 11000000}}))
        self.assertEqual(status(h, "platforms"), "warn")


class Errors(unittest.TestCase):
    def test_missing_field_is_an_error_not_a_guess(self):
        a = one_month()
        del a["months"][0]["labour"]
        with self.assertRaisesRegex(health.ActualsError, "missing labour"):
            health.analyse(a)

    def test_bad_values(self):
        for change, msg in (({"direct_cost": -5}, "negative"), ({"direct_cost": "banyak"}, "not a number"),
                            ({"channels": {}}, "no channels"),
                            ({"channels": {"app": {"gross": 10, "commission": 20}}}, "commission is more")):
            with self.assertRaisesRegex(health.ActualsError, msg):
                health.analyse(one_month(**change))

    def test_month_format(self):
        for bad in ("2026-6", "Nov 2026", "2026-13", ""):
            with self.assertRaisesRegex(health.ActualsError, "YYYY-MM"):
                health.analyse(one_month(month=bad))

    def test_compliance_typos_are_errors_not_passes(self):
        for item, msg in (({"item": "NIB", "status": "Missing", "severity": "blocks_sales"}, "status"),
                          ({"item": "NIB", "status": "missing", "severity": "high"}, "severity")):
            with self.assertRaisesRegex(health.ActualsError, msg):
                health.analyse(one_month(), compliance={"items": [item]})

    def test_duplicate_month(self):
        a = one_month()
        a["months"].append(copy.deepcopy(a["months"][0]))
        with self.assertRaisesRegex(health.ActualsError, "twice"):
            health.analyse(a)


class Cli(unittest.TestCase):
    def test_writes_files_and_exit_codes(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "actuals.json")
            shutil.copy(example("checker-health", "example.json"), p)
            self.assertEqual(health.main([p]), 0)
            self.assertTrue(os.path.exists(os.path.join(d, "health.md")))
            with open(os.path.join(d, "health.json"), encoding="utf-8") as fh:
                self.assertEqual(json.load(fh)["verdict"], "Waspada")
            self.assertEqual(health.main([p, "--check"]), 1)
            self.assertEqual(health.main([os.path.join(d, "nope.json")]), 4)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
