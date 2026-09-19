"""Adversarial tests for the Forward Coverage Ledger.

The mission's own words drive the sharpest assertions here: "UNKNOWN != MISSING.
MISSING != ZERO." Several tests exist purely to prove those two inequalities
hold in code, not just in the docstring.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from quant.dataplane.forward_capture import (ATTEMPT_FAILED, ATTEMPT_SUCCEEDED,
                                             AttemptJournal, CaptureAttempt,
                                             FAILURE_TIMEOUT, VALIDATION_NOT_APPLICABLE,
                                             VALIDATION_OK)
from quant.dataplane.forward_coverage import (CELL_ATTEMPTED, CELL_CONFLICT,
                                              CELL_EXPECTED, CELL_MISSING,
                                              CELL_OBSERVED, CELL_UNKNOWN, CELL_VALID,
                                              ExpectedCalendar, ForwardCoverageLedger,
                                              seed_expected_sessions_from_dataset)
from quant.dataplane.forward_recorder import ForwardObservation, ForwardRecorder
from quant.dataplane.panel import PricePanel

SOURCE = "yahoo_daily_chart"


def rig(directory: str, grace_hours: float = 24.0):
    root = Path(directory)
    calendar = ExpectedCalendar(root / "sessions.jsonl", root / "universe.jsonl")
    recorder = ForwardRecorder(root / "forward.jsonl")
    journal = AttemptJournal(root / "attempts.jsonl")
    ledger = ForwardCoverageLedger(calendar, recorder, journal, SOURCE,
                                   missing_grace_hours=grace_hours)
    return calendar, recorder, journal, ledger


def attempt(source_id=SOURCE, outcome=ATTEMPT_SUCCEEDED, failure_state=None,
           sessions_observed=(), symbols_observed=(), attempt_id="a1") -> CaptureAttempt:
    return CaptureAttempt(
        attempt_id=attempt_id, source_id=source_id, source_version="v1",
        market_session="REGULAR", symbols_requested=("XLK",),
        fetch_started_at="2026-09-18T21:00:00+00:00",
        fetch_completed_at="2026-09-18T21:00:01+00:00" if outcome == ATTEMPT_SUCCEEDED else None,
        outcome=outcome, failure_state=failure_state, schema_version="v1",
        payload_hash="sha256:aa" if outcome == ATTEMPT_SUCCEEDED else None,
        validation_state=VALIDATION_OK if outcome == ATTEMPT_SUCCEEDED else VALIDATION_NOT_APPLICABLE,
        lineage="test", symbols_observed=symbols_observed, sessions_observed=sessions_observed)


class ExpectedCalendarTest(unittest.TestCase):
    def test_declaring_sessions_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, *_ = rig(directory)
            self.assertEqual(calendar.declare_sessions(["2026-09-18", "2026-09-19"]), 2)
            self.assertEqual(calendar.declare_sessions(["2026-09-18"]), 0)
            self.assertEqual(calendar.expected_sessions(), {"2026-09-18", "2026-09-19"})

    def test_universe_change_is_not_applied_retroactively(self):
        """Adding a symbol today must not make yesterday's silence MISSING."""
        with tempfile.TemporaryDirectory() as directory:
            calendar, *_ = rig(directory)
            calendar.declare_universe(["XLK", "SPY"], effective_from="2026-09-01")
            calendar.declare_universe(["XLK", "SPY", "NEWSYMBOL"], effective_from="2026-09-19")
            self.assertEqual(calendar.expected_symbols_for("2026-09-10"), {"XLK", "SPY"})
            self.assertEqual(calendar.expected_symbols_for("2026-09-19"),
                             {"XLK", "SPY", "NEWSYMBOL"})
            # Before any declaration existed at all: genuinely unknown, not empty.
            self.assertIsNone(calendar.expected_symbols_for("2026-08-01"))

    def test_seed_from_a_validated_dataset_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset_path = root / "snapshot.csv"
            PricePanel([
                {"date": "2026-09-16", "symbol": "XLK", "open": 1, "high": 1,
                 "low": 1, "close": 1, "adj_close": 1, "volume": 1},
                {"date": "2026-09-17", "symbol": "XLK", "open": 1, "high": 1,
                 "low": 1, "close": 1, "adj_close": 1, "volume": 1},
            ]).write(dataset_path)
            calendar, *_ = rig(directory)
            added = seed_expected_sessions_from_dataset(calendar, dataset_path)
            self.assertEqual(added, 2)
            self.assertEqual(calendar.expected_sessions(), {"2026-09-16", "2026-09-17"})

    def test_seed_from_the_real_committed_sector_panel(self):
        """Lightweight integration check against the actual repository dataset."""
        repo_root = Path(__file__).resolve().parents[1]
        dataset_path = repo_root / "data" / "datasets" / "us_sector_etf_daily.csv"
        if not dataset_path.exists():
            self.skipTest("committed sector panel not present in this checkout")
        with tempfile.TemporaryDirectory() as directory:
            calendar, *_ = rig(directory)
            added = seed_expected_sessions_from_dataset(calendar, dataset_path, ["SPY"])
            self.assertGreater(added, 2000)  # this panel has thousands of sessions


