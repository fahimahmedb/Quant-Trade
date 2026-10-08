"""Adversarial pre-execution tests for the B4 harness. Mechanics are tested on SYNTHETIC panels only: the real
family computation is never run, so no result on the real data is observed before the single execution."""
import ast
import datetime as dt
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "time_series_macro_b4"))
import run_b4 as b4  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402


def weekdays(n, start=dt.date(2016, 9, 12)):
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def panel_from(prices: dict, dates):
    """prices[name] = list of closes; open = close, adj_close = close (no distributions)."""
    rows = []
    for name, series in prices.items():
        for d, p in zip(dates, series):
            rows.append({"date": d, "symbol": name, "open": p, "high": p, "low": p, "close": p, "adj_close": p, "volume": 1})
    return PricePanel(rows)


def random_walk(n, seed, drift=0.0):
    rng, p, out = random.Random(seed), 100.0, []
    for _ in range(n):
        p *= 1.0 + drift + rng.gauss(0, 0.01)
        out.append(p)
    return out


class Mechanics(unittest.TestCase):
    def setUp(self):
        self.dates = weekdays(900)
        self.prices = {n: random_walk(900, i) for i, n in enumerate(b4.INSTRUMENTS)}
        self.panel = panel_from(self.prices, self.dates)

    def test_no_look_ahead(self):
        cut = 500
        altered = {n: s[:cut + 1] + [x * 3.7 for x in s[cut + 1:]] for n, s in self.prices.items()}
        other = panel_from(altered, self.dates)
        for L in b4.LOOKBACKS:
            a = [r for r in b4.rows_for(self.panel, L) if r["exit_date"] <= self.dates[cut]]
            b = [r for r in b4.rows_for(other, L) if r["exit_date"] <= self.dates[cut]]
            self.assertTrue(a)
            self.assertEqual(a, b)

    def test_timeline_signal_at_close_t_entry_t_plus_1_exit_t_plus_2(self):
        row = b4.rows_for(self.panel, 21)[0]
        i = self.dates.index(row["signal_date"])
        self.assertEqual((row["entry_date"], row["exit_date"]), (self.dates[i + 1], self.dates[i + 2]))
        self.assertEqual(i, 21)  # first causal signal needs L earlier closes
        self.assertEqual(len(b4.rows_for(self.panel, 21)), len(self.dates) - 21 - 2)

    def test_sign_flip_costs_two_thirds_and_entry_via_zero_one_third(self):
        n = 120
        flat, up, down = [100.0] * 60, [100.0 + i for i in range(1, 31)], [130.0 - 3.1 * i for i in range(1, 31)]
        spy = flat + up + down
        panel = panel_from({"SPY": spy, "TLT": [100.0] * n, "GLD": [100.0] * n}, weekdays(n))
        rows = b4.rows_for(panel, 21)
        weights = [r["weights"]["SPY"] for r in rows]
        turnovers = [r["turnover"]["SPY"] for r in rows]
        self.assertEqual(weights[0], 0.0)
        enter = weights.index(1 / 3)
        self.assertAlmostEqual(turnovers[enter], 1 / 3)             # entry via zero
        flips = [i for i in range(1, len(weights)) if weights[i - 1] > 0 > weights[i]]
        self.assertTrue(flips)
        self.assertAlmostEqual(turnovers[flips[0]], 2 / 3)          # +1/3 -> -1/3
        for r in rows:                                               # flat instruments never trade
            self.assertEqual((r["weights"]["TLT"], r["turnover"]["TLT"]), (0.0, 0.0))

    def test_borrow_only_on_tlt_and_gld_shorts(self):
        base = {"gross": 0}
        row = {"weights": {"SPY": -1 / 3, "TLT": -1 / 3, "GLD": -1 / 3}, "returns": {n: 0.0 for n in b4.INSTRUMENTS},
               "turnover": {n: 0.0 for n in b4.INSTRUMENTS}}
        parts = b4.net_parts(row, 5.0, 100.0)
        self.assertEqual(parts["SPY"]["borrow"], 0.0)
        expected = (1 / 3) * 100.0 / 10_000.0 / 252
        self.assertAlmostEqual(parts["TLT"]["borrow"], expected, places=15)
        self.assertAlmostEqual(parts["GLD"]["borrow"], expected, places=15)
        long_row = dict(row, weights={n: 1 / 3 for n in b4.INSTRUMENTS})
        self.assertEqual(sum(p["borrow"] for p in b4.net_parts(long_row, 5.0, 100.0).values()), 0.0)
        del base

    def test_transaction_cost_applies_to_full_absolute_weight_change(self):
        row = {"weights": {"SPY": -1 / 3, "TLT": 0.0, "GLD": 0.0}, "returns": {n: 0.0 for n in b4.INSTRUMENTS},
               "turnover": {"SPY": 2 / 3, "TLT": 0.0, "GLD": 0.0}}
        self.assertAlmostEqual(b4.net_series([row], 5.0, 0.0)[0], -(2 / 3) * 5.0 / 10_000.0)

    def test_instrument_contributions_reconcile_with_net_return(self):
        rows = [r for r in b4.rows_for(self.panel, 63) if r["k"] > 300]
        m = b4.metrics(rows)
        self.assertLess(abs(m["instrument_contribution_sum"] - m["arithmetic_net_sum"]), 1e-12)

    def test_whole_family_runs_on_synthetic_data_and_is_deterministic(self):
        bounds = {"DISCOVERY": (self.dates[0], self.dates[650]), "EVALUATION": (self.dates[651], self.dates[897])}
        a, b = b4.evaluate_family(self.panel, bounds), b4.evaluate_family(self.panel, bounds)
        self.assertTrue(b4.same(a, b))
        self.assertIn(a["selected_lookback"], b4.LOOKBACKS)
        self.assertLess(a["reconciliation_error"], 1e-12)
        self.assertEqual(set(a["criteria"]), {k for k in a["criteria"]})
        self.assertEqual(len(a["criteria"]), 7)

    def test_family_output_is_json_serialisable_and_main_would_not_crash_on_write(self):
        import json
        bounds = {"DISCOVERY": (self.dates[0], self.dates[650]), "EVALUATION": (self.dates[651], self.dates[897])}
        out = b4.evaluate_family(self.panel, bounds)
        out.update({"fingerprint_before": "x", "TRIAL_COUNT_SOURCE": "REGISTRY"})
        text = json.dumps({"RESULT": b4.judge(out, dict(out)), "run": out}, sort_keys=True)
        self.assertIn("candidate_metrics", text)
        self.assertEqual(json.loads(text)["run"]["selected_lookback"], out["selected_lookback"])

    def test_the_three_instruments_share_the_same_dates_in_the_real_panel(self):
        panel, _ = b4.build_research_panel(b4.DATA)
        per = {n: [d for d in panel.dates if panel.has(d, n)] for n in b4.INSTRUMENTS}
        self.assertEqual(per["SPY"], per["TLT"])
        self.assertEqual(per["SPY"], per["GLD"])
        self.assertEqual(panel.aligned_dates(b4.INSTRUMENTS), panel.dates)

    def test_selection_uses_only_the_common_intersection(self):
        rows = b4.rows_for(self.panel, 21)
        bounds = (self.dates[0], self.dates[650])
        chosen = b4.common_discovery_rows(rows, bounds)
        self.assertTrue(chosen)
        self.assertTrue(all(r["k"] >= 252 for r in chosen))
        self.assertTrue(all(b4.in_window(r, bounds) for r in chosen))
        self.assertLess(len(chosen), len([r for r in rows if b4.in_window(r, bounds)]))

    def test_rows_are_dropped_when_entry_or_exit_leaves_the_window(self):
        rows = b4.rows_for(self.panel, 21)
        edge = self.dates[400]
        inside = [r for r in rows if b4.in_window(r, (self.dates[0], edge))]
        self.assertEqual(inside[-1]["exit_date"], edge)
        self.assertTrue(all(r["exit_date"] <= edge for r in inside))


