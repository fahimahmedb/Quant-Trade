"""Adversarial pre-execution tests for the B2 harness. None of them runs the real scans, so no result is observed."""
import ast
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research" / "sector_xrev_b2"))
import run_b2  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.factory.lanes import WINDOWS, lane_definitions  # noqa: E402


class FingerprintAndBounds(unittest.TestCase):
    def test_altered_dataset_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            data = bytearray(run_b2.DATA.read_bytes())
            data[-5] ^= 1
            copy.write_bytes(bytes(data))
            with self.assertRaisesRegex(run_b2.InvalidInput, "fingerprint"):
                run_b2.compute(data_path=copy)

    def test_appended_shadow_row_is_refused_by_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "panel.csv"
            shutil.copy(run_b2.DATA, copy)
            with open(copy, "a") as f:
                f.write("2026-09-14,XLB,1,1,1,1,1,1\n")
            with self.assertRaisesRegex(run_b2.InvalidInput, "fingerprint"):
                run_b2.compute(data_path=copy)

    def test_shadow_guard_rejects_a_post_boundary_bar(self):
        rows = [{"date": d, "symbol": "XLB", "open": 1, "high": 1, "low": 1, "close": 1, "adj_close": 1, "volume": 1}
                for d in ("2025-03-11", "2025-03-12")]
        with self.assertRaisesRegex(run_b2.InvalidInput, "2025-03-12"):
            run_b2.assert_no_shadow(PricePanel(rows))
        run_b2.assert_no_shadow(PricePanel(rows[:1]))

    def test_real_research_view_ends_on_the_boundary(self):
        panel = PricePanel.load(run_b2.DATA)
        windows = panel.split(WINDOWS, symbols=run_b2.UNIVERSE)
        run_b2.assert_windows(windows)
        visible = panel.restrict(end=windows["VALIDATION"].end)
        run_b2.assert_no_shadow(visible)
        self.assertEqual(max(visible.dates), run_b2.LAST_RESEARCH_DATE)

    def test_moved_window_bounds_are_refused(self):
        with self.assertRaisesRegex(run_b2.InvalidInput, "window bounds"):
            run_b2.compute(windows_spec={"DISCOVERY": 0.50, "VALIDATION": 0.35, "SHADOW": 0.15})


class GridSize(unittest.TestCase):
    def _defs(self, delta):
        def fake(universe, dataset_id):
            defs = lane_definitions(universe, dataset_id)
            grid = defs[run_b2.LANE2]["grid"]
            defs[run_b2.LANE2] = dict(defs[run_b2.LANE2], grid=grid[:-1] if delta < 0 else grid + grid[:1])
            return defs
        return fake

    def test_declared_grids_are_24_and_12(self):
        defs = lane_definitions(run_b2.UNIVERSE, "us_sector_etf_daily")
        self.assertEqual([len(defs[run_b2.LANE1]["grid"]), len(defs[run_b2.LANE2]["grid"])], [24, 12])

    def test_35_and_37_expressions_are_refused(self):
        for delta in (-1, 1):
            with self.assertRaisesRegex(run_b2.InvalidInput, "pre-registered"):
                run_b2.compute(lane_defs=self._defs(delta))


class WritePolicy(unittest.TestCase):
    def test_existing_target_and_forbidden_locations_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "r.json"
            existing.write_text("x")
            self.assertEqual(run_b2.main(["run_b2.py", str(existing)]), 2)
            self.assertEqual(existing.read_text(), "x")
        for sub in ("data", "var", "src"):
            self.assertEqual(run_b2.main(["run_b2.py", str(ROOT / sub / "b2.json")]), 2)
            self.assertFalse((ROOT / sub / "b2.json").exists())

    def test_source_calls_no_state_mutating_api(self):
        tree = ast.parse((ROOT / "research/sector_xrev_b2/run_b2.py").read_text())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for banned in ("run_lane", "StrategyRegistry", "EventLog", "record_trials", "preserve_research_partition",
                       "preserve_research_cohort", "append_jsonl", "write_json", "ResearchTicket"):
            self.assertNotIn(banned, names)


class Judge(unittest.TestCase):
    def _run(self, **over):
        l2 = {"best": "xs_momentum_l21_z0.5_h5_b0.05", "best_discovery_sharpe": 0.363, "filtered": False,
              "oos_summary": {"net_return": -0.0608, "gross_return": -0.0137, "total_costs": 0.0490, "annual_turnover": 32.9,
                              "market_beta": -0.062, "t_statistic": -0.39, "market_return_same_window": 0.3834},
              "oos_verdict": {"required_t_statistic": 3.20, "decision": "REJECT_RESEARCH"}}
        l2.update(over)
        return {"lane1": {"best": "a", "best_discovery_sharpe": -0.015, "filtered": True}, "lane2": l2}

    def test_recorded_figures_confirm(self):
        run = self._run()
        self.assertEqual(run_b2.judge(run, run)[0], "NEGATIVE_REPLICATION_CONFIRMED")

    def test_any_outside_tolerance_is_divergence(self):
        run = self._run()
        run["lane2"]["oos_summary"]["net_return"] = -0.0500
        self.assertEqual(run_b2.judge(run, run)[0], "REPLICATION_DIVERGENCE")
        run = self._run(best="xs_momentum_l21_z0.5_h21_b0.05")
        self.assertEqual(run_b2.judge(run, run)[0], "REPLICATION_DIVERGENCE")

    def test_nondeterminism_is_divergence(self):
        a, b = self._run(), self._run()
        b["lane2"]["oos_summary"]["t_statistic"] = -0.39 + 1e-6
        self.assertEqual(run_b2.judge(a, b)[0], "REPLICATION_DIVERGENCE")


if __name__ == "__main__":
    unittest.main()
