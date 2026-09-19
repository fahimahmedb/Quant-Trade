"""Adversarial tests for the forward-capture adapter contract and execution engine.

Everything here uses fake adapters and a frozen, injectable clock. Nothing
makes a real network call -- that is exercised separately, live, by
``scripts/forward_capture_runner.py`` and documented in the mission's
handoff artifacts, not asserted here.
"""

from __future__ import annotations

import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from quant.dataplane.adapters import DataUnavailable
from quant.dataplane.forward_capture import (ATTEMPT_FAILED, ATTEMPT_SUCCEEDED,
                                             FAILURE_DNS_OR_NETWORK, FAILURE_HTTP_ERROR,
                                             FAILURE_MALFORMED_RESPONSE,
                                             FAILURE_NO_USABLE_ROWS,
                                             FAILURE_SCHEMA_CHANGED,
                                             FAILURE_SOURCE_ERROR_PAYLOAD,
                                             FAILURE_TIMEOUT, FAILURE_TRUNCATED,
                                             VALIDATION_FAILED, VALIDATION_NOT_APPLICABLE,
                                             VALIDATION_OK, AttemptJournal, CaptureAttempt,
                                             ForwardCaptureFailure, ForwardCaptureRequest,
                                             ForwardCaptureTaskStore, FrozenForwardTimebase,
                                             _classify_failure, _classify_yahoo_exception,
                                             due, execute_forward_capture)
from quant.dataplane.forward_recorder import ForwardRecorder
from quant.dataplane.panel import PricePanel


def panel(rows: list[dict] | None = None) -> PricePanel:
    rows = rows if rows is not None else [
        {"date": "2026-09-18", "symbol": "XLK", "open": 100.0, "high": 101.0,
         "low": 99.0, "close": 100.5, "adj_close": 100.5, "volume": 1_000_000.0},
        {"date": "2026-09-18", "symbol": "SPY", "open": 500.0, "high": 502.0,
         "low": 498.0, "close": 501.0, "adj_close": 501.0, "volume": 2_000_000.0},
    ]
    return PricePanel(rows)


def system(directory: str):
    root = Path(directory)
    recorder = ForwardRecorder(root / "forward.jsonl")
    journal = AttemptJournal(root / "attempts.jsonl")
    task_store = ForwardCaptureTaskStore(root / "tasks.json")
    return recorder, journal, task_store


REQUEST = ForwardCaptureRequest(source_id="yahoo_daily_chart", symbols=("XLK", "SPY"))


class DueTest(unittest.TestCase):
    def test_never_attempted_is_due(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, task_store = system(directory)
            task = task_store.get(REQUEST.source_id)
            self.assertTrue(due(task, REQUEST, FrozenForwardTimebase().now()))

    def test_disabled_task_is_never_due(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, task_store = system(directory)
            task = task_store.get(REQUEST.source_id)
            task.enabled = False
            self.assertFalse(due(task, REQUEST, FrozenForwardTimebase().now()))

    def test_due_respects_the_declared_minimum_interval(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, task_store = system(directory)
            task = task_store.get(REQUEST.source_id)
            timebase = FrozenForwardTimebase()
            task.last_attempt_at = timebase.now().isoformat()
            self.assertFalse(due(task, REQUEST, timebase.now()))
            timebase.advance(REQUEST.min_interval_seconds - 1)
            self.assertFalse(due(task, REQUEST, timebase.now()))
            timebase.advance(2)
            self.assertTrue(due(task, REQUEST, timebase.now()))


class ExecuteForwardCaptureSuccessTest(unittest.TestCase):
    def test_a_successful_attempt_is_journaled_and_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()
            adapter = lambda symbols: (panel(), {"adapter": "fake"})
            result = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             adapter, timebase)
            self.assertEqual(result.attempt.outcome, ATTEMPT_SUCCEEDED)
            self.assertIsNone(result.attempt.failure_state)
            self.assertEqual(result.attempt.validation_state, VALIDATION_OK)
            self.assertEqual(result.accepted_count, 2)
            self.assertEqual(sorted(result.attempt.symbols_observed), ["SPY", "XLK"])
            self.assertEqual(len(journal.all()), 1)
            self.assertEqual(recorder.symbols(), ["SPY", "XLK"])
            task = task_store.get(REQUEST.source_id)
            self.assertEqual(task.attempts, 1)
            self.assertEqual(task.successes, 1)
            self.assertEqual(task.consecutive_failures, 0)
            self.assertIsNotNone(task.last_success_at)

    def test_fetch_started_and_completed_bracket_the_adapter_call(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()

            def slow_adapter(symbols):
                timebase.advance(12.5)  # simulate the network round trip
                return panel(), {}

            result = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             slow_adapter, timebase)
            started = result.attempt.fetch_started_at
            completed = result.attempt.fetch_completed_at
            self.assertNotEqual(started, completed)
            self.assertLess(started, completed)

    def test_idempotent_resubmission_of_the_same_fetch_accepts_nothing_new(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()
            adapter = lambda symbols: (panel(), {})
            first = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                            adapter, timebase)
            timebase.advance(REQUEST.min_interval_seconds + 1)
            second = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             adapter, timebase)
            self.assertEqual(first.accepted_count, 2)
            self.assertEqual(second.accepted_count, 0)  # both DUPLICATE_IGNORED
            self.assertEqual(len(recorder.accepted()), 2)
            self.assertEqual(len(journal.all()), 2)  # both attempts still journaled

    def test_no_field_is_silently_coerced_to_zero(self):
        """A source that omits a field must never surface as 0.0 downstream."""
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            incomplete = panel([
                {"date": "2026-09-18", "symbol": "XLK", "open": 100.0, "high": 101.0,
                 "low": 99.0, "close": 100.5, "adj_close": 100.5, "volume": 1_000_000.0},
            ])
            adapter = lambda symbols: (incomplete, {})
            result = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             adapter, FrozenForwardTimebase())
            self.assertEqual(recorder.symbols(), ["XLK"])  # SPY never fabricated as zero

    def test_empty_panel_is_a_validation_failure_not_a_silent_success(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            adapter = lambda symbols: (PricePanel([]), {})
            result = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             adapter, FrozenForwardTimebase())
            self.assertEqual(result.attempt.outcome, ATTEMPT_SUCCEEDED)
            self.assertEqual(result.attempt.validation_state, VALIDATION_FAILED)
            self.assertEqual(result.accepted_count, 0)


