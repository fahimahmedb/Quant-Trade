from __future__ import annotations

import inspect
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Mapping

from quant.economics.coordinate import DeltaCoordinateBinding
from quant.economics.decision import EVIDENCE_DEVELOPMENT
from quant.science.effect import (
    ALLOCATION_CONSTRUCTOR_ID,
    COHORT_GAP_VIOLATION,
    CONCENTRATION_GUARD_FAILED,
    COHORT_ACCRUAL_AFTER_STRUCTURAL_STOP,
    CONFIRMATORY_LOOK_ALREADY_CONSUMED,
    DEPENDENCE_MODEL_UNSUPPORTED,
    D19_INSUFFICIENT,
    EFFECT_UNAVAILABLE,
    FIFTH_COHORT_REFUSED,
    INSUFFICIENT_G,
    INTER_COHORT_SEPARATION,
    PROTOCOL_ID,
    STRUCTURAL_CONTINUE,
    STRUCTURAL_INFERENCE_ELIGIBLE,
    STRUCTURAL_INSUFFICIENT,
    AllocationCandidate,
    CohortProtocolStore,
    ForwardConfirmationReceipt,
    CohortRecord,
    MethodQualificationStore,
    ProtocolConfig,
    ProtocolConflict,
    StructuralEvent,
    assemble_form4_effect,
    build_delta_coordinate_binding,
    commit_reference_allocations,
    connected_components,
    one_look_signature_proof,
    qualify_method,
    scientific_sample_id,
    sign_flip_interval,
    structural_stopping_decision,
)
from quant.science.formation import SessionCalendar


class ExplodingOutcomes(Mapping[str, float]):
    def __getitem__(self, key: str) -> float:
        raise AssertionError("target outcome was read before the lawful look")

    def __iter__(self):
        raise AssertionError("target outcomes were iterated before the lawful look")

    def __len__(self) -> int:
        raise AssertionError("target outcome length was read before the lawful look")

    def __contains__(self, key: object) -> bool:
        raise AssertionError("target outcome membership was read before the lawful look")


class FirstVerticalScientificEffectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calendar = SessionCalendar(tuple(f"S{i:04d}" for i in range(2200)))
        self.config = ProtocolConfig()
        self.starts = (100, 431, 762, 1093)

    def _event(
        self, cohort_ordinal: int, number: int, entry_index: int,
        *, issuer: str | None = None, weight: float = 100.0,
        d19_complete: bool = True,
    ) -> StructuralEvent:
        event_id = f"c{cohort_ordinal}-e{number}"
        return StructuralEvent(
            event_id=event_id,
            issuer_cik=issuer or f"issuer-{cohort_ordinal}-{number}",
            security_id=f"security-{cohort_ordinal}-{number}",
            crossing_id=f"crossing-{cohort_ordinal}-{number}",
            entry_session=self.calendar.at(entry_index),
            scheduled_exit_session=self.calendar.at(entry_index + 19),
            allocation_weight=weight,
            adv20_usd=max(100_000.0, weight / 0.001),
            allocation_slot=number % 20,
            allocation_reason="POSITIVE_REFERENCE_ALLOCATION",
            allocation_commitment_hash=f"commit-{event_id}",
            content_addresses=(f"sha256:{event_id}",),
            d19_complete=d19_complete,
        )

    def _cohort(
        self, ordinal: int, *, event_offsets=(0, 80, 160, 240),
        matured: bool = True,
    ) -> CohortRecord:
        start = self.starts[ordinal - 1]
        events = tuple(
            self._event(ordinal, number, start + offset)
            for number, offset in enumerate(event_offsets)
        )
        return CohortRecord(
            cohort_id=f"cohort-{ordinal}",
            ordinal=ordinal,
            first_entry_session=self.calendar.at(start),
            last_entry_session=self.calendar.at(start + 251),
            matured=matured,
            protocol_hash=self.config.protocol_hash,
            events=events,
            source_manifest_hash=f"manifest-{ordinal}",
        )

    def _eligible_cohorts(self):
        return (self._cohort(1), self._cohort(2), self._cohort(3))

    def test_protocol_geometry_is_frozen_and_hash_addressed(self):
        self.assertEqual(PROTOCOL_ID, "FORM4_FIRST_VERTICAL_MULTI_COHORT_V1")
        self.assertEqual(self.config.entry_sessions_per_cohort, 252)
        self.assertEqual(self.config.k_max, 4)
        self.assertEqual(self.config.inter_cohort_separation, 80)
        self.assertEqual(self.config.g_min, 10)
        self.assertTrue(self.config.protocol_hash.startswith("sha256:"))
        self.assertTrue(
            ALLOCATION_CONSTRUCTOR_ID.startswith("FORM4_SLOT20_ADV20_V1:sha256:")
        )

    def test_reference_allocation_is_pre_outcome_and_enforces_active_issuer_slot(self):
        signature = inspect.signature(commit_reference_allocations)
        self.assertNotIn("outcomes", signature.parameters)
        candidates = (
            AllocationCandidate("a", "issuer-x", "sec-x", "cross-a", "S0100", 100_000.0),
            AllocationCandidate("b", "issuer-x", "sec-x", "cross-b", "S0105", 100_000.0),
            AllocationCandidate("c", "issuer-y", "sec-y", "cross-c", "S0106", 200_000.0),
        )
        events = commit_reference_allocations(candidates, self.calendar)
        self.assertEqual(events[0].allocation_weight, 100.0)
        self.assertEqual(events[1].allocation_weight, 0.0)
        self.assertEqual(events[1].allocation_reason, "ISSUER_ALREADY_HAS_ACTIVE_SLOT")
        self.assertEqual(events[2].allocation_weight, 200.0)
        self.assertTrue(all(
            event.allocation_commitment_hash.startswith("sha256:") for event in events
        ))

    def test_protocol_store_freezes_after_first_cohort(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            first = self._cohort(1)
            store.register_cohort(self.config, first, self.calendar)
            store.register_cohort(self.config, first, self.calendar)
            changed = ProtocolConfig(k_max=5)
            with self.assertRaises(ProtocolConflict):
                store.register_cohort(changed, self._cohort(2), self.calendar)

    def test_invalid_251_session_geometry_fails_closed(self):
        cohort = self._cohort(1)
        cohort = replace(
            cohort, last_entry_session=self.calendar.at(self.starts[0] + 250)
        )
        decision = structural_stopping_decision((cohort,), self.calendar)
        self.assertEqual(decision.state, STRUCTURAL_INSUFFICIENT)
        self.assertIn("COHORT_ENTRY_SESSION_GEOMETRY_NOT_252", decision.reasons)

    def test_protocol_hash_mismatch_fails_closed(self):
        cohort = replace(self._cohort(1), protocol_hash="sha256:not-the-frozen-protocol")
        decision = structural_stopping_decision((cohort,), self.calendar)
        self.assertEqual(decision.state, STRUCTURAL_INSUFFICIENT)
        self.assertIn("COHORT_PROTOCOL_HASH_MISMATCH", decision.reasons)

    def test_inter_cohort_gap_inside_80_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            first = self._cohort(1)
            store.register_cohort(self.config, first, self.calendar)
            start = self.starts[0] + 251 + INTER_COHORT_SEPARATION - 1
            bad = CohortRecord(
                cohort_id="cohort-2", ordinal=2,
                first_entry_session=self.calendar.at(start),
                last_entry_session=self.calendar.at(start + 251),
                matured=True, protocol_hash=self.config.protocol_hash,
                events=(self._event(2, 0, start),), source_manifest_hash="bad",
            )
            with self.assertRaisesRegex(ProtocolConflict, COHORT_GAP_VIOLATION):
                store.register_cohort(self.config, bad, self.calendar)

    def test_next_cohort_waits_for_previous_cohort_maturity(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            store.register_cohort(
                self.config, self._cohort(1, matured=False), self.calendar
            )
            with self.assertRaisesRegex(ProtocolConflict, "PRIOR_COHORT_NOT_FULLY_MATURED"):
                store.register_cohort(self.config, self._cohort(2), self.calendar)

    def test_valid_80_session_boundary_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            store.register_cohort(self.config, self._cohort(1), self.calendar)
            store.register_cohort(self.config, self._cohort(2), self.calendar)
            self.assertEqual(len(store.cohorts()), 2)

    def test_accrual_stops_once_structural_guard_is_reached(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            store.register_cohort(self.config, self._cohort(1), self.calendar)
            store.register_cohort(self.config, self._cohort(2), self.calendar)
            store.register_cohort(self.config, self._cohort(3), self.calendar)
            with self.assertRaisesRegex(
                ProtocolConflict, COHORT_ACCRUAL_AFTER_STRUCTURAL_STOP
            ):
                store.register_cohort(self.config, self._cohort(4), self.calendar)

    def test_cross_cohort_repeated_issuer_merges_components(self):
        first = self._cohort(1)
        second = self._cohort(2)
        repeated = replace(second.events[0], issuer_cik=first.events[0].issuer_cik)
        second = replace(second, events=(repeated,) + second.events[1:])
        assignments, exposures = connected_components((first, second), self.calendar)
        self.assertEqual(
            assignments[first.events[0].event_id], assignments[repeated.event_id]
        )
        self.assertEqual(len(exposures), 7)

    def test_structural_stopping_never_accepts_outcome_parameter(self):
        parameters = {
            name.lower()
            for name in inspect.signature(structural_stopping_decision).parameters
        }
        self.assertFalse(parameters & {"outcomes", "target_outcomes", "t_j", "returns"})
        self.assertTrue(one_look_signature_proof())

    def test_g_below_ten_continues_without_inference(self):
        one = structural_stopping_decision((self._cohort(1),), self.calendar)
        two = structural_stopping_decision(
            (self._cohort(1), self._cohort(2)), self.calendar
        )
        self.assertEqual(one.state, STRUCTURAL_CONTINUE)
        self.assertEqual(two.state, STRUCTURAL_CONTINUE)
        self.assertIn(INSUFFICIENT_G, one.reasons)
        self.assertIn(INSUFFICIENT_G, two.reasons)

    def test_pre_stop_assembler_does_not_read_target_outcomes(self):
        artifact = assemble_form4_effect(
            cohorts=(self._cohort(1), self._cohort(2)),
            calendar=self.calendar,
            outcomes=ExplodingOutcomes(),
            method_qualification=qualify_method(self.config),
        )
        self.assertEqual(artifact.status, "REFUSED")
        self.assertIn(INSUFFICIENT_G, artifact.reason_codes)

    def test_three_cohorts_reach_structural_guard(self):
        decision = structural_stopping_decision(self._eligible_cohorts(), self.calendar)
        self.assertEqual(decision.state, STRUCTURAL_INFERENCE_ELIGIBLE)
        self.assertEqual(decision.positive_exposure_components, 12)
        self.assertLessEqual(decision.max_component_exposure_share, 0.10)

    def test_kmax_exhaustion_below_guard_is_insufficient(self):
        sparse = tuple(
            self._cohort(i, event_offsets=(0, 160)) for i in range(1, 5)
        )
        decision = structural_stopping_decision(sparse, self.calendar)
        self.assertEqual(decision.state, STRUCTURAL_INSUFFICIENT)
        self.assertIn(INSUFFICIENT_G, decision.reasons)

    def test_fifth_cohort_is_refused(self):
        starts = list(self.starts) + [1424]
        cohorts = []
        for ordinal, start in enumerate(starts, 1):
            cohorts.append(CohortRecord(
                cohort_id=f"cohort-{ordinal}", ordinal=ordinal,
                first_entry_session=self.calendar.at(start),
                last_entry_session=self.calendar.at(start + 251),
                matured=True, protocol_hash=self.config.protocol_hash,
                events=(), source_manifest_hash=f"manifest-{ordinal}",
            ))
        decision = structural_stopping_decision(tuple(cohorts), self.calendar)
        self.assertEqual(decision.state, STRUCTURAL_INSUFFICIENT)
        self.assertIn(FIFTH_COHORT_REFUSED, decision.reasons)

    def test_concentration_above_ten_percent_refuses_guard(self):
        cohorts = list(self._eligible_cohorts())
        first_event = replace(
            cohorts[0].events[0], allocation_weight=300.0, adv20_usd=500_000.0
        )
        cohorts[0] = replace(
            cohorts[0], events=(first_event,) + cohorts[0].events[1:]
        )
        decision = structural_stopping_decision(tuple(cohorts), self.calendar)
        self.assertNotEqual(decision.state, STRUCTURAL_INFERENCE_ELIGIBLE)
        self.assertIn(CONCENTRATION_GUARD_FAILED, decision.reasons)

    def test_d19_refusal_happens_before_any_outcome_read(self):
        cohorts = list(self._eligible_cohorts())
        broken = replace(cohorts[0].events[0], d19_complete=False)
        cohorts[0] = replace(
            cohorts[0], events=(broken,) + cohorts[0].events[1:]
        )
        artifact = assemble_form4_effect(
            cohorts=tuple(cohorts), calendar=self.calendar,
            outcomes=ExplodingOutcomes(),
            method_qualification=qualify_method(self.config),
        )
        self.assertEqual(artifact.status, "REFUSED")
        self.assertIn(D19_INSUFFICIENT, artifact.reason_codes)

    def test_missing_method_qualification_refuses_before_outcome_read(self):
        artifact = assemble_form4_effect(
            cohorts=self._eligible_cohorts(), calendar=self.calendar,
            outcomes=ExplodingOutcomes(), method_qualification=None,
        )
        self.assertEqual(artifact.status, "REFUSED")
        self.assertIn(DEPENDENCE_MODEL_UNSUPPORTED, artifact.reason_codes)
        self.assertIn(EFFECT_UNAVAILABLE, artifact.reason_codes)

    def test_coordinate_unresolved_and_mismatch_refuse_before_outcome_read(self):
        qualification = qualify_method(self.config)
        unresolved = assemble_form4_effect(
            cohorts=self._eligible_cohorts(), calendar=self.calendar,
            outcomes=ExplodingOutcomes(), method_qualification=qualification,
            binding=DeltaCoordinateBinding(),
        )
        self.assertIn("DELTA_COORDINATE_UNRESOLVED", unresolved.reason_codes)

        mismatch = assemble_form4_effect(
            cohorts=self._eligible_cohorts(), calendar=self.calendar,
            outcomes=ExplodingOutcomes(), method_qualification=qualification,
            binding=build_delta_coordinate_binding(benchmark_symbol="QQQ"),
        )
        self.assertIn("DELTA_COORDINATE_MISMATCH", mismatch.reason_codes)

    def test_method_qualification_has_all_ten_prespecified_stress_cases(self):
        artifact = qualify_method(self.config)
        names = {item.name for item in artifact.stress_results}
        self.assertEqual(names, {
            "null_effect", "positive_effect", "common_market_shock",
            "repeated_issuer_dependence", "overlapping_influence_windows",
            "unequal_allocations", "random_denominator",
            "one_dominant_exposure_component", "insufficient_component_count",
            "dependence_model_misspecification_stress",
        })
        self.assertTrue(artifact.numerical_qualification_passed)
        self.assertFalse(artifact.qualified_for_forward_confirmation)
        self.assertTrue(artifact.synthetic_only)

    def test_qualification_store_replay_is_idempotent_and_conflict_detecting(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MethodQualificationStore(Path(directory) / "qualification.json")
            artifact = qualify_method(self.config)
            store.record(artifact)
            store.record(artifact)
            changed = replace(
                artifact, applicability_statement="materially different statement"
            )
            with self.assertRaises(ValueError):
                store.record(changed)

    def test_sampled_sign_flip_is_seed_deterministic(self):
        weights = [1.0] * 21
        outcomes = [0.001 * index for index in range(21)]
        components = [f"c{index}" for index in range(21)]
        first = sign_flip_interval(
            weights, outcomes, components, seed=7, draws=128
        )
        second = sign_flip_interval(
            weights, outcomes, components, seed=7, draws=128
        )
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.enumeration, "SEEDED_RADEMACHER_SAMPLE")

    def test_synthetic_positive_fixture_stays_development(self):
        cohorts = self._eligible_cohorts()
        outcomes = {
            event.event_id: 0.01 + index * 0.0001
            for index, event in enumerate(
                event for cohort in cohorts for event in cohort.events
            )
        }
        qualification = qualify_method(
            self.config,
            target_cohort_applicability_supported=True,
            applicability_evidence_hash="sha256:synthetic-applicability-fixture",
            applicability_statement="synthetic fixture only",
        )
        artifact = assemble_form4_effect(
            cohorts=cohorts, calendar=self.calendar, outcomes=outcomes,
            method_qualification=qualification, synthetic=True,
        )
        self.assertEqual(artifact.status, "ESTIMATE_RESOLVED")
        self.assertEqual(artifact.evidence_label, EVIDENCE_DEVELOPMENT)
        self.assertIsNotNone(artifact.effect_estimate)
        self.assertIsNotNone(artifact.delta_coordinate_hash)
        self.assertIn("SYNTHETIC_FIXTURE_DEVELOPMENT_ONLY", artifact.reason_codes)

    def test_activated_cohort_can_mature_without_rewriting_frozen_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            active = self._cohort(1, matured=False)
            store.register_cohort(self.config, active, self.calendar)
            self.assertFalse(store.cohorts()[0].matured)
            matured = self._cohort(1, matured=True)
            store.register_cohort(self.config, matured, self.calendar)
            self.assertTrue(store.cohorts()[0].matured)
            self.assertEqual(store.document()["protocol_hash"], self.config.protocol_hash)

    def test_zero_allocation_unresolved_d19_still_blocks_before_outcomes(self):
        cohorts = list(self._eligible_cohorts())
        zero = replace(
            cohorts[0].events[0],
            allocation_weight=0.0,
            d19_complete=False,
        )
        cohorts[0] = replace(cohorts[0], events=(zero,) + cohorts[0].events[1:])
        artifact = assemble_form4_effect(
            cohorts=tuple(cohorts),
            calendar=self.calendar,
            outcomes=ExplodingOutcomes(),
            method_qualification=qualify_method(self.config),
        )
        self.assertEqual(artifact.status, "REFUSED")
        self.assertIn(D19_INSUFFICIENT, artifact.reason_codes)

    def test_structural_sample_identity_binds_contributing_content_addresses(self):
        cohorts = list(self._eligible_cohorts())
        first = scientific_sample_id(tuple(cohorts), self.calendar)
        changed_event = replace(
            cohorts[0].events[0],
            content_addresses=("sha256:different-content",),
        )
        cohorts[0] = replace(
            cohorts[0], events=(changed_event,) + cohorts[0].events[1:]
        )
        second = scientific_sample_id(tuple(cohorts), self.calendar)
        self.assertNotEqual(first, second)

    def test_synthetic_method_qualification_cannot_self_authorize_forward(self):
        qualification = qualify_method(
            self.config,
            target_cohort_applicability_supported=True,
            applicability_evidence_hash="sha256:synthetic-only",
            applicability_statement="synthetic-only fixture",
        )
        self.assertTrue(qualification.numerical_qualification_passed)
        self.assertFalse(qualification.qualified_for_forward_confirmation)

    def test_confirmatory_look_is_durable_idempotent_and_conflict_closed(self):
        cohorts = self._eligible_cohorts()
        qualification = replace(
            qualify_method(self.config),
            target_cohort_applicability_supported=True,
            applicability_evidence_hash="sha256:independent-applicability-proof",
            applicability_statement="fixture representing independently supplied applicability",
            synthetic_only=False,
        )
        sample_id = scientific_sample_id(cohorts, self.calendar)
        receipt = ForwardConfirmationReceipt(
            receipt_id="receipt-1",
            protocol_hash=self.config.protocol_hash,
            sample_id=sample_id,
            evidence_identity="scope-1",
            session_seals_hash="sha256:session-seals",
            allocation_seal_hash="sha256:allocation-seal",
            use_ledger_receipt="sha256:use-ledger",
            family_look_receipt="sha256:family-look",
            post_freeze_recording_proven=True,
            evidence_unconsumed=True,
        )
        outcomes = {
            event.event_id: 0.01 + index * 0.0001
            for index, event in enumerate(
                event for cohort in cohorts for event in cohort.events
            )
        }
        with tempfile.TemporaryDirectory() as directory:
            store = CohortProtocolStore(Path(directory) / "protocol.json")
            for cohort in cohorts:
                store.register_cohort(self.config, cohort, self.calendar)
            first = assemble_form4_effect(
                cohorts=cohorts, calendar=self.calendar, outcomes=outcomes,
                method_qualification=qualification, forward_receipt=receipt,
                look_store=store,
            )
            replay = assemble_form4_effect(
                cohorts=cohorts, calendar=self.calendar, outcomes=outcomes,
                method_qualification=qualification, forward_receipt=receipt,
                look_store=store,
            )
            self.assertEqual(first.status, "ESTIMATE_RESOLVED")
            self.assertEqual(first.evidence_label, "FORWARD_CONFIRMATION")
            self.assertEqual(first.to_dict(), replay.to_dict())

            changed = dict(outcomes)
            changed[cohorts[0].events[0].event_id] += 0.001
            refused = assemble_form4_effect(
                cohorts=cohorts, calendar=self.calendar, outcomes=changed,
                method_qualification=qualification, forward_receipt=receipt,
                look_store=store,
            )
            self.assertEqual(refused.status, "REFUSED")
            self.assertIn(CONFIRMATORY_LOOK_ALREADY_CONSUMED, refused.reason_codes)

    def test_no_manual_forward_confirmed_boolean_exists(self):
        parameters = inspect.signature(assemble_form4_effect).parameters
        self.assertNotIn("forward_confirmed", parameters)
        self.assertNotIn("forward_confirmation", parameters)


if __name__ == "__main__":
    unittest.main()
