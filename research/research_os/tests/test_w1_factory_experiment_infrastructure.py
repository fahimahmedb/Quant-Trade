from __future__ import annotations

from copy import deepcopy
import os
import unittest

from quant.factory.experiments import (
    ExperimentLifecycle,
    ExperimentRegistryError,
    assert_registry_matches,
    bind_execution_plan,
    bind_receipt,
    bind_replay,
    canonical_hash,
    create_registry_entry,
)
from quant.factory.geometry import GeometryDeclarationError, GeometryStatus, geometry_from_mapping
from quant.factory.outcome_firewall import OutcomeFirewallError, assert_pre_outcome_payload, read_outcomes
from quant.factory.power import PowerDeclarationError, PowerStatus, derive_normal_approximation, power_from_mapping


def base_fixture():
    candidate = {"hypothesis_id": "HYP-1", "generation_id": "GEN-1", "claim": "x"}
    protocol_payload = {"hypothesis_id": "HYP-1", "generation_id": "GEN-1", "candidate": candidate}
    protocol_hash = canonical_hash(protocol_payload)
    envelope = {
        "experiment_id": "EXP-HYP-1-GEN-1",
        "status": "FROZEN_READY_NO_OUTCOME",
        "protocol_hash": protocol_hash,
        "protocol_payload": protocol_payload,
        "outcome_opened": False,
        "result": "NOT_OBSERVED",
    }
    bindings = {key: canonical_hash({key: 1}) for key in
                ("generation", "candidate", "protocol", "source", "pit", "code_environment")}
    frozen = {
        "hypothesis_id": "HYP-1", "generation_id": "GEN-1",
        "candidate_hash": canonical_hash(candidate), "protocol_hash": protocol_hash,
        "source_snapshot_hashes": ["snap"], "source_pit_metadata": [{"asof": "T"}],
        "outcome_accessed": False, "economic_result": "NOT_OBSERVED",
    }
    trial = {"hypothesis_id": "HYP-1", "generation_id": "GEN-1", "observed_attempt_count": 0,
             "effective_trials_status": "UNKNOWN", "estimated_effective_trials": None}
    geometry = geometry_from_mapping(protocol_hash, None)
    power = power_from_mapping(protocol_hash, None)
    return envelope, frozen, bindings, trial, geometry, power


def entry_fixture():
    return create_registry_entry(*(), **dict(zip(
        ("envelope", "frozen_protocol", "binding_hashes", "trial_accounting", "geometry", "power"),
        base_fixture(),
    )))


def plan_fixture(entry):
    body = {
        "experiment_id": entry.experiment_id,
        "frozen_protocol_hash": entry.frozen_protocol_hash,
        "binding_hashes": dict(entry.binding_hashes),
        "execution_mode": "DRY_RUN_NO_OUTCOME",
    }
    return {
        "experiment_id": entry.experiment_id,
        "status": "READY_FOR_REPRODUCIBLE_DRY_RUN",
        "execution_plan_hash": canonical_hash(body),
        "plan": body,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
    }