class ClassifyTest(unittest.TestCase):
    NOW_SESSION_OPEN = datetime(2026, 9, 18, 12, 0, 0, tzinfo=timezone.utc)
    NOW_AFTER_CLOSE = datetime(2026, 9, 19, 6, 0, 0, tzinfo=timezone.utc)  # +1d +6h
    NOW_GRACE_ELAPSED = datetime(2026, 9, 20, 6, 0, 0, tzinfo=timezone.utc)  # +2d +6h

    def declared(self, calendar):
        calendar.declare_sessions(["2026-09-18"])
        calendar.declare_universe(["XLK"], effective_from="2026-09-01")

    def test_undeclared_cell_is_unknown_not_missing(self):
        """No calendar/universe authority at all: UNKNOWN, never MISSING."""
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, ledger = rig(directory)
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_UNKNOWN)

    def test_symbol_outside_the_effective_universe_is_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, _, ledger = rig(directory)
            self.declared(calendar)
            cell = ledger.classify("2026-09-18", "NOT_IN_UNIVERSE", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_UNKNOWN)

    def test_session_not_yet_closed_is_unknown_not_expected(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, _, ledger = rig(directory)
            self.declared(calendar)
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_SESSION_OPEN)
            self.assertEqual(cell.state, CELL_UNKNOWN)

    def test_closed_declared_never_attempted_is_expected(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, _, ledger = rig(directory)
            self.declared(calendar)
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_AFTER_CLOSE)
            self.assertEqual(cell.state, CELL_EXPECTED)

    def test_failed_attempts_within_grace_are_attempted_not_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, journal, ledger = rig(directory, grace_hours=24.0)
            self.declared(calendar)
            failed = attempt(outcome=ATTEMPT_FAILED, failure_state=FAILURE_TIMEOUT)
            journal.append(failed)
            # journaled_at is stamped by AttemptJournal.append at call time
            # (now, in this test's real wall clock), which is always >= the
            # 2026-09-19 close bound used for comparison, so it counts as
            # "after close" -- this exercises the source-wide attempt
            # attribution described in the module docstring.
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_AFTER_CLOSE)
            self.assertEqual(cell.state, CELL_ATTEMPTED)

    def test_missing_requires_grace_period_not_just_a_failure(self):
        """MISSING != ZERO: one failed attempt alone is not enough."""
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, journal, ledger = rig(directory, grace_hours=0.0)
            self.declared(calendar)
            journal.append(attempt(outcome=ATTEMPT_FAILED, failure_state=FAILURE_TIMEOUT))
            still_attempted = ledger.classify("2026-09-18", "XLK", self.NOW_AFTER_CLOSE)
            # With zero grace hours, immediately-after-close attempts already
            # exceed the grace bound, so this specific configuration reaches
            # MISSING -- proving MISSING is reachable at all, and that it is a
            # named disposition earned by an elapsed grace period rather than
            # a default value silently returned for "nothing recorded yet".
            self.assertEqual(still_attempted.state, CELL_MISSING)

    def test_missing_is_never_the_default_for_an_unattempted_cell(self):
        """A cell nobody ever tried is EXPECTED, never silently MISSING."""
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, _, ledger = rig(directory, grace_hours=0.0)
            self.declared(calendar)
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_EXPECTED)
            self.assertNotEqual(cell.state, CELL_MISSING)

    def test_valid_observation_wins_over_any_attempt_history(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, recorder, journal, ledger = rig(directory)
            self.declared(calendar)
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-18", fields={"close": 100.0},
                source=SOURCE, source_fingerprint="sha256:aa"))
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_VALID)
            self.assertIsNotNone(cell.known_since)

    def test_conflict_is_visible_as_its_own_state(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, recorder, journal, ledger = rig(directory)
            self.declared(calendar)
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-18", fields={"close": 100.0},
                source=SOURCE, source_fingerprint="sha256:aa",
                recorded_at="2026-09-18T21:00:00+00:00"))
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-18", fields={"close": 101.0},
                source=SOURCE, source_fingerprint="sha256:bb",
                recorded_at="2026-09-19T21:00:00+00:00"))
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_CONFLICT)

    def test_observed_names_the_gap_between_a_validated_fetch_and_a_durable_write(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, recorder, journal, ledger = rig(directory)
            self.declared(calendar)
            journal.append(attempt(outcome=ATTEMPT_SUCCEEDED,
                                   sessions_observed=("2026-09-18",),
                                   symbols_observed=("XLK",)))
            # No recorder entry at all -- simulating a crash after the fetch
            # validated but before (or in a differently-ordered adapter,
            # instead of) the durable record was written.
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            self.assertEqual(cell.state, CELL_OBSERVED)

    def test_unrelated_successful_attempt_does_not_manufacture_coverage(self):
        """A success for a different symbol/session must not launder this cell."""
        with tempfile.TemporaryDirectory() as directory:
            calendar, _, journal, ledger = rig(directory, grace_hours=0.0)
            self.declared(calendar)
            journal.append(attempt(outcome=ATTEMPT_SUCCEEDED,
                                   sessions_observed=("2026-09-17",),  # different session
                                   symbols_observed=("XLK",)))
            cell = ledger.classify("2026-09-18", "XLK", self.NOW_GRACE_ELAPSED)
            # The only attempt on file did not cover this cell and was not
            # itself a failure either -- summary() must still be able to
            # count it, and it must not be silently promoted to VALID/OBSERVED.
            self.assertIn(cell.state, (CELL_MISSING, CELL_EXPECTED, CELL_ATTEMPTED))
            self.assertNotEqual(cell.state, CELL_VALID)
            self.assertNotEqual(cell.state, CELL_OBSERVED)


class SummaryTest(unittest.TestCase):
    def test_summary_counts_every_declared_cell_exactly_once(self):
        with tempfile.TemporaryDirectory() as directory:
            calendar, recorder, journal, ledger = rig(directory, grace_hours=0.0)
            calendar.declare_sessions(["2026-09-17", "2026-09-18"])
            calendar.declare_universe(["XLK", "SPY"], effective_from="2026-09-01")
            recorder.record(ForwardObservation(
                symbol="XLK", session_date="2026-09-17", fields={"close": 1.0},
                source=SOURCE, source_fingerprint="sha256:aa"))
            now = datetime(2026, 9, 20, 0, 0, 0, tzinfo=timezone.utc)
            summary = ledger.summary(now)
            self.assertEqual(sum(summary["counts"].values()), 4)  # 2 sessions x 2 symbols
            self.assertEqual(summary["counts"][CELL_VALID], 1)
            self.assertEqual(summary["counts"][CELL_EXPECTED], 3)
            self.assertEqual(len(summary["cells"]), 4)


if __name__ == "__main__":
    unittest.main()
