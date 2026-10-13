"""Adversarial pre-execution tests for the Q30 path-2 cost diagnostic. SYNTHETIC data only: the diagnostic is never computed
on the real B2/B4 rows by these tests, so no result is observed before the single execution."""
import ast
import datetime as dt
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "cost_model_q30"))
import run_cost_diag as cd  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.desk.execution import ExecutionModel  # noqa: E402
from quant.factory.evaluate import falsify, summarize  # noqa: E402
from quant.factory.signals import StrategySpec  # noqa: E402


def weekdays(n, start=dt.date(2022, 1, 3)):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def panel_of(symbols, n=80, volume=1_000_000.0, price=100.0, seed=1):
    rng, dates, rows = random.Random(seed), weekdays(n), []
    for s in symbols:
        p = price
        for d in dates:
            p *= 1.0 + rng.gauss(0, 0.005)
            rows.append({"date": d, "symbol": s, "open": p, "high": p, "low": p, "close": p, "adj_close": p, "volume": volume})
    return PricePanel(rows), dates


def make_rows(dates, weights_by_day, returns_by_day=None):
    rows = []
    for k, w in enumerate(weights_by_day):
        rows.append({"signal_date": dates[25 + k], "entry_date": dates[26 + k], "exit_date": dates[27 + k], "weights": dict(w),
                     "returns": (returns_by_day[k] if returns_by_day else {s: 0.001 for s in w}), "positions": len(w)})
    return rows


class CostArithmetic(unittest.TestCase):
    def setUp(self):
        self.panel, self.dates = panel_of(["SPY", "TLT"])
        self.third = 1 / 3

    def test_sign_flip_is_charged_on_the_full_absolute_weight_change(self):
        rows = make_rows(self.dates, [{"SPY": self.third}, {"SPY": -self.third}])
        priced = cd.price_rows(rows, self.panel, 1_000_000.0, {**cd.CENTRAL, "borrow_bps_year": 0.0})
        delta = 2 / 3
        # E1: commission is the DESK's own, on the slippage-adjusted fill price of a SIGNED order (a sale fills below the reference).
        model = ExecutionModel()
        reference = self.panel.adjusted(rows[1]["entry_date"], "SPY", "open")
        fill = model.fill(self.panel, "SPY", -delta * 1_000_000.0 / reference, rows[1]["signal_date"], rows[1]["entry_date"])
        self.assertAlmostEqual(priced["posts"]["commission"][1], fill["commission"] / 1_000_000.0, places=15)
        self.assertLess(fill["fill_price"], reference)
        self.assertAlmostEqual(priced["posts"]["spread"][1], delta * 1.0 / 10_000, places=15)
        self.assertAlmostEqual(priced["turnover"][1], delta, places=15)

    def test_entry_charges_one_unit_once_and_an_unchanged_position_charges_nothing(self):
        rows = make_rows(self.dates, [{"SPY": self.third}, {"SPY": self.third}])
        priced = cd.price_rows(rows, self.panel, 1_000_000.0, cd.CENTRAL)
        self.assertAlmostEqual(priced["posts"]["spread"][0], self.third * 1.0 / 10_000, places=15)
        self.assertEqual(priced["posts"]["spread"][1], 0.0)
        self.assertEqual(priced["posts"]["commission"][1], 0.0)

    def test_initial_position_removes_the_artificial_entry_cost(self):
        rows = make_rows(self.dates, [{"SPY": self.third}])
        self.assertEqual(cd.price_rows(rows, self.panel, 1e6, cd.CENTRAL, initial={"SPY": self.third})["turnover"][0], 0.0)

    def test_borrow_is_charged_on_short_exposure_of_every_instrument_and_only_there(self):
        rows = make_rows(self.dates, [{"SPY": -self.third, "TLT": self.third}])
        priced = cd.price_rows(rows, self.panel, 1e6, {**cd.CENTRAL, "commission_bps": 0.0, "half_spread_bps": 0.0, "impact_bps_at_5pct": 0.0})
        self.assertAlmostEqual(priced["posts"]["borrow"][0], self.third * 100.0 / 10_000 / 252, places=15)
        self.assertEqual(priced["by_instrument"]["TLT"]["borrow"], 0.0)
        self.assertGreater(priced["by_instrument"]["SPY"]["borrow"], 0.0)

    def test_financing_is_charged_on_gross_exposure_including_longs(self):
        rows = make_rows(self.dates, [{"SPY": self.third, "TLT": -self.third}])
        params = {**cd.CENTRAL, "financing_bps_year": 500.0}
        priced = cd.price_rows(rows, self.panel, 1e6, params)
        self.assertAlmostEqual(priced["posts"]["financing"][0], 2 * self.third * 500.0 / 10_000 / 252, places=15)

    def test_gross_minus_posts_equals_net_exactly_and_by_instrument(self):
        rng = random.Random(3)
        weights = [{"SPY": rng.choice((-1, 0, 1)) / 3, "TLT": rng.choice((-1, 0, 1)) / 3} for _ in range(40)]
        returns = [{"SPY": rng.gauss(0, .01), "TLT": rng.gauss(0, .01)} for _ in range(40)]
        rows = make_rows(self.dates, weights, returns)
        for params in (cd.CENTRAL, cd.STRESS):
            self.assertLess(cd.reconciliation_error(cd.price_rows(rows, self.panel, 1e6, params)), 1e-12)

    def test_costs_are_monotone_in_the_multiplier_and_zero_multiplier_is_gross(self):
        rng = random.Random(4)
        weights = [{"SPY": rng.choice((-1, 0, 1)) / 3} for _ in range(40)]
        rows = make_rows(self.dates, weights, [{"SPY": rng.gauss(0, .01)} for _ in range(40)])
        nets = [sum(cd.price_rows(rows, self.panel, 1e6, cd.STRESS, m)["net"]) for m in cd.MULTIPLIERS]
        self.assertTrue(all(a >= b for a, b in zip(nets, nets[1:])))
        zero = cd.price_rows(rows, self.panel, 1e6, cd.STRESS, 0.0)
        self.assertEqual(zero["net"], zero["gross"])

    def test_the_central_model_is_the_desk_model_not_a_copy(self):
        model = cd.model_for(cd.CENTRAL)
        self.assertEqual(model, ExecutionModel())
        self.assertIs(type(model), ExecutionModel)


