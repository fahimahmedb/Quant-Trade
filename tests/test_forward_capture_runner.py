"""Lightweight regression checks for the manual runner script's own wiring.

The script is a thin CLI over already-tested library functions
(`forward_capture.execute_forward_capture`, `forward_coverage.*`); this file
does not re-test those (see their own dedicated test modules) or make network
calls. It only guards the parts that are specific to the script itself: that
its declared universe matches the one already authorized elsewhere in the
repository, and that its subcommands are wired to the expected handlers.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_SPEC = importlib.util.spec_from_file_location(
    "forward_capture_runner", ROOT / "scripts" / "forward_capture_runner.py")
runner = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(runner)

from quant.dataplane.ingest import BENCHMARK, CONTEXT, SECTOR_UNIVERSE  # noqa: E402


class RunnerWiringTest(unittest.TestCase):
    def test_forward_universe_matches_the_already_authorized_ingest_universe(self):
        """No new, unauthorized universe is invented for forward capture."""
        self.assertEqual(set(runner.FORWARD_UNIVERSE),
                         set(SECTOR_UNIVERSE) | {BENCHMARK} | set(CONTEXT))

    def test_source_id_matches_the_authorized_source_inventory_entry(self):
        from quant.dataplane.forward_contracts import YAHOO_DAILY_CHART
        self.assertEqual(runner.SOURCE_ID, YAHOO_DAILY_CHART.source_id)
        self.assertTrue(YAHOO_DAILY_CHART.capturable_now)

    def test_every_subcommand_has_a_handler(self):
        parser_actions = {"declare-universe", "declare-sessions", "run-once",
                          "status", "coverage"}
        for name in parser_actions:
            handler_name = f"cmd_{name.replace('-', '_')}"
            self.assertTrue(hasattr(runner, handler_name), f"missing {handler_name}")

    def test_run_once_never_calls_the_network_adapter_when_not_due_and_not_forced(self):
        import tempfile
        from datetime import datetime, timezone

        with tempfile.TemporaryDirectory() as directory:
            from quant.paths import QuantPaths
            paths = QuantPaths(Path(directory)).ensure_forward()
            from quant.dataplane.forward_capture import ForwardCaptureTaskStore
            task_store = ForwardCaptureTaskStore(paths.forward_tasks)
            task = task_store.get(runner.SOURCE_ID)
            task.last_attempt_at = datetime.now(timezone.utc).isoformat()
            task_store.save()

            called = {"count": 0}
            original = runner.yahoo_forward_adapter
            runner.yahoo_forward_adapter = lambda **kwargs: called.__setitem__(
                "count", called["count"] + 1) or (lambda symbols: (_ for _ in ()).throw(
                    AssertionError("adapter must not be built or called")))
            try:
                import argparse
                exit_code = runner.cmd_run_once(paths, argparse.Namespace(force=False))
            finally:
                runner.yahoo_forward_adapter = original
            self.assertEqual(exit_code, 0)
            self.assertEqual(called["count"], 0)


if __name__ == "__main__":
    unittest.main()