def receipt_fixture(entry):
    payload = {
        "experiment_id": entry.experiment_id,
        "execution_plan_hash": entry.execution_plan_hash,
        "frozen_protocol_hash": entry.frozen_protocol_hash,
        "binding_hashes": dict(entry.binding_hashes),
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
    return {**payload, "receipt_hash": canonical_hash(payload)}


class RegistryBindingTests(unittest.TestCase):
    def test_registry_identity_is_deterministic_and_immutable(self):
        first = entry_fixture(); second = entry_fixture()
        self.assertEqual(first, second)
        self.assertEqual(first.lifecycle, ExperimentLifecycle.FROZEN)
        self.assertEqual(first.entry_hash, canonical_hash(first.identity_payload()))

    def test_foreign_registry_entry_rejected(self):
        entry = entry_fixture()
        with self.assertRaisesRegex(ExperimentRegistryError, "FOREIGN_REGISTRY_EXPERIMENT"):
            assert_registry_matches(entry, experiment_id="EXP-OTHER", candidate_hash=entry.candidate_hash,
                                    protocol_hash=entry.protocol_hash)

    def test_self_consistent_wrong_candidate_rejected_at_creation(self):
        envelope, frozen, bindings, trial, geometry, power = base_fixture()
        frozen["candidate_hash"] = canonical_hash({"hypothesis_id": "HYP-1", "generation_id": "GEN-1", "claim": "other"})
        with self.assertRaisesRegex(ExperimentRegistryError, "FROZEN_CANDIDATE_BINDING_MISMATCH"):
            create_registry_entry(envelope=envelope, frozen_protocol=frozen, binding_hashes=bindings,
                                  trial_accounting=trial, geometry=geometry, power=power)

    def test_protocol_mutation_after_registration_cannot_rebind(self):
        entry = entry_fixture(); plan = plan_fixture(entry)
        plan["plan"]["frozen_protocol_hash"] = "0" * 64
        plan["execution_plan_hash"] = canonical_hash(plan["plan"])
        with self.assertRaisesRegex(ExperimentRegistryError, "EXECUTION_PLAN_FROZEN_PROTOCOL_MISMATCH"):
            bind_execution_plan(entry, plan)

    def test_lifecycle_requires_exact_plan_receipt_and_replay(self):
        frozen = entry_fixture()
        prepared = bind_execution_plan(frozen, plan_fixture(frozen))
        receipt = receipt_fixture(prepared)
        bound = bind_receipt(prepared, receipt)
        replay = {"experiment_id": bound.experiment_id, "execution_plan_hash": bound.execution_plan_hash,
                  "status": "REPLAY_MATCH", "outcome_accessed": False, "economic_result": "NOT_OBSERVED"}
        verified = bind_replay(bound, replay)
        self.assertEqual(verified.lifecycle, ExperimentLifecycle.REPLAY_VERIFIED)
        with self.assertRaises(ExperimentRegistryError):
            bind_replay(verified, replay)

    def test_replay_against_different_experiment_rejected(self):
        frozen = entry_fixture(); prepared = bind_execution_plan(frozen, plan_fixture(frozen))
        bound = bind_receipt(prepared, receipt_fixture(prepared))
        replay = {"experiment_id": "EXP-FOREIGN", "execution_plan_hash": bound.execution_plan_hash,
                  "status": "REPLAY_MATCH", "outcome_accessed": False, "economic_result": "NOT_OBSERVED"}
        with self.assertRaisesRegex(ExperimentRegistryError, "FOREIGN_EXPERIMENT_REPLAY"):
            bind_replay(bound, replay)


class PowerGeometryTests(unittest.TestCase):
    def test_unknown_is_explicit(self):
        envelope, *_ = base_fixture()
        self.assertEqual(power_from_mapping(envelope["protocol_hash"], None).status, PowerStatus.UNKNOWN)
        self.assertEqual(geometry_from_mapping(envelope["protocol_hash"], None).status, GeometryStatus.UNKNOWN)

    def test_bool_and_nonfinite_power_rejected(self):
        protocol_hash = base_fixture()[0]["protocol_hash"]
        payload = {"status":"DECLARED", "minimum_detectable_effect":True, "baseline_scale":1.0,
                   "significance_level":0.05, "desired_power":0.8, "required_observations":100,
                   "method":"DECLARED", "assumptions":["iid"]}
        with self.assertRaises(PowerDeclarationError): power_from_mapping(protocol_hash, payload)
        payload["minimum_detectable_effect"] = float("nan")
        with self.assertRaises(PowerDeclarationError): power_from_mapping(protocol_hash, payload)

    def test_semantic_null_known_power_rejected(self):
        protocol_hash = base_fixture()[0]["protocol_hash"]
        with self.assertRaises(PowerDeclarationError):
            power_from_mapping(protocol_hash, {"status":"DECLARED"})

    def test_power_derivation_requires_declared_assumptions_and_is_bound(self):
        protocol_hash = base_fixture()[0]["protocol_hash"]
        power = derive_normal_approximation(protocol_hash=protocol_hash, minimum_detectable_effect=.1,
            baseline_scale=1.0, significance_level=.05, desired_power=.8,
            assumptions=("normal approximation appropriate", "independent observation units"))
        self.assertEqual(power.status, PowerStatus.DERIVED_FROM_DECLARED_ASSUMPTIONS)
        self.assertGreaterEqual(power.required_observations, 2)
        self.assertEqual(power.protocol_hash, protocol_hash)

    def test_stale_geometry_protocol_binding_rejected(self):
        envelope, frozen, bindings, trial, _, power = base_fixture()
        geometry = geometry_from_mapping("f" * 64, None)
        with self.assertRaisesRegex(ExperimentRegistryError, "GEOMETRY_PROTOCOL_BINDING_MISMATCH"):
            create_registry_entry(envelope=envelope, frozen_protocol=frozen, binding_hashes=bindings,
                                  trial_accounting=trial, geometry=geometry, power=power)

    def test_geometry_rejects_bool_and_nonfinite(self):
        protocol_hash = base_fixture()[0]["protocol_hash"]
        common = {"status":"DECLARED", "observation_unit":"event", "target_observations":10,
                  "dependence_assumption":"clustered", "sampling_rule":"all eligible"}
        with self.assertRaises(GeometryDeclarationError):
            geometry_from_mapping(protocol_hash, {**common, "target_observations": True})
        with self.assertRaises(GeometryDeclarationError):
            geometry_from_mapping(protocol_hash, {**common, "max_cluster_share": float("inf")})


class OutcomeFirewallTests(unittest.TestCase):
    def test_outcome_payload_and_derived_fields_rejected(self):
        for payload in (
            {"outcome_payload": []}, {"future_return": 0.0}, {"p_value": 0.2},
            {"economic_result": 0.0}, {"result": {"net_return": 0.1}},
            {"role": "outcome", "dataset_id": "x"},
        ):
            with self.subTest(payload=payload), self.assertRaises(OutcomeFirewallError):
                assert_pre_outcome_payload(payload)

    def test_outcome_definition_is_not_confused_with_outcome_data(self):
        assert_pre_outcome_payload({"outcome_definition":"five day return", "result":"NOT_OBSERVED",
                                    "outcome_accessed":False})

    def test_legacy_gate_cannot_bypass_campaign_authority(self):
        os.environ["QUANT_BLUE_TEAM_OUTCOME_TOKEN"] = "x" * 32
        try:
            with self.assertRaisesRegex(OutcomeFirewallError, "SEALED_BY_AUTHORITY"):
                read_outcomes(None, lambda: [1, 2, 3], gate=object())
        finally:
            os.environ.pop("QUANT_BLUE_TEAM_OUTCOME_TOKEN", None)


if __name__ == "__main__":
    unittest.main()