class Capacity(unittest.TestCase):
    def test_adv_is_causal_it_ignores_volume_after_the_signal_date(self):
        panel_a, dates = panel_of(["SPY"], volume=1_000.0)
        rows_b = []
        for d in dates:
            bar = panel_a.bars[(d, "SPY")]
            rows_b.append({"date": d, "symbol": "SPY", **{**bar, "volume": bar["volume"] * (1000 if d > dates[26] else 1)}})
        panel_b = PricePanel(rows_b)
        rows = make_rows(dates, [{"SPY": 1 / 3}])
        a = cd.price_rows(rows, panel_a, 1e6, cd.CENTRAL)
        b = cd.price_rows(rows, panel_b, 1e6, cd.CENTRAL)
        self.assertEqual(a["posts"], b["posts"])

    def test_participation_above_the_desk_limit_is_a_refusal_not_a_cap(self):
        panel, dates = panel_of(["SPY"], volume=10_000.0, price=100.0)  # ADV about 1e6 dollars
        rows = make_rows(dates, [{"SPY": 1 / 3}])
        small = cd.price_rows(rows, panel, 1_000.0, cd.CENTRAL)
        large = cd.price_rows(rows, panel, 1_000_000_000.0, cd.CENTRAL)
        self.assertEqual(small["breaches"], [])
        self.assertTrue(large["breaches"])
        self.assertGreater(large["max_participation"], 0.05)

    def test_zero_adv_is_undetermined_and_fail_closed(self):
        panel, dates = panel_of(["SPY"], volume=0.0)
        rows = make_rows(dates, [{"SPY": 1 / 3}])
        priced = cd.price_rows(rows, panel, 1e6, cd.CENTRAL)
        self.assertTrue(priced["undetermined"])
        status = cd.status_for({"net_return": 1, "gross_pnl_arithmetic": 1, "post_totals": {}}, {}, {}, {}, priced)
        self.assertEqual(status["status"], "COST_UNDETERMINED")