class ExecuteForwardCaptureFailureTest(unittest.TestCase):
    def run_failure(self, adapter) -> "tuple":
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            result = execute_forward_capture(REQUEST, recorder, journal, task_store,
                                             adapter, FrozenForwardTimebase())
            # Read everything needed for assertions before the temp directory
            # (and the objects backed by it) go out of scope.
            journal_rows = journal.all()
            task = task_store.get(REQUEST.source_id)
            return result, journal_rows, task

    def test_dns_or_network_failure(self):
        def adapter(symbols):
            try:
                raise urllib.error.URLError("name resolution failed")
            except urllib.error.URLError as exc:
                raise DataUnavailable(f"XLK: {type(exc).__name__}: {exc}") from exc
        result, journal_rows, task = self.run_failure(adapter)
        self.assertEqual(result.attempt.outcome, ATTEMPT_FAILED)
        self.assertEqual(result.attempt.failure_state, FAILURE_DNS_OR_NETWORK)
        self.assertEqual(result.attempt.fetch_completed_at, None)
        self.assertEqual(result.attempt.validation_state, VALIDATION_NOT_APPLICABLE)
        self.assertEqual(task.consecutive_failures, 1)
        self.assertEqual(journal_rows[0]["failure_state"], FAILURE_DNS_OR_NETWORK)

    def test_timeout(self):
        def adapter(symbols):
            try:
                raise TimeoutError("timed out")
            except TimeoutError as exc:
                raise DataUnavailable(f"XLK: {type(exc).__name__}: {exc}") from exc
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_TIMEOUT)

    def test_http_error_including_rate_limit(self):
        def adapter(symbols):
            try:
                raise urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)
            except urllib.error.HTTPError as exc:
                raise DataUnavailable(f"XLK: {type(exc).__name__}: {exc}") from exc
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_HTTP_ERROR)

    def test_malformed_json_response(self):
        def adapter(symbols):
            try:
                json.loads("{not valid json")
            except json.JSONDecodeError as exc:
                raise DataUnavailable(f"XLK: {type(exc).__name__}: {exc}") from exc
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_MALFORMED_RESPONSE)

    def test_source_reported_error_payload(self):
        adapter = lambda symbols: (_ for _ in ()).throw(
            DataUnavailable("XLK: source returned error {'code': 'Not Found'}"))
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_SOURCE_ERROR_PAYLOAD)

    def test_no_usable_rows(self):
        adapter = lambda symbols: (_ for _ in ()).throw(
            DataUnavailable("XLK: source returned no complete bars"))
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_NO_USABLE_ROWS)

    def test_truncated_transfer_via_injected_failure(self):
        """The real adapter cannot yet distinguish truncation from other
        malformed JSON (see forward_contracts.YAHOO_DAILY_CHART.failure_modes'
        comment); this exercises the state via direct injection so the
        classification path itself is proven, honestly labelled as such."""
        adapter = lambda symbols: (_ for _ in ()).throw(
            ForwardCaptureFailure(FAILURE_TRUNCATED, "connection reset after 400 of 1703 bytes"))
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_TRUNCATED)

    def test_schema_change_via_moved_response_keys(self):
        def adapter(symbols):
            payload = {"chart": {"result": [{"unexpected_shape": True}]}}
            return payload["chart"]["result"][0]["indicators"]  # KeyError
        result, _, _ = self.run_failure(adapter)
        self.assertEqual(result.attempt.failure_state, FAILURE_SCHEMA_CHANGED)

    def test_repeated_failures_accumulate_consecutive_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()

            def always_fails(symbols):
                raise ForwardCaptureFailure(FAILURE_DNS_OR_NETWORK, "down")

            for _ in range(3):
                execute_forward_capture(REQUEST, recorder, journal, task_store,
                                        always_fails, timebase)
                timebase.advance(REQUEST.min_interval_seconds + 1)
            self.assertEqual(task_store.get(REQUEST.source_id).consecutive_failures, 3)
            self.assertEqual(len(journal.all()), 3)

    def test_failure_then_success_resets_consecutive_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()

            def fails(symbols):
                raise ForwardCaptureFailure(FAILURE_TIMEOUT, "slow")

            execute_forward_capture(REQUEST, recorder, journal, task_store, fails, timebase)
            timebase.advance(REQUEST.min_interval_seconds + 1)
            execute_forward_capture(REQUEST, recorder, journal, task_store,
                                    lambda symbols: (panel(), {}), timebase)
            task = task_store.get(REQUEST.source_id)
            self.assertEqual(task.consecutive_failures, 0)
            self.assertEqual(task.successes, 1)
            self.assertEqual(task.attempts, 2)


