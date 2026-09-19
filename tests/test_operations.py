"""Operational failures, readiness gates, decay monitoring and evidence provenance.

The tests worth reading are the refusals: a stale quote cannot mark a position, a
missing bar cannot become a decision, a restart cannot resubmit an order, an
outage cannot be resolved by assuming a fill, and a retirement rule cannot be
written after the window it judges.
"""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from quant.operations import (EvidenceRecord, EvidenceRegistry, FailureInjection, Gate,
                              MonitoringWindow, OrderIntent, OrderSubmissionLedger,
                              RetirementRule, assess_readiness, check_bar, check_quote,
                              coverage_report, monitor)
from quant.operations.failures import (BAR_HALTED, BAR_MISSING, BAR_PRESENT,
                                       FAILURE_MODES, FILL_ACCEPTED,
                                       FILL_DUPLICATE_IGNORED, FILL_OVERFILL_REFUSED,
                                       FILL_UNKNOWN_ORDER, ORDER_DUPLICATE_SUPPRESSED,
                                       ORDER_RESERVED, ORDER_SENT,
                                       ORDER_UNKNOWN_AFTER_OUTAGE, QUOTE_FRESH,
                                       QUOTE_STALE, QUOTE_TIMESTAMP_MISSING)
from quant.operations.monitoring import (MONITOR_DRIFTING, MONITOR_RETIRE,
                                         MONITOR_UNRESOLVED, MONITOR_WITHIN_TOLERANCE,
                                         RULE_DECLARED_TOO_LATE)
from quant.operations.readiness import (GATE_CAPACITY, GATE_ECONOMIC, GATE_MONITORING,
                                        GATE_OPERATIONAL, GATE_SATISFIED,
                                        GATE_STATISTICAL, GATE_UNRESOLVED,
                                        GATE_UNSATISFIED, GATES, NOT_READY,
                                        PAPER_SHADOW_READY)
from quant.operations.registry import (RECORD_ACCEPTED, RECORD_DUPLICATE,
                                       RECORD_INCOMPLETE)


def joined(problems) -> str:
    return " | ".join(problems)


class QuoteAndBarTest(unittest.TestCase):
    def test_fresh_quote_is_usable(self):
        check = check_quote("2026-09-18T20:00:00+00:00", "2026-09-18T20:01:00+00:00")
        self.assertEqual(check.state, QUOTE_FRESH)
        self.assertTrue(check.usable)

    def test_old_quote_cannot_mark_a_position(self):
        check = check_quote("2026-09-18T18:00:00+00:00", "2026-09-18T20:01:00+00:00")
        self.assertEqual(check.state, QUOTE_STALE)
        self.assertFalse(check.usable)

    def test_quote_from_the_future_is_stale_too(self):
        check = check_quote("2026-09-18T21:00:00+00:00", "2026-09-18T20:00:00+00:00")
        self.assertEqual(check.state, QUOTE_STALE)
        self.assertIn("ahead of the valuation instant", check.detail)

    def test_quote_without_a_timestamp_cannot_be_shown_fresh(self):
        self.assertEqual(check_quote(None, "2026-09-18T20:00:00+00:00").state,
                         QUOTE_TIMESTAMP_MISSING)

    def test_complete_bar_is_present(self):
        self.assertEqual(check_bar({"open": 1.0, "close": 1.1, "volume": 100.0}),
                         BAR_PRESENT)

    def test_missing_bar_blocks_the_decision(self):
        self.assertEqual(check_bar(None), BAR_MISSING)
        self.assertEqual(check_bar({"open": 1.0, "close": None, "volume": 10.0}),
                         BAR_MISSING)

    def test_nan_price_is_a_missing_bar(self):
        self.assertEqual(check_bar({"open": float("nan"), "close": 1.0, "volume": 5.0}),
                         BAR_MISSING)

    def test_halt_blocks_the_decision_even_with_a_bar(self):
        self.assertEqual(check_bar({"open": 1.0, "close": 1.0, "volume": 1.0}, halted=True),
                         BAR_HALTED)