class Selection(unittest.TestCase):
    def test_ties_go_to_the_smaller_lookback(self):
        self.assertEqual(b4.select_lookback({21: 0.5, 63: 0.5, 126: 0.5, 252: 0.5}), 21)
        self.assertEqual(b4.select_lookback({21: 0.5, 63: 0.5 + 1e-13, 126: 0.4, 252: 0.1}), 21)

    def test_a_strictly_higher_sharpe_wins(self):
        self.assertEqual(b4.select_lookback({21: 0.1, 63: 0.2, 126: 0.15, 252: 0.3}), 252)
        self.assertEqual(b4.select_lookback({21: 0.1, 63: 0.2 + 1e-9, 126: 0.15, 252: 0.1}), 63)


class Criteria(unittest.TestCase):
    def good(self, **over):
        m = {"net_return": 0.1, "net_sharpe": 0.5, "t_statistic": 3.227, "halves": [0.01, 0.02], "stress_net_return": 0.01,
             "positive_annual_total": 1.0, "max_year_share": 0.6,
             "instrument_net_contribution": {"SPY": 1.0, "TLT": 0.5, "GLD": -0.2}}
        m.update(over)
        return m

    def test_all_seven_pass_exactly_at_the_pre_registered_boundaries(self):
        self.assertTrue(all(b4.criteria(self.good()).values()))

    def test_each_criterion_fails_independently(self):
        cases = {"1_net_return_positive": {"net_return": 0.0}, "2_net_sharpe_positive": {"net_sharpe": 0.0},
                 "3_t_statistic_at_least_threshold": {"t_statistic": 3.2269}, "4_both_halves_positive": {"halves": [0.01, -0.01]},
                 "5_stress_net_positive": {"stress_net_return": 0.0}, "6_no_year_above_60pct": {"max_year_share": 0.61},
                 "7_at_least_two_instruments_positive": {"instrument_net_contribution": {"SPY": 1.0, "TLT": -0.5, "GLD": -0.2}}}
        for name, over in cases.items():
            result = b4.criteria(self.good(**over))
            self.assertFalse(result[name], name)
            self.assertEqual(sum(1 for ok in result.values() if not ok), 1, name)

    def test_zero_positive_annual_total_fails_criterion_6(self):
        self.assertFalse(b4.criteria(self.good(positive_annual_total=0.0, max_year_share=None))["6_no_year_above_60pct"])

    def test_threshold_is_the_pre_registered_constant(self):
        from statistics import NormalDist
        self.assertEqual(b4.T_THRESHOLD, 3.227)
        self.assertAlmostEqual(NormalDist().inv_cdf(1 - 0.05 / (2 * b4.TRIAL_COUNT)), 3.2272, places=4)
        self.assertEqual(b4.TRIAL_COUNT, b4.PRIOR_TRIALS + len(b4.LOOKBACKS))