class ReviewFixes(unittest.TestCase):
    def test_a_breached_order_is_priced_with_an_uncapped_impact(self):
        panel, dates = panel_of(["SPY"], volume=10_000.0, price=100.0)
        rows = make_rows(dates, [{"SPY": 1 / 3}])
        model = ExecutionModel()
        adv = model.adv(panel, "SPY", rows[0]["signal_date"])
        for nav in (3e6, 30e6):
            participation = (1 / 3) * nav / adv
            self.assertGreater(participation, 0.05)
            priced = cd.price_rows(rows, panel, nav, cd.CENTRAL)
            expected = (1 / 3) * 10.0 * (participation / 0.05) ** 0.5 / 10_000
            self.assertAlmostEqual(priced["posts"]["impact"][0], expected, places=12)
            self.assertTrue(priced["breaches"])

    def test_an_untruncated_order_keeps_the_desk_impact(self):
        panel, dates = panel_of(["SPY"], volume=1e9, price=100.0)
        rows = make_rows(dates, [{"SPY": 1 / 3}])
        priced = cd.price_rows(rows, panel, 1e6, cd.CENTRAL)
        adv = ExecutionModel().adv(panel, "SPY", rows[0]["signal_date"])
        expected = (1 / 3) * 10.0 * ((1 / 3) * 1e6 / adv / 0.05) ** 0.5 / 10_000
        self.assertAlmostEqual(priced["posts"]["impact"][0], expected, places=15)
        self.assertEqual(priced["breaches"], [])

    def test_a_bad_reconciliation_or_identity_forces_undetermined_over_every_other_status(self):
        clean = {"undetermined": [], "breaches": [], "max_participation": 0.0}
        central = {"net_return": 0.1, "gross_pnl_arithmetic": 0.2, "post_totals": {"commission": 0.0}}
        ok = {"a": True}
        for recon, ident in ((1e-12, 0.0), (float("nan"), 0.0), (float("inf"), 0.0), (0.0, 1e-3), (0.0, float("nan"))):
            problems = cd.integrity_problems(recon, ident)
            self.assertTrue(problems, (recon, ident))
            self.assertEqual(cd.status_for(central, {}, ok, ok, clean, problems)["status"], "COST_UNDETERMINED")
        self.assertEqual(cd.integrity_problems(9e-13, 1e-10), [])

    def test_the_turnover_identity_holds_for_the_published_row_convention(self):
        panel, dates = panel_of(["SPY", "TLT"])
        rows = make_rows(dates, [{"SPY": 1 / 3, "TLT": -1 / 3}, {"SPY": -1 / 3, "TLT": -1 / 3}, {"SPY": 0.0, "TLT": 1 / 3}])
        priced = cd.price_rows(rows, panel, 1e6, cd.CENTRAL)
        original = [2 / 3, 2 / 3, 1 / 3 + 2 / 3]
        self.assertAlmostEqual(sum(priced["turnover"]), sum(original), places=12)

    def test_any_unexpected_exception_is_persisted_as_an_invalid_run(self):
        import json
        original = cd.compute

        def boom(*a, **k):
            raise KeyError("x")
        cd.compute = boom
        try:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "r.json"
                self.assertEqual(cd.main(["run_cost_diag.py", str(target)]), 1)
                doc = json.loads(target.read_text())
                self.assertEqual(doc["RESULT"], "INVALID_INPUT")
                self.assertIn("KeyError", doc["problems"][0])
        finally:
            cd.compute = original

    def test_the_result_records_provenance_and_post_labels(self):
        import json
        original = cd.compute
        cd.compute = lambda *a, **k: {"x": 1.0}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "r.json"
                cd.main(["run_cost_diag.py", str(target)])
                doc = json.loads(target.read_text())
        finally:
            cd.compute = original
        self.assertEqual(doc["erratum_1_sha256"], cd.ERRATUM_SHA256)
        self.assertEqual(doc["specification_sha256"], cd.SPEC_SHA256)
        self.assertEqual(len(doc["harness_sha256"]), 64)
        self.assertTrue(doc["central_equals_desk_defaults"])
        self.assertIn("ASSUMED_BORROW_BPS_YEAR", doc["post_labels"].values())

    def test_the_frozen_b4_module_is_executed_from_the_verified_bytes(self):
        with self.assertRaisesRegex(cd.InvalidInput, "frozen B4 harness"):
            cd._load_frozen("x", cd.B4_PATH, "0" * 64)
        module = cd._load_frozen("y", cd.B4_PATH, cd.B4_BLOB_SHA256)
        self.assertTrue(callable(module.rows_for))