class OrderLedgerTest(unittest.TestCase):
    def intent(self, order_id: str = "COID-1", quantity: float = 100.0) -> OrderIntent:
        return OrderIntent(client_order_id=order_id, symbol="AAA", quantity=quantity,
                           strategy_id="S1", session_date="2026-09-18")

    def test_reservation_is_written_before_the_order_is_sent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.jsonl"
            ledger = OrderSubmissionLedger(path)
            self.assertEqual(ledger.reserve(self.intent()).state, ORDER_RESERVED)
            # The reservation is durable even though nothing was sent yet.
            self.assertIn(ORDER_RESERVED, path.read_text())
            self.assertEqual(ledger.mark_sent("COID-1"), ORDER_SENT)

    def test_restart_after_a_crash_does_not_resubmit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.jsonl"
            first = OrderSubmissionLedger(path)
            first.reserve(self.intent())
            # Crash here: reserved, never marked sent.
            reopened = OrderSubmissionLedger(path)
            self.assertEqual(reopened.reserve(self.intent()).state,
                             ORDER_DUPLICATE_SUPPRESSED)

    def test_marking_sent_twice_is_suppressed(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            ledger.mark_sent("COID-1")
            self.assertEqual(ledger.mark_sent("COID-1"), ORDER_DUPLICATE_SUPPRESSED)

    def test_sending_an_unreserved_order_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            self.assertEqual(ledger.mark_sent("GHOST"), "ORDER_NOT_RESERVED")

    def test_partial_fills_accumulate(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            self.assertEqual(ledger.record_fill("COID-1", "F1", 40.0), FILL_ACCEPTED)
            self.assertEqual(ledger.record_fill("COID-1", "F2", 60.0), FILL_ACCEPTED)
            self.assertAlmostEqual(ledger.filled_quantity("COID-1"), 100.0, places=9)
            self.assertAlmostEqual(ledger.outstanding("COID-1"), 0.0, places=9)

    def test_duplicate_fill_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            ledger.record_fill("COID-1", "F1", 40.0)
            self.assertEqual(ledger.record_fill("COID-1", "F1", 40.0),
                             FILL_DUPLICATE_IGNORED)
            self.assertAlmostEqual(ledger.filled_quantity("COID-1"), 40.0, places=9)

    def test_overfill_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            ledger.record_fill("COID-1", "F1", 90.0)
            self.assertEqual(ledger.record_fill("COID-1", "F2", 20.0),
                             FILL_OVERFILL_REFUSED)

    def test_fill_for_an_unknown_order_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            self.assertEqual(ledger.record_fill("GHOST", "F1", 10.0), FILL_UNKNOWN_ORDER)

    def test_fills_replay_to_the_same_quantity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.jsonl"
            ledger = OrderSubmissionLedger(path)
            ledger.reserve(self.intent())
            ledger.record_fill("COID-1", "F1", 30.0)
            ledger.record_fill("COID-1", "F2", 30.0)
            reopened = OrderSubmissionLedger(path)
            self.assertAlmostEqual(reopened.filled_quantity("COID-1"), 60.0, places=9)
            self.assertEqual(reopened.record_fill("COID-1", "F1", 30.0),
                             FILL_DUPLICATE_IGNORED)

    def test_unreachable_broker_yields_unknown_not_a_guess(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            ledger.mark_sent("COID-1")
            report = ledger.reconcile(None)
            self.assertFalse(report["broker_reachable"])
            self.assertEqual(report["unknown"], 1)
            self.assertEqual(report["orders"][0]["state"], ORDER_UNKNOWN_AFTER_OUTAGE)

    def test_reconciliation_detects_a_fill_quantity_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent())
            ledger.mark_sent("COID-1")
            ledger.record_fill("COID-1", "F1", 40.0)
            report = ledger.reconcile({"COID-1": {"filled_quantity": 100.0}})
            self.assertEqual(report["mismatches"], 1)

    def test_reconciliation_distinguishes_never_sent_from_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            ledger.reserve(self.intent("COID-A"))
            ledger.reserve(self.intent("COID-B"))
            ledger.mark_sent("COID-B")
            report = ledger.reconcile({})
            states = {row["client_order_id"]: row["state"] for row in report["orders"]}
            self.assertEqual(states["COID-A"], "ORDER_NEVER_SENT")
            self.assertEqual(states["COID-B"], "ORDER_UNKNOWN_TO_BROKER")

    def test_zero_quantity_intent_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = OrderSubmissionLedger(Path(directory) / "orders.jsonl")
            outcome = ledger.reserve(self.intent(quantity=0.0))
            self.assertEqual(outcome.state, "ORDER_INTENT_INVALID")
            self.assertIn("ZERO_QUANTITY_ORDER", outcome.detail)

    def test_failure_mode_coverage_names_what_is_missing(self):
        scenarios = [FailureInjection(mode, f"scenario for {mode}", "REFUSED")
                     for mode in FAILURE_MODES[:3]]
        report = coverage_report(scenarios)
        self.assertFalse(report["complete"])
        self.assertIn("BROKER_OUTAGE", report["missing"])

    def test_full_coverage_is_reported_complete(self):
        scenarios = [FailureInjection(mode, f"scenario for {mode}", "REFUSED")
                     for mode in FAILURE_MODES]
        self.assertTrue(coverage_report(scenarios)["complete"])


class ReadinessTest(unittest.TestCase):
    def gates(self, **states) -> list[Gate]:
        return [Gate(name, states.get(name, GATE_SATISFIED), "evidence",
                     f"artifact://{name}") for name in GATES]

    def test_all_gates_satisfied_reaches_paper_shadow_ready(self):
        verdict = assess_readiness("LANE_1", self.gates())
        self.assertEqual(verdict.state, PAPER_SHADOW_READY)
        self.assertTrue(verdict.ready_for_paper_shadow)

    def test_readiness_never_authorises_real_capital(self):
        verdict = assess_readiness("LANE_1", self.gates())
        self.assertEqual(verdict.capital_authority, "PAPER_SHADOW_ONLY")
        self.assertFalse(verdict.to_dict()["real_capital_authorized"])

    def test_the_weakest_gate_is_reported_not_an_average(self):
        verdict = assess_readiness("LANE_1", self.gates(**{GATE_CAPACITY: GATE_UNSATISFIED}))
        self.assertEqual(verdict.state, NOT_READY)
        self.assertEqual(verdict.binding_gate, GATE_CAPACITY)

    def test_an_unassessed_gate_is_missing_not_passed(self):
        gates = [gate for gate in self.gates() if gate.name != GATE_MONITORING]
        verdict = assess_readiness("LANE_1", gates)
        self.assertEqual(verdict.state, NOT_READY)
        self.assertIn("GATE_NOT_ASSESSED", joined(verdict.violations))

    def test_satisfied_gate_requires_an_evidence_reference(self):
        gates = self.gates()
        gates[0] = replace(gates[0], evidence_reference="")
        verdict = assess_readiness("LANE_1", gates)
        self.assertIn("SATISFIED_GATE_WITHOUT_EVIDENCE_REFERENCE", joined(verdict.violations))

    def test_unresolved_gate_blocks_readiness(self):
        verdict = assess_readiness("LANE_1",
                                   self.gates(**{GATE_STATISTICAL: GATE_UNRESOLVED}))
        self.assertEqual(verdict.state, NOT_READY)
        self.assertEqual(verdict.binding_gate, GATE_STATISTICAL)

    def test_statistics_cannot_compensate_for_economics(self):
        verdict = assess_readiness("LANE_1", self.gates(**{GATE_ECONOMIC: GATE_UNSATISFIED}))
        self.assertEqual(verdict.binding_gate, GATE_ECONOMIC)
        self.assertEqual(verdict.state, NOT_READY)

    def test_duplicate_gate_declaration_is_refused(self):
        gates = self.gates() + [Gate(GATE_OPERATIONAL, GATE_SATISFIED, "again", "ref")]
        self.assertIn("DUPLICATE_GATE_DECLARED",
                      joined(assess_readiness("LANE_1", gates).violations))


class MonitoringTest(unittest.TestCase):
    def rule(self, **overrides) -> RetirementRule:
        fields = dict(rule_id="RETIRE_V1", declared_at="2026-09-01T00:00:00+00:00",
                      breach_floor=0.0, consecutive_breaches=3,
                      friction_drift_limit_bps=2.0)
        fields.update(overrides)
        return RetirementRule(**fields)

    def windows(self, effects, frictions=None) -> list[MonitoringWindow]:
        return [MonitoringWindow(f"W{index}", f"2026-10-{index + 1:02d}T00:00:00+00:00",
                                 effect,
                                 None if frictions is None else frictions[index])
                for index, effect in enumerate(effects)]

    def test_all_windows_above_the_floor_are_within_tolerance(self):
        verdict = monitor(self.rule(), self.windows([0.01, 0.02, 0.005]))
        self.assertEqual(verdict.state, MONITOR_WITHIN_TOLERANCE)
        self.assertEqual(verdict.trailing_breaches, 0)

    def test_consecutive_breaches_trigger_retirement(self):
        verdict = monitor(self.rule(), self.windows([0.01, -0.01, -0.02, -0.03]))
        self.assertEqual(verdict.state, MONITOR_RETIRE)
        self.assertTrue(verdict.retire)
        self.assertEqual(verdict.trailing_breaches, 3)

    def test_non_consecutive_breaches_drift_without_retiring(self):
        verdict = monitor(self.rule(), self.windows([-0.01, 0.02, -0.01, 0.03]))
        self.assertEqual(verdict.state, MONITOR_DRIFTING)
        self.assertEqual(verdict.trailing_breaches, 0)

    def test_a_rule_declared_after_the_first_window_is_refused(self):
        verdict = monitor(self.rule(declared_at="2026-10-05T00:00:00+00:00"),
                          self.windows([-0.01, -0.02, -0.03]))
        self.assertEqual(verdict.state, MONITOR_UNRESOLVED)
        self.assertIn(RULE_DECLARED_TOO_LATE, joined(verdict.violations))

    def test_friction_drift_above_the_limit_is_drift(self):
        verdict = monitor(self.rule(), self.windows([0.01, 0.02, 0.03], [8.0, 9.0, 10.0]),
                          expected_friction_bps=5.0)
        self.assertEqual(verdict.state, MONITOR_DRIFTING)
        self.assertAlmostEqual(verdict.friction_drift, 4.0, places=9)

    def test_no_windows_is_unresolved(self):
        verdict = monitor(self.rule(), [])
        self.assertEqual(verdict.state, MONITOR_UNRESOLVED)
        self.assertIn("NO_MONITORING_WINDOWS", joined(verdict.violations))

    def test_zero_consecutive_breaches_is_an_invalid_rule(self):
        verdict = monitor(self.rule(consecutive_breaches=0), self.windows([0.01]))
        self.assertEqual(verdict.state, MONITOR_UNRESOLVED)
        self.assertIn("CONSECUTIVE_BREACHES_MUST_BE_POSITIVE", joined(verdict.violations))


class EvidenceRegistryTest(unittest.TestCase):
    def record(self, **overrides) -> EvidenceRecord:
        fields = dict(evidence_id="E1", dataset_version="panel@sha256:aaaa",
                      protocol_hash="sha256:bbbb", code_sha="3ba24cea",
                      result_summary="net effect 12 bps, interval [4, 20] bps",
                      decision="CONTINUE", label="DEVELOPMENT")
        fields.update(overrides)
        return EvidenceRecord(**fields)

    def test_a_complete_chain_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            self.assertEqual(registry.record(self.record()), RECORD_ACCEPTED)
            self.assertEqual(len(registry), 1)

    def test_a_broken_chain_is_refused_and_journaled(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            self.assertEqual(registry.record(self.record(code_sha="")), RECORD_INCOMPLETE)
            self.assertEqual(len(registry), 0)
            self.assertEqual(len(registry.incomplete()), 1)

    def test_the_same_chain_is_not_recorded_twice(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            registry.record(self.record())
            self.assertEqual(registry.record(self.record(evidence_id="E2")),
                             RECORD_DUPLICATE)

    def test_a_changed_code_sha_is_a_different_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            registry.record(self.record())
            self.assertEqual(registry.record(self.record(evidence_id="E2",
                                                        code_sha="deadbeef")),
                             RECORD_ACCEPTED)

    def test_registry_survives_a_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            EvidenceRegistry(path).record(self.record())
            reopened = EvidenceRegistry(path)
            self.assertEqual(reopened.record(self.record()), RECORD_DUPLICATE)
            self.assertIsNotNone(reopened.get("E1"))

    def test_unrecognised_label_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            self.assertEqual(registry.record(self.record(label="PROVEN")),
                             RECORD_INCOMPLETE)

    def test_citations_and_confirmations_can_be_listed(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = EvidenceRegistry(Path(directory) / "evidence.jsonl")
            registry.record(self.record())
            registry.record(self.record(evidence_id="E2", label="FORWARD_CONFIRMATION",
                                       protocol_hash="sha256:cccc"))
            self.assertEqual(len(registry.citations_for("CONTINUE")), 2)
            self.assertEqual(len(registry.confirmation_records()), 1)


if __name__ == "__main__":
    unittest.main()