class TrialCount(unittest.TestCase):
    def _files(self, tmp, registry=None, state="After 36 declared expressions the bar is higher."):
        reg = Path(tmp) / "strategies.json"
        if registry is not None:
            reg.write_text(registry)
        st = Path(tmp) / "STATE.md"
        if state is not None:
            st.write_text(state)
        return reg, st

    def test_registry_with_exactly_36_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, st = self._files(tmp, '{"trials": {"us_sector_etf_daily@sha256:ab": 24, "us_sector_etf_daily@sha256:cd": 12}}')
            self.assertEqual(b4.trial_count_source(reg, st), "REGISTRY")

    def test_registry_with_another_count_is_invalid(self):
        for payload in ('{"trials": {"us_sector_etf_daily@x": 35}}', '{"trials": {"us_sector_etf_daily@x": 37}}', '{"trials": {}}', "not json"):
            with tempfile.TemporaryDirectory() as tmp:
                reg, st = self._files(tmp, payload)
                with self.assertRaises(b4.InvalidTrialCount):
                    b4.trial_count_source(reg, st)

    def test_absent_registry_falls_back_to_state_md_and_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, st = self._files(tmp)
            self.assertEqual(b4.trial_count_source(reg, st), "STATE_MD_NO_REGISTRY")

    def test_absent_registry_with_conflicting_or_missing_state_md_is_invalid(self):
        for state in ("after 36 declared expressions and after 40 declared expressions", "nothing relevant", None):
            with tempfile.TemporaryDirectory() as tmp:
                reg, st = self._files(tmp, state=state)
                with self.assertRaises(b4.InvalidTrialCount):
                    b4.trial_count_source(reg, st)

    def test_registry_36_but_conflicting_state_md_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, st = self._files(tmp, '{"trials": {"us_sector_etf_daily@x": 36}}', state="After 40 declared expressions the bar rises.")
            with self.assertRaisesRegex(b4.InvalidTrialCount, "conflict"):
                b4.trial_count_source(reg, st)
            reg, st = self._files(tmp, '{"trials": {"us_sector_etf_daily@x": 36}}', state="no relevant sentence")
            self.assertEqual(b4.trial_count_source(reg, st), "REGISTRY")
            reg, st = self._files(tmp, '{"trials": {"us_sector_etf_daily@x": 36}}', state=None)
            self.assertEqual(b4.trial_count_source(reg, st), "REGISTRY")

    def test_real_state_md_records_36(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(b4.trial_count_source(Path(tmp) / "none.json", b4.STATE_MD), "STATE_MD_NO_REGISTRY")


class Gates(unittest.TestCase):
    def test_altered_dataset_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            data = bytearray(b4.DATA.read_bytes())
            data[-5] ^= 1
            copy.write_bytes(bytes(data))
            with self.assertRaisesRegex(b4.InvalidInput, "fingerprint"):
                b4.compute(data_path=copy)

    def test_appended_shadow_row_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            shutil.copy(b4.DATA, copy)
            with open(copy, "a") as f:
                f.write("2026-09-14,SPY,1,1,1,1,1,1\n")
            with self.assertRaisesRegex(b4.InvalidInput, "fingerprint"):
                b4.compute(data_path=copy)

    def test_moved_bounds_are_refused(self):
        with self.assertRaisesRegex(b4.InvalidInput, "window bounds"):
            b4.compute(bounds={"DISCOVERY": ("2016-09-12", "2022-03-08"), "EVALUATION": ("2022-03-09", "2025-03-12")})

    def test_no_post_boundary_bar_is_ever_materialised(self):
        seen, original = [], PricePanel.__init__

        def spy(self, rows):
            seen.extend(str(r["date"]) for r in rows)
            original(self, rows)
        PricePanel.__init__ = spy
        try:
            panel, skipped = b4.build_research_panel(b4.DATA)
        finally:
            PricePanel.__init__ = original
        self.assertTrue(seen)
        self.assertLess(max(seen), b4.FIRST_FORBIDDEN_DATE)
        self.assertEqual(max(panel.dates), b4.LAST_RESEARCH_DATE)
        self.assertEqual(sorted(panel.symbols), sorted(b4.INSTRUMENTS))
        self.assertGreater(skipped, 0)

    def test_forbidden_lines_never_reach_the_csv_parser(self):
        fed, original = [], b4.csv.DictReader

        def spy(lines, *a, **k):
            lines = list(lines)
            fed.extend(lines)
            return original(lines, *a, **k)
        b4.csv.DictReader = spy
        try:
            panel, skipped = b4.build_research_panel(b4.DATA)
        finally:
            b4.csv.DictReader = original
        self.assertGreater(len(fed), 1000)
        self.assertTrue(fed[0].startswith("date,"))
        self.assertLess(max(line[:10] for line in fed[1:]), b4.FIRST_FORBIDDEN_DATE)
        self.assertGreater(skipped, 0)
        self.assertEqual(len(fed) - 1 + skipped, 30168)

    def test_a_line_without_a_leading_date_is_refused_not_passed_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "p.csv"
            bad.write_text("date,symbol,open,high,low,close,adj_close,volume\n2026-09-14,SPY,1,1,1,1,1,1\n\"2026-09-14\",SPY,1,1,1,1,1,1\n")
            with self.assertRaisesRegex(b4.InvalidInput, "leading ISO date"):
                b4.build_research_panel(bad)
            bad.write_text("symbol,date\n")
            with self.assertRaisesRegex(b4.InvalidInput, "header"):
                b4.build_research_panel(bad)

    def test_registry_precondition_runs_before_any_bar_is_parsed(self):
        seen, original = [], PricePanel.__init__
        PricePanel.__init__ = lambda self, rows: seen.append(1) or original(self, rows)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                reg = Path(tmp) / "r.json"
                reg.write_text('{"trials": {"us_sector_etf_daily@x": 99}}')
                with self.assertRaises(b4.InvalidTrialCount):
                    b4.compute(registry=reg)
        finally:
            PricePanel.__init__ = original
        self.assertEqual(seen, [])


class Metadata(unittest.TestCase):
    def test_real_metadata_passes(self):
        b4.check_metadata()

    def test_missing_altered_or_inconsistent_metadata_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "none.json"
            with self.assertRaisesRegex(b4.InvalidInput, "missing"):
                b4.check_metadata(missing)
            altered = Path(tmp) / "m.json"
            altered.write_bytes(b4.META.read_bytes().replace(b'"rows": 30168', b'"rows": 30169'))
            with self.assertRaisesRegex(b4.InvalidInput, "differs from the expected identity"):
                b4.check_metadata(altered)
        with self.assertRaisesRegex(b4.InvalidInput, "inconsistent"):
            b4.check_metadata(b4.META, "sha256:" + "0" * 64)

    def test_compute_refuses_before_parsing_when_metadata_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(b4.InvalidInput, "missing"):
                b4.compute(meta_path=Path(tmp) / "none.json")


class WritePolicy(unittest.TestCase):
    def test_existing_target_forbidden_locations_and_missing_parent_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "r.json"
            existing.write_text("x")
            self.assertEqual(b4.main(["run_b4.py", str(existing)]), 2)
            self.assertEqual(existing.read_text(), "x")
            missing = Path(tmp) / "new_dir" / "r.json"
            self.assertEqual(b4.main(["run_b4.py", str(missing)]), 2)
            self.assertFalse(missing.parent.exists())
        for sub in ("data", "var", "src"):
            self.assertEqual(b4.main(["run_b4.py", str(ROOT / sub / "b4.json")]), 2)

    def test_snapshot_delta_and_bytecode_flag(self):
        self.assertTrue(sys.dont_write_bytecode)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").write_text("1")
            before = b4.snapshot(root)
            self.assertEqual(b4.delta(before, b4.snapshot(root)), [])
            (root / "b").write_text("2")
            self.assertEqual({Path(p).name for p in b4.delta(before, b4.snapshot(root))}, {"b"})

    def test_source_calls_no_state_mutating_api(self):
        tree = ast.parse((ROOT / "research/time_series_macro_b4/run_b4.py").read_text())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for banned in ("run_lane", "StrategyRegistry", "EventLog", "record_trials", "preserve_research_partition",
                       "preserve_research_cohort", "append_jsonl", "write_json", "ResearchTicket", "mkdir", "write_text", "write_bytes"):
            self.assertNotIn(banned, names)


class Judge(unittest.TestCase):
    def test_statuses(self):
        run = {"all_criteria_true": False, "x": 1.0}
        self.assertEqual(b4.judge(run, dict(run)), "FAMILY_REJECTED")
        self.assertEqual(b4.judge(dict(run, all_criteria_true=True), dict(run, all_criteria_true=True)), "PROVISIONAL_POSITIVE_ON_SPENT_DATA")
        self.assertEqual(b4.judge(run, dict(run, x=1.0 + 1e-6)), "REPRODUCTION_DIVERGENCE")
        self.assertEqual(b4.judge(run, dict(run, x=1.0 + 1e-12)), "FAMILY_REJECTED")


if __name__ == "__main__":
    unittest.main()