class PreRegisteredOutputs(unittest.TestCase):
    def test_orders_are_audited_with_side_notional_adv_participation_and_shortfall(self):
        panel, dates = panel_of(["SPY"])
        rows = make_rows(dates, [{"SPY": 1 / 3}, {"SPY": -1 / 3}])
        priced = cd.price_rows(rows, panel, 1e6, cd.CENTRAL, record_orders=True)
        self.assertEqual(len(priced["orders"]), 2)
        first, second = priced["orders"]
        self.assertEqual((first[2], second[2]), (1.0, -1.0))
        self.assertAlmostEqual(second[3], (2 / 3) * 1e6)
        self.assertGreater(second[4], 0)
        self.assertAlmostEqual(second[5], second[3] / second[4])
        self.assertAlmostEqual(second[6], (priced["posts"]["commission"][1] + priced["posts"]["spread"][1] + priced["posts"]["impact"][1]) * 1e6)

    def test_metrics_include_drawdown_monetary_cost_and_cost_per_turnover(self):
        panel, dates = panel_of(["SPY"])
        rng = random.Random(5)
        rows = make_rows(dates, [{"SPY": rng.choice((-1, 1)) / 3} for _ in range(40)], [{"SPY": rng.gauss(0, .01)} for _ in range(40)])
        priced = cd.price_rows(rows, panel, 1e6, cd.CENTRAL)
        m = cd.metrics_from(rows, priced, priced)
        self.assertLessEqual(m["max_drawdown"], 0.0)
        self.assertAlmostEqual(m["total_cost_fraction_of_nav"], sum(m["post_totals"].values()))
        self.assertAlmostEqual(m["cost_per_unit_turnover_bps"], m["total_cost_fraction_of_nav"] / m["total_turnover"] * 1e4)

    def test_total_break_even_multiplier_zeroes_the_net_pnl(self):
        panel, dates = panel_of(["SPY"])
        rows = make_rows(dates, [{"SPY": 1 / 3}, {"SPY": -1 / 3}] * 10, [{"SPY": 0.002}, {"SPY": -0.002}] * 10)
        m = cd.break_even_total_multiplier(rows, panel, 1e6)
        self.assertNotIsInstance(m, dict)
        self.assertAlmostEqual(sum(cd.price_rows(rows, panel, 1e6, cd.CENTRAL, m)["net"]), 0.0, places=9)

    def test_b4_targets_carry_the_selected_or_comparison_role(self):
        n = 2700
        panel, dates = panel_of(list(cd.b4.INSTRUMENTS), n=n, seed=11)
        shifted = weekdays(n, start=dt.date(2016, 9, 12))
        rows = [{"date": shifted[dates.index(d)], "symbol": s, **{k: v for k, v in b.items()}} for (d, s), b in panel.bars.items()]
        targets = cd.b4_targets(PricePanel(rows))
        roles = {k: v["role"] for k, v in targets.items()}
        self.assertEqual(roles["B4_L252"], "selected_in_B4")
        for k in ("B4_L21", "B4_L63", "B4_L126"):
            self.assertEqual(roles[k], "comparison_only_not_for_selection")


