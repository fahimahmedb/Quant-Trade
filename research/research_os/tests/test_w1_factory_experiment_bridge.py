from __future__ import annotations

from copy import deepcopy
import unittest

from quant.factory.experiments import canonical_hash
from research.research_os.expansion.experiment_infrastructure import (
    ExperimentInfrastructureError,
    assert_same_infrastructure,
    bind_pre_outcome_infrastructure,
)


def fixture(*, declared=True):
    candidate = {"hypothesis_id":"H", "generation_id":"G", "claim":"x"}
    protocol_payload = {"hypothesis_id":"H", "generation_id":"G", "candidate":candidate}
    protocol_hash = canonical_hash(protocol_payload)
    envelope = {"experiment_id":"EXP-H-G", "status":"FROZEN_READY_NO_OUTCOME",
                "protocol_hash":protocol_hash, "protocol_payload":protocol_payload,
                "outcome_opened":False, "result":"NOT_OBSERVED"}
    bindings = {k:canonical_hash({k:1}) for k in
                ("generation","candidate","protocol","source","pit","code_environment")}
    frozen = {"hypothesis_id":"H", "generation_id":"G", "candidate_hash":canonical_hash(candidate),
              "protocol_hash":protocol_hash, "outcome_accessed":False, "economic_result":"NOT_OBSERVED"}
    body = {"experiment_id":"EXP-H-G", "frozen_protocol_hash":canonical_hash(frozen),
            "binding_hashes":bindings, "execution_mode":"DRY_RUN_NO_OUTCOME"}
    plan_hash = canonical_hash(body)
    receipt_payload = {"receipt_version":"pre-outcome-experiment-receipt.v1", "experiment_id":"EXP-H-G",
        "status":"PRE_OUTCOME_READY", "frozen_protocol_hash":canonical_hash(frozen),
        "execution_plan_hash":plan_hash, "binding_hashes":bindings,
        "outcome_access_authorized":False, "outcome_accessed":False, "economic_result":"NOT_OBSERVED",
        "economic_experiment_authorized":False, "prospective_observation_authorized":False,
        "real_capital_authorized":False, "live_trading_authorized":False}
    plan = {"experiment_id":"EXP-H-G", "status":"READY_FOR_REPRODUCIBLE_DRY_RUN",
            "execution_plan_hash":plan_hash, "plan":body, "frozen_protocol":frozen,
            "binding_hashes":bindings, "pre_outcome_receipt":{**receipt_payload, "receipt_hash":canonical_hash(receipt_payload)},
            "outcome_accessed":False, "economic_result":"NOT_OBSERVED"}
    replay = {"experiment_id":"EXP-H-G", "status":"REPLAY_MATCH", "execution_plan_hash":plan_hash,
              "outcome_accessed":False, "economic_result":"NOT_OBSERVED"}
    trial = {"hypothesis_id":"H", "generation_id":"G", "observed_attempt_count":0,
             "effective_trials_status":"UNKNOWN", "estimated_effective_trials":None}
    geometry = None; power = None
    if declared:
        geometry = {"status":"DECLARED", "observation_unit":"event", "target_observations":100,
                    "dependence_assumption":"independent units by preregistration", "cluster_key":None,
                    "max_cluster_share":None, "sampling_rule":"all eligible", "assumptions":["pre-outcome only"]}
        power = {"status":"DECLARED", "minimum_detectable_effect":0.1, "baseline_scale":1.0,
                 "significance_level":0.05, "desired_power":0.8, "required_observations":100,
                 "method":"DECLARED_BY_PROTOCOL_OWNER", "assumptions":["not empirically estimated"]}
    return envelope, plan, replay, trial, geometry, power


class BridgeTests(unittest.TestCase):
    def bind(self, declared=True):
        e,p,r,t,g,w = fixture(declared=declared)
        return bind_pre_outcome_infrastructure(envelope=e, plan=p, replay=r, trial_accounting=t,
                                               geometry_declaration=g, power_declaration=w)

    def test_declared_infrastructure_reaches_replay_verified(self):
        result = self.bind()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["registry"]["lifecycle"], "REPLAY_VERIFIED")
        self.assertFalse(result["outcome_accessed"])

    def test_unknown_geometry_and_power_are_explicit(self):
        result = self.bind(False)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["geometry"]["status"], "UNKNOWN")
        self.assertEqual(result["power"]["status"], "UNKNOWN")
        self.assertIn("GEOMETRY_DECLARATION_UNKNOWN", result["declaration_gaps"])
        self.assertIn("POWER_DECLARATION_UNKNOWN", result["declaration_gaps"])

    def test_missing_replay_is_not_execution_ready(self):
        e,p,_,t,g,w = fixture()
        result = bind_pre_outcome_infrastructure(envelope=e, plan=p, replay=None, trial_accounting=t,
                                                 geometry_declaration=g, power_declaration=w)
        self.assertIn("EXPERIMENT_REPLAY_NOT_VERIFIED", result["blockers"])
        self.assertEqual(result["registry"]["lifecycle"], "RECEIPT_BOUND")

    def test_previous_receipt_cannot_rebind_different_declaration(self):
        frozen = self.bind()
        e,p,r,t,g,w = fixture()
        g = deepcopy(g); g["target_observations"] = 101
        current = bind_pre_outcome_infrastructure(envelope=e, plan=p, replay=r, trial_accounting=t,
                                                  geometry_declaration=g, power_declaration=w)
        with self.assertRaisesRegex(ExperimentInfrastructureError, "BINDING_MISMATCH"):
            assert_same_infrastructure(current, frozen)

    def test_foreign_replay_fails_closed(self):
        e,p,r,t,g,w = fixture(); r["experiment_id"] = "EXP-FOREIGN"
        with self.assertRaisesRegex(ExperimentInfrastructureError, "FOREIGN_EXPERIMENT_REPLAY"):
            bind_pre_outcome_infrastructure(envelope=e, plan=p, replay=r, trial_accounting=t,
                                            geometry_declaration=g, power_declaration=w)

    def test_outcome_injection_fails_closed(self):
        e,p,r,t,g,w = fixture(); p["future_return"] = 0.2
        with self.assertRaises(ExperimentInfrastructureError):
            bind_pre_outcome_infrastructure(envelope=e, plan=p, replay=r, trial_accounting=t,
                                            geometry_declaration=g, power_declaration=w)


if __name__ == "__main__": unittest.main()
