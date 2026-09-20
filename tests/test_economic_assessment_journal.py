"""The durable economic assessment journal (mission item 4).

Covers exactly the mission's named test list for this component: torn
append, duplicate append, restart, same-id conflict, and the
crash-after-assessment-before-Desk replay guarantee.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import economics_fixtures as fixtures
from quant.economics import (AssessmentConflict, AssessmentRecord, EconomicAssessmentJournal,
                             PortfolioInteraction, compute_input_fingerprint, economic_gate)
from quant.economics.decision import EffectEstimate
from quant.economics.journal import RECORD_ACCEPTED, RECORD_CONFLICT
from quant.economics.states import CLUSTERING_UNIT_O4_RESOLVED, CONTINUE


def _verdict_and_result():
    theta = fixtures.theta_state()
    meue_result = fixtures.meue_recipe().evaluate(theta)
    estimate = EffectEstimate(delta_hat=0.05, lower=0.04, upper=0.06, confidence_level=0.95,
                              evidence_label="DEVELOPMENT", sample_provenance="SYNTHETIC_FIXTURE",
                              clustering_unit_provenance=CLUSTERING_UNIT_O4_RESOLVED)
    interaction = PortfolioInteraction(overlap_fraction=0.0, residual_beta=0.0)
    verdict = economic_gate(estimate, meue_result, theta, interaction)
    return estimate, meue_result, theta, interaction, verdict


def _record(assessment_id="EA-1", **overrides) -> AssessmentRecord:
    estimate, meue_result, theta, interaction, verdict = _verdict_and_result()
    fingerprint = overrides.pop("input_fingerprint", None) or compute_input_fingerprint(
        estimate, meue_result, theta, interaction)
    return AssessmentRecord.from_verdict(assessment_id, fingerprint, verdict, meue_result,
                                        **overrides)


class AssessmentRecordTest(unittest.TestCase):
    def test_from_verdict_carries_the_mission_named_fields(self):
        record = _record(effect_version="peer_lead_lag@v3", parameter_provenance="sha256:params",
                         cost_scenario="s_1_opening_regime_worse", capacity_state="POLICY_UNCHANGED",
                         portfolio_context_ref="BOOK_SNAPSHOT_2026-09-19", code_sha="abc123",
                         protocol_hash="sha256:protocol")
        document = record.to_dict()
        for field_name in ("assessment_id", "input_fingerprint", "effect_version",
                          "recipe_version", "parameter_provenance", "cost_scenario",
                          "capacity_state", "portfolio_context_ref", "decision", "reason_codes",
                          "recorded_at", "code_sha", "protocol_hash"):
            self.assertIn(field_name, document)
        self.assertEqual(document["decision"], CONTINUE)
        self.assertTrue(document["recipe_version"])  # real recipe_hash, not fabricated


class EconomicAssessmentJournalTest(unittest.TestCase):
    def test_duplicate_append_same_fingerprint_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            journal = EconomicAssessmentJournal(path)
            record = _record()
            self.assertEqual(journal.record(record), RECORD_ACCEPTED)
            self.assertEqual(journal.record(record), RECORD_ACCEPTED)  # duplicate, same input
            self.assertEqual(len(path.read_text().strip().splitlines()), 1)
            self.assertEqual(len(journal), 1)

    def test_same_id_different_fingerprint_is_a_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            journal = EconomicAssessmentJournal(path)
            first = _record(input_fingerprint="sha256:aaa")
            second = _record(input_fingerprint="sha256:bbb")
            journal.record(first)
            with self.assertRaises(AssessmentConflict) as caught:
                journal.record(second)
            self.assertEqual(caught.exception.assessment_id, "EA-1")
            self.assertEqual(caught.exception.existing_fingerprint, "sha256:aaa")
            self.assertEqual(caught.exception.new_fingerprint, "sha256:bbb")
            # The original accepted decision is never overwritten by the conflict.
            self.assertEqual(journal.get("EA-1")["input_fingerprint"], "sha256:aaa")
            lines = path.read_text().strip().splitlines()
            self.assertEqual(len(lines), 2)  # the accepted record, plus one conflict audit line
            self.assertIn(RECORD_CONFLICT, lines[1])

    def test_restart_reaches_the_same_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            first = EconomicAssessmentJournal(path)
            record = _record()
            first.record(record)
            reopened = EconomicAssessmentJournal(path)
            self.assertEqual(reopened.get("EA-1")["input_fingerprint"], record.input_fingerprint)
            self.assertEqual(len(reopened), 1)
            # A post-restart repeat with identical inputs is still idempotent.
            self.assertEqual(reopened.record(record), RECORD_ACCEPTED)
            self.assertEqual(len(path.read_text().strip().splitlines()), 1)

    def test_crash_after_assessment_before_desk_replays_the_same_state(self):
        """The exact scenario the mission names: kill the process right after
        the assessment is journaled, before Desk ever sees it. Replay must
        reach the identical decision — never re-derive it, never lose it."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            live = EconomicAssessmentJournal(path)
            record = _record(portfolio_context_ref="BOOK_SNAPSHOT_PRE_CRASH")
            live.record(record)
            # Simulate the crash: no clean shutdown, just a fresh process
            # opening the same file.
            del live
            recovered = EconomicAssessmentJournal(path)
            recovered_record = recovered.get("EA-1")
            self.assertIsNotNone(recovered_record)
            self.assertEqual(recovered_record["decision"], record.decision)
            self.assertEqual(recovered_record["capital_order_eligibility"],
                             record.capital_order_eligibility)
            self.assertEqual(recovered_record["input_fingerprint"], record.input_fingerprint)
            self.assertEqual(recovered_record["portfolio_context_ref"], "BOOK_SNAPSHOT_PRE_CRASH")
            self.assertEqual(recovered.replay(), recovered._by_id)

    def test_torn_final_append_is_recovered_not_duplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessments.jsonl"
            journal = EconomicAssessmentJournal(path)
            journal.record(_record("EA-1"))
            with path.open("a", encoding="utf-8") as handle:
                handle.write('{"assessment_id": "EA-2", "state": "ASSESSMENT_RECORDED"')  # no \n
            reopened = EconomicAssessmentJournal(path)
            self.assertEqual(len(reopened), 1)  # the torn EA-2 tail never counted
            reopened.record(_record("EA-2"))
            self.assertEqual(len(reopened), 2)
            self.assertEqual(len(reopened.replay()), 2)

    def test_fingerprint_changes_when_a_real_input_changes(self):
        estimate, meue_result, theta, interaction, _ = _verdict_and_result()
        base = compute_input_fingerprint(estimate, meue_result, theta, interaction)
        from dataclasses import replace
        moved = compute_input_fingerprint(replace(estimate, delta_hat=0.09), meue_result, theta,
                                          interaction)
        self.assertNotEqual(base, moved)

    def test_fingerprint_is_stable_for_identical_inputs(self):
        estimate, meue_result, theta, interaction, _ = _verdict_and_result()
        first = compute_input_fingerprint(estimate, meue_result, theta, interaction)
        second = compute_input_fingerprint(estimate, meue_result, theta, interaction)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