class Status(unittest.TestCase):
    CLEAN = {"undetermined": [], "breaches": [], "max_participation": 0.0}

    def central(self, **over):
        m = {"net_return": 0.05, "gross_pnl_arithmetic": 0.10, "post_totals": {"commission": 0.01, "spread": 0.01, "impact": 0.0,
                                                                              "borrow": 0.02, "financing": 0.0}}
        m.update(over)
        return m

    def test_all_four_statuses(self):
        ok = {"a": True, "b": True}
        bad = {"a": True, "b": False}
        self.assertEqual(cd.status_for(self.central(), {}, ok, ok, self.CLEAN)["status"], "COST_ROBUST")
        self.assertEqual(cd.status_for(self.central(), {}, ok, bad, self.CLEAN)["status"], "COST_SENSITIVE")
        self.assertEqual(cd.status_for(self.central(), {}, bad, ok, self.CLEAN)["status"], "COST_INFEASIBLE")
        self.assertEqual(cd.status_for(self.central(net_return=-0.01), {}, ok, ok, self.CLEAN)["status"], "COST_INFEASIBLE")
        self.assertEqual(cd.status_for(self.central(), {}, ok, ok, {**self.CLEAN, "breaches": [1]})["status"], "COST_INFEASIBLE")

    def test_one_post_taking_half_of_gross_makes_it_sensitive(self):
        ok = {"a": True}
        heavy = self.central(post_totals={"commission": 0.0, "spread": 0.0, "impact": 0.0, "borrow": 0.05, "financing": 0.0})
        self.assertEqual(cd.status_for(heavy, {}, ok, ok, self.CLEAN)["status"], "COST_SENSITIVE")

    def test_non_positive_gross_pnl_is_infeasible_and_the_post_share_is_not_evaluated(self):
        ok = {"a": True}
        result = cd.status_for(self.central(gross_pnl_arithmetic=-0.01), {}, ok, ok, self.CLEAN)
        self.assertEqual(result["status"], "COST_INFEASIBLE")
        self.assertTrue(any("not evaluated" in r for r in result["reasons"]))

    def test_undetermined_beats_every_other_status(self):
        out = cd.status_for(self.central(net_return=-1), {}, {"a": False}, {"a": False}, {**self.CLEAN, "undetermined": [1], "breaches": [1]})
        self.assertEqual(out["status"], "COST_UNDETERMINED")


class BreakEven(unittest.TestCase):
    def test_bisection_finds_the_known_borrow_break_even(self):
        panel, dates = panel_of(["SPY"])
        # constant short position: net = gross - |w| * rate * n ; choose gross so the break-even is 250 bp/year
        n, w = 30, -1 / 3
        per_day_gross = abs(w) * 250.0 / 10_000 / 252
        returns = [{"SPY": -per_day_gross / abs(w)} for _ in range(n)]  # short earns -ret * |w|
        rows = make_rows(dates, [{"SPY": w}] * n, returns)
        params_free = {**cd.CENTRAL, "commission_bps": 0.0, "half_spread_bps": 0.0, "impact_bps_at_5pct": 0.0}
        original = cd.CENTRAL
        cd.CENTRAL = params_free
        try:
            value = cd.break_even(rows, panel, 1e6, "borrow_bps_year", initial={"SPY": w})
        finally:
            cd.CENTRAL = original
        self.assertAlmostEqual(value, 250.0, places=3)

    def test_a_series_that_never_crosses_zero_is_reported_not_bracketed(self):
        panel, dates = panel_of(["SPY"])
        rows = make_rows(dates, [{"SPY": 1 / 3}] * 10, [{"SPY": 0.01}] * 10)
        out = cd.break_even(rows, panel, 1e6, "borrow_bps_year", initial={"SPY": 1 / 3})
        self.assertIsInstance(out, dict)
        self.assertEqual(out["status"], "NOT_BRACKETED")


class CriteriaParity(unittest.TestCase):
    def test_b2_criteria_match_falsify_on_the_shared_tests(self):
        panel, dates = panel_of(["SPY", "XLB"], n=400, seed=7)
        rng = random.Random(9)
        rows, net = [], []
        for k in range(300):
            ret = rng.gauss(0.0004, 0.01)
            rows.append({"signal_date": dates[k], "entry_date": dates[k + 1], "exit_date": dates[k + 2], "gross_return": ret,
                         "cost": 0.0, "net_return": ret, "turnover": 0.1, "positions": 2})
            net.append(ret)
        summary = summarize(rows, panel, "SPY", 5.0)
        spec = StrategySpec(family="cross_sectional", universe=["XLB", "SPY"], lookback_days=21, direction=1)
        verdict = falsify(rows, summary, panel, "SPY", spec, cd.B2_TRIALS)
        market = [panel.adjusted(r["exit_date"], "SPY", "open") / panel.adjusted(r["entry_date"], "SPY", "open") - 1.0 for r in rows]
        m = {"net_return": summary["net_return"], "stress_net_return": 0.1, "halves": verdict["subperiod_returns"], "t_statistic": summary["t_statistic"]}
        mine = cd.b2_criteria(m, market, net, summary["active_observations"])
        tests = verdict["tests"]
        self.assertEqual(mine["net_profitable"], tests["net_profitable_after_modeled_costs"])
        self.assertEqual(mine["profitable_in_both_subperiods"], tests["profitable_in_both_subperiods"])
        self.assertEqual(mine["market_beta_below_0_15"], tests["market_beta_below_0_15"])
        self.assertEqual(mine["top_5_days_below_half_of_gains"], tests["top_5_days_below_half_of_gains"])
        self.assertEqual(mine["t_statistic_survives_multiple_testing"], tests["t_statistic_survives_multiple_testing"])
        self.assertEqual(mine["at_least_100_active_observations"], tests["at_least_100_active_observations"])