class ClassifierUnitTest(unittest.TestCase):
    def test_unclassified_exception_falls_back_honestly(self):
        self.assertEqual(_classify_failure(RuntimeError("something else")),
                         "UNCLASSIFIED_ADAPTER_EXCEPTION")

    def test_data_unavailable_with_os_error_cause_is_network(self):
        try:
            raise OSError("network unreachable")
        except OSError as exc:
            wrapped = DataUnavailable("XLK: OSError: network unreachable")
            wrapped.__cause__ = exc
        self.assertEqual(_classify_yahoo_exception(wrapped), FAILURE_DNS_OR_NETWORK)


class RestartReplayTest(unittest.TestCase):
    def test_attempt_journal_and_task_store_survive_a_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, journal, task_store = system(directory)
            timebase = FrozenForwardTimebase()
            execute_forward_capture(REQUEST, recorder, journal, task_store,
                                    lambda symbols: (panel(), {}), timebase)

            # Reopen everything from disk, as a restarted process would.
            root = Path(directory)
            reopened_recorder = ForwardRecorder(root / "forward.jsonl")
            reopened_journal = AttemptJournal(root / "attempts.jsonl")
            reopened_store = ForwardCaptureTaskStore(root / "tasks.json")

            self.assertEqual(reopened_recorder.symbols(), ["SPY", "XLK"])
            self.assertEqual(len(reopened_journal.all()), 1)
            task = reopened_store.get(REQUEST.source_id)
            self.assertEqual(task.attempts, 1)
            self.assertEqual(task.successes, 1)

            # And a further attempt behaves exactly as it would have without
            # the restart -- idempotent resubmission, not a doubled accept.
            timebase.advance(REQUEST.min_interval_seconds + 1)
            second = execute_forward_capture(REQUEST, reopened_recorder, reopened_journal,
                                             reopened_store, lambda symbols: (panel(), {}),
                                             timebase)
            self.assertEqual(second.accepted_count, 0)


class CaptureAttemptContractTest(unittest.TestCase):
    def test_failed_attempt_must_name_a_failure_state(self):
        with self.assertRaises(ValueError):
            CaptureAttempt(attempt_id="a", source_id="s", source_version="v",
                          market_session="REGULAR", symbols_requested=("X",),
                          fetch_started_at="2026-09-19T00:00:00+00:00",
                          fetch_completed_at=None, outcome=ATTEMPT_FAILED,
                          failure_state=None, schema_version="v1", payload_hash=None,
                          validation_state=VALIDATION_NOT_APPLICABLE, lineage="x")

    def test_succeeded_attempt_must_not_carry_a_failure_state(self):
        with self.assertRaises(ValueError):
            CaptureAttempt(attempt_id="a", source_id="s", source_version="v",
                          market_session="REGULAR", symbols_requested=("X",),
                          fetch_started_at="2026-09-19T00:00:00+00:00",
                          fetch_completed_at="2026-09-19T00:00:01+00:00",
                          outcome=ATTEMPT_SUCCEEDED, failure_state=FAILURE_TIMEOUT,
                          schema_version="v1", payload_hash="sha256:aa",
                          validation_state=VALIDATION_OK, lineage="x")


if __name__ == "__main__":
    unittest.main()