class Gates(unittest.TestCase):
    def test_altered_dataset_is_refused_before_anything_is_computed(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "p.csv"
            data = bytearray(cd.DATA.read_bytes())
            data[-5] ^= 1
            copy.write_bytes(bytes(data))
            with self.assertRaisesRegex(cd.InvalidInput, "fingerprint"):
                cd.compute(data_path=copy)

    def test_a_changed_frozen_b4_harness_is_refused(self):
        original = cd.B4_BLOB_SHA256
        cd.B4_BLOB_SHA256 = "0" * 64
        try:
            with self.assertRaisesRegex(cd.InvalidInput, "frozen B4 harness"):
                cd.compute()
        finally:
            cd.B4_BLOB_SHA256 = original

    def test_the_frozen_b4_dependency_matches_its_pinned_hash(self):
        cd.check_frozen_dependency()

    def test_forbidden_lines_never_reach_the_csv_parser(self):
        fed, original = [], cd.csv.DictReader

        def spy(lines, *a, **k):
            lines = list(lines)
            fed.extend(lines)
            return original(lines, *a, **k)
        cd.csv.DictReader = spy
        try:
            panel, skipped = cd.build_panel(cd.DATA, cd.B2_PANEL_SYMBOLS + ["TLT", "GLD"])
        finally:
            cd.csv.DictReader = original
        self.assertLess(max(line[:10] for line in fed[1:]), cd.FIRST_FORBIDDEN_DATE)
        self.assertEqual(len(fed) - 1 + skipped, 30168)
        self.assertEqual(panel.dates[-1], cd.LAST_RESEARCH_DATE)

    def test_write_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "r.json"
            existing.write_text("x")
            self.assertEqual(cd.main(["run_cost_diag.py", str(existing)]), 2)
            self.assertEqual(cd.main(["run_cost_diag.py", str(Path(tmp) / "new" / "r.json")]), 2)
        for sub in ("data", "var", "src"):
            self.assertEqual(cd.main(["run_cost_diag.py", str(ROOT / sub / "c.json")]), 2)

    def test_a_late_filesystem_change_invalidates_the_persisted_result(self):
        import json
        original_compute, original_delta = cd.compute, cd.b4.delta
        calls = []
        cd.compute = lambda *a, **k: {"x": 1.0}
        cd.b4.delta = lambda before, after: (calls.append(1) or ([] if len(calls) == 1 else ["/repo/unexpected"]))
        try:
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "r.json"
                self.assertEqual(cd.main(["run_cost_diag.py", str(target)]), 3)
                doc = json.loads(target.read_text())
                self.assertEqual((doc["RESULT"], doc["return_code"]), ("INVALID_INPUT", 3))
        finally:
            cd.compute, cd.b4.delta = original_compute, original_delta

    def test_source_calls_no_state_mutating_api_and_writes_only_through_the_protocol(self):
        tree = ast.parse((ROOT / "research/cost_model_q30/run_cost_diag.py").read_text())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for banned in ("run_lane", "StrategyRegistry", "EventLog", "record_trials", "preserve_research_partition",
                       "append_jsonl", "write_json", "ResearchTicket", "mkdir", "write_text", "write_bytes"):
            self.assertNotIn(banned, names)


if __name__ == "__main__":
    unittest.main()
