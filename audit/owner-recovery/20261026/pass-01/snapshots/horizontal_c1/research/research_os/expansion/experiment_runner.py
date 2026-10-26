from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Sequence
import hashlib
import sys
from pathlib import Path

from research.research_os.scientific_store import sha256_json


UNKNOWN = "UNKNOWN"
NOT_OBSERVED = "NOT_OBSERVED"
FROZEN_PROTOCOL_VERSION = "pre-outcome-frozen-protocol.v1"

FROZEN_PROTOCOL_FIELDS = (
    "universe",
    "clock",
    "entry_definition",
    "exit_definition",
    "economic_expression",
    "benchmark",
    "gross_metric",
    "net_metric",
    "cost_assumptions",
    "capacity_assumptions",
    "sample_definition",
    "sample_window",
    "exclusions",
    "missing_data_policy",
    "revision_policy",
    "survivorship_policy",
    "falsification_rule",
    "decision_map",
    "observed_attempt_count",
    "effective_trials",
    "multiplicity_family",
)

# These declarations were added after the original frozen-protocol contract. They
# remain optional for byte-compatible replay of historical plans, but when a
# current protocol carries them they are part of the runner's protocol identity.
# Adding, removing or changing one after freeze must therefore move the protocol
# binding rather than being left to a downstream sidecar check.
FROZEN_PROTOCOL_IDENTITY_FIELDS = FROZEN_PROTOCOL_FIELDS + (
    "multiplicity_method",
    "geometry_declaration",
    "power_declaration",
)

BINDING_ORDER = (
    "generation",
    "candidate",
    "protocol",
    "source",
    "pit",
    "code_environment",
)

BINDING_MISMATCH_ERRORS = {
    "generation": "GENERATION_BINDING_MISMATCH",
    "candidate": "CANDIDATE_BINDING_MISMATCH",
    "protocol": "PROTOCOL_BINDING_MISMATCH",
    "source": "SOURCE_BINDING_MISMATCH",
    "pit": "PIT_BINDING_MISMATCH",
    "code_environment": "CODE_ENVIRONMENT_BINDING_MISMATCH",
}


class FrozenExperimentBindingError(ValueError):
    """Raised when a pre-outcome experiment freeze is incomplete or changes materially."""


def _valid_effective_trials(value: Any) -> bool:
    return value == UNKNOWN or (
        type(value) in (int, float) and value >= 0
        and (not isinstance(value, float) or isfinite(value))
    )


def _copy_fields(source: Mapping[str, Any], fields: Sequence[str]) -> Dict[str, Any]:
    return {field: deepcopy(source[field]) for field in fields if field in source}


def _source_snapshot_hash(item: Mapping[str, Any]) -> Any:
    return item.get("snapshot_hash") or item.get("route_hash") or item.get("content_hash")


class DryRunExperimentRunner:
    """Builds and replays deterministic execution plans without opening economic outcomes."""

    def __init__(self, runner_version: str = "dry-run-experiment-runner.v1") -> None:
        self.runner_version = runner_version

    def plan(
        self,
        envelope: Dict[str, Any],
        source_qualifications: Iterable[Dict[str, Any]],
        runner_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        qualifications = list(source_qualifications)
        blockers: List[str] = []
        if envelope.get("status") != "FROZEN_READY_NO_OUTCOME":
            blockers.append("EXPERIMENT_ENVELOPE_NOT_FROZEN")
        if not envelope.get("protocol_hash"):
            blockers.append("PROTOCOL_HASH_MISSING")
        if envelope.get("outcome_opened") is not False:
            blockers.append("OUTCOME_ALREADY_OPENED")
        if envelope.get("result", NOT_OBSERVED) != NOT_OBSERVED:
            blockers.append("ECONOMIC_RESULT_ALREADY_OBSERVED")
        if not qualifications:
            blockers.append("SOURCE_QUALIFICATION_MISSING")
        if any(item.get("status") != "PASS" for item in qualifications):
            blockers.append("SOURCE_QUALIFICATION_BLOCKED")
        if any(item.get("outcome_accessed") is not False for item in qualifications):
            blockers.append("SOURCE_OUTCOME_ACCESS_DETECTED")

        required_meta = ("dataset_manifest_hash", "code_hash", "environment_hash", "seed")
        for field in required_meta:
            if runner_meta.get(field) in (None, ""):
                blockers.append(f"RUNNER_{field.upper()}_MISSING")

        source_hashes = sorted(item.get("route_hash") for item in qualifications if item.get("route_hash"))
        frozen_protocol = None
        binding_hashes = None
        frozen_protocol_hash = None
        if runner_meta.get("frozen_protocol") is not None:
            frozen_protocol, freeze_blockers = self._freeze_pre_outcome_protocol(
                envelope, qualifications, runner_meta
            )
            blockers.extend(freeze_blockers)
            if frozen_protocol is not None:
                binding_hashes = self._binding_hashes(frozen_protocol)
                frozen_protocol_hash = sha256_json(frozen_protocol)

        plan_payload = {
            "runner_version": self.runner_version,
            "experiment_id": envelope.get("experiment_id"),
            "protocol_hash": envelope.get("protocol_hash"),
            "dataset_manifest_hash": runner_meta.get("dataset_manifest_hash"),
            "code_hash": runner_meta.get("code_hash"),
            "environment_hash": runner_meta.get("environment_hash"),
            "seed": runner_meta.get("seed"),
            "source_route_hashes": source_hashes,
            "declared_metrics": list(runner_meta.get("declared_metrics") or []),
            "execution_mode": "DRY_RUN_NO_OUTCOME",
        }
        # Preserve the exact legacy dry-run plan payload/fingerprint unless the
        # caller explicitly requests the new pre-outcome economic freeze.
        if frozen_protocol is not None:
            plan_payload.update({
                "frozen_protocol_version": FROZEN_PROTOCOL_VERSION,
                "frozen_protocol_hash": frozen_protocol_hash,
                "binding_hashes": deepcopy(binding_hashes),
            })
        plan_hash = sha256_json(plan_payload)
        unique_blockers = sorted(set(blockers))
        ready = not unique_blockers
        result = {
            "experiment_id": envelope.get("experiment_id"),
            "status": "READY_FOR_REPRODUCIBLE_DRY_RUN" if ready else "BLOCK",
            "blockers": unique_blockers,
            "runner_version": self.runner_version,
            "execution_plan_hash": plan_hash,
            "plan": plan_payload,
            "outcome_access_authorized": False,
            "outcome_accessed": False,
            "economic_result": NOT_OBSERVED,
            "side_effects_authorized": False,
            "reproducible_inputs_frozen": ready,
            "frozen_protocol_capability": "READY" if frozen_protocol is not None and ready else (
                "BLOCKED" if runner_meta.get("frozen_protocol") is not None else "LEGACY_DRY_RUN_ONLY"
            ),
            "frozen_protocol": frozen_protocol,
            "binding_hashes": deepcopy(binding_hashes),
        }
        if frozen_protocol is not None:
            receipt = {
                "receipt_version": "pre-outcome-experiment-receipt.v1",
                "experiment_id": envelope.get("experiment_id"),
                "status": "PRE_OUTCOME_READY" if ready else "BLOCK",
                "frozen_protocol_hash": frozen_protocol_hash,
                "execution_plan_hash": plan_hash,
                "binding_hashes": deepcopy(binding_hashes),
                "outcome_access_authorized": False,
                "outcome_accessed": False,
                "economic_result": NOT_OBSERVED,
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            }
            receipt["receipt_hash"] = sha256_json(receipt)
            result["pre_outcome_receipt"] = receipt
        return result

    def _freeze_pre_outcome_protocol(
        self,
        envelope: Mapping[str, Any],
        qualifications: Sequence[Mapping[str, Any]],
        runner_meta: Mapping[str, Any],
    ) -> tuple[Dict[str, Any] | None, List[str]]:
        blockers: List[str] = []
        declared = runner_meta.get("frozen_protocol")
        if not isinstance(declared, Mapping):
            return None, ["FROZEN_PROTOCOL_BINDINGS_INVALID"]

        for field in FROZEN_PROTOCOL_FIELDS:
            if field not in declared:
                blockers.append(f"FROZEN_PROTOCOL_{field.upper()}_MISSING")

        payload = envelope.get("protocol_payload")
        candidate = payload.get("candidate") if isinstance(payload, Mapping) else None
        hypothesis_id = payload.get("hypothesis_id") if isinstance(payload, Mapping) else None
        generation_id = payload.get("generation_id") if isinstance(payload, Mapping) else None
        if not isinstance(candidate, Mapping):
            blockers.append("FROZEN_PROTOCOL_CANDIDATE_MISSING")
        if isinstance(payload, Mapping) and sha256_json(payload) != envelope.get("protocol_hash"):
            blockers.append("FROZEN_PROTOCOL_HASH_MISMATCH")
        if isinstance(candidate, Mapping):
            if candidate.get("hypothesis_id") != hypothesis_id:
                blockers.append("FROZEN_PROTOCOL_HYPOTHESIS_BINDING_MISMATCH")
            if candidate.get("generation_id") != generation_id:
                blockers.append("FROZEN_PROTOCOL_GENERATION_BINDING_MISMATCH")
        if hypothesis_id in (None, ""):
            blockers.append("FROZEN_PROTOCOL_HYPOTHESIS_ID_MISSING")
        if generation_id in (None, ""):
            blockers.append("FROZEN_PROTOCOL_GENERATION_ID_MISSING")

        candidate_hash = sha256_json(candidate) if isinstance(candidate, Mapping) else None
        protocol_hash = envelope.get("protocol_hash")
        source_snapshot_hashes = sorted(
            value for value in (_source_snapshot_hash(item) for item in qualifications) if value
        )
        if len(source_snapshot_hashes) != len(qualifications):
            blockers.append("SOURCE_SNAPSHOT_HASH_MISSING")

        source_pit_metadata = runner_meta.get("source_pit_metadata")
        if source_pit_metadata in (None, ""):
            blockers.append("SOURCE_PIT_METADATA_MISSING")

        required_binding_meta = ("code_sha", "environment", "dependency_fingerprint")
        for field in required_binding_meta:
            if runner_meta.get(field) in (None, ""):
                blockers.append(f"RUNNER_{field.upper()}_MISSING")

        if "observed_attempt_count" in declared:
            attempts = declared.get("observed_attempt_count")
            if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
                blockers.append("FROZEN_PROTOCOL_OBSERVED_ATTEMPT_COUNT_INVALID")
        if "effective_trials" in declared:
            effective = declared.get("effective_trials")
            if not _valid_effective_trials(effective):
                blockers.append("FROZEN_PROTOCOL_EFFECTIVE_TRIALS_INVALID")

        authoritative = {
            "hypothesis_id": hypothesis_id,
            "generation_id": generation_id,
            "candidate_hash": candidate_hash,
            "protocol_hash": protocol_hash,
        }
        for field, value in authoritative.items():
            if field in declared and declared.get(field) != value:
                blockers.append(f"DECLARED_{field.upper()}_MISMATCH")

        if blockers:
            return None, blockers

        package: Dict[str, Any] = {
            "freeze_version": FROZEN_PROTOCOL_VERSION,
            **authoritative,
            "source_snapshot_hashes": source_snapshot_hashes,
            "source_route_hashes": sorted(
                item.get("route_hash") for item in qualifications if item.get("route_hash")
            ),
            "source_pit_metadata": deepcopy(source_pit_metadata),
            **_copy_fields(declared, FROZEN_PROTOCOL_IDENTITY_FIELDS),
            "seed": runner_meta.get("seed"),
            "environment": runner_meta.get("environment"),
            "code_sha": runner_meta.get("code_sha"),
            "code_hash": runner_meta.get("code_hash"),
            "environment_hash": runner_meta.get("environment_hash"),
            "dependency_fingerprint": runner_meta.get("dependency_fingerprint"),
        }
        return package, []

    @staticmethod
    def _binding_hashes(frozen_protocol: Mapping[str, Any]) -> Dict[str, str]:
        protocol_fields = _copy_fields(frozen_protocol, FROZEN_PROTOCOL_IDENTITY_FIELDS)
        return {
            "generation": sha256_json({"generation_id": frozen_protocol["generation_id"]}),
            "candidate": sha256_json({
                "hypothesis_id": frozen_protocol["hypothesis_id"],
                "candidate_hash": frozen_protocol["candidate_hash"],
            }),
            "protocol": sha256_json({
                "protocol_hash": frozen_protocol["protocol_hash"],
                **protocol_fields,
            }),
            "source": sha256_json({
                "source_snapshot_hashes": frozen_protocol["source_snapshot_hashes"],
                "source_route_hashes": frozen_protocol.get("source_route_hashes", []),
            }),
            "pit": sha256_json(frozen_protocol["source_pit_metadata"]),
            "code_environment": sha256_json({
                "seed": frozen_protocol["seed"],
                "environment": frozen_protocol["environment"],
                "code_sha": frozen_protocol["code_sha"],
                "code_hash": frozen_protocol["code_hash"],
                "environment_hash": frozen_protocol["environment_hash"],
                "dependency_fingerprint": frozen_protocol["dependency_fingerprint"],
            }),
        }

    def verify_bindings(
        self,
        plan: Dict[str, Any],
        envelope: Dict[str, Any],
        source_qualifications: Iterable[Dict[str, Any]],
        runner_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Rebind a frozen plan and fail closed on any material pre-outcome change."""
        self.replay(plan)
        if not isinstance(plan.get("frozen_protocol"), Mapping):
            raise FrozenExperimentBindingError("FROZEN_PROTOCOL_NOT_PRESENT")

        # Preserve the existing identity diagnostics even when the supplied
        # envelope also carries a stale protocol hash after that identity edit.
        payload = envelope.get("protocol_payload")
        if isinstance(payload, Mapping):
            if payload.get("generation_id") != plan["frozen_protocol"]["generation_id"]:
                raise FrozenExperimentBindingError("GENERATION_BINDING_MISMATCH")
            candidate = payload.get("candidate")
            if isinstance(candidate, Mapping) and sha256_json(candidate) != plan["frozen_protocol"]["candidate_hash"]:
                raise FrozenExperimentBindingError("CANDIDATE_BINDING_MISMATCH")

        rebound = self.plan(envelope, source_qualifications, runner_meta)
        if rebound.get("status") != "READY_FOR_REPRODUCIBLE_DRY_RUN":
            raise FrozenExperimentBindingError(
                "REBIND_BLOCKED:" + ",".join(rebound.get("blockers") or [])
            )
        original_hashes = plan.get("binding_hashes") or {}
        rebound_hashes = rebound.get("binding_hashes") or {}
        for binding in BINDING_ORDER:
            if original_hashes.get(binding) != rebound_hashes.get(binding):
                raise FrozenExperimentBindingError(BINDING_MISMATCH_ERRORS[binding])
        if plan.get("execution_plan_hash") != rebound.get("execution_plan_hash"):
            raise FrozenExperimentBindingError("EXECUTION_PLAN_BINDING_MISMATCH")
        self._assert_pre_outcome_closed(rebound)
        return {
            "experiment_id": plan["experiment_id"],
            "status": "FROZEN_BINDINGS_MATCH",
            "execution_plan_hash": plan["execution_plan_hash"],
            "outcome_accessed": False,
            "economic_result": NOT_OBSERVED,
        }

    def replay(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        if plan.get("status") != "READY_FOR_REPRODUCIBLE_DRY_RUN":
            raise ValueError("blocked execution plan cannot be replayed")
        self._assert_pre_outcome_closed(plan)
        replay_hash = sha256_json(plan["plan"])
        if replay_hash != plan["execution_plan_hash"]:
            raise ValueError("execution plan mutation detected")
        if plan.get("experiment_id") != plan["plan"].get("experiment_id"):
            raise ValueError("EXPERIMENT_ID_BINDING_MISMATCH")
        frozen_protocol = plan.get("frozen_protocol")
        if "frozen_protocol_version" in plan["plan"]:
            if plan["plan"]["frozen_protocol_version"] != FROZEN_PROTOCOL_VERSION:
                raise ValueError("UNSUPPORTED_FROZEN_PROTOCOL_VERSION")
            if not isinstance(frozen_protocol, Mapping):
                raise ValueError("FROZEN_PROTOCOL_REQUIRED")
        if frozen_protocol is not None:
            expected_frozen_hash = plan["plan"].get("frozen_protocol_hash")
            if expected_frozen_hash != sha256_json(frozen_protocol):
                raise ValueError("frozen protocol mutation detected")
            computed_hashes = self._binding_hashes(frozen_protocol)
            if plan.get("binding_hashes") != computed_hashes:
                raise ValueError("frozen binding hash mutation detected")
            if plan["plan"].get("binding_hashes") != computed_hashes:
                raise ValueError("execution plan binding hash mismatch")
            if not _valid_effective_trials(frozen_protocol.get("effective_trials")):
                raise ValueError("FROZEN_PROTOCOL_EFFECTIVE_TRIALS_INVALID")

        receipt = plan.get("pre_outcome_receipt")
        if frozen_protocol is not None and not isinstance(receipt, Mapping):
            raise ValueError("PRE_OUTCOME_RECEIPT_REQUIRED")
        if receipt is not None:
            if frozen_protocol is None:
                raise ValueError("PRE_OUTCOME_RECEIPT_WITHOUT_FROZEN_PROTOCOL")
            expected_receipt_hash = receipt.get("receipt_hash")
            payload = {key: value for key, value in receipt.items() if key != "receipt_hash"}
            if expected_receipt_hash != sha256_json(payload):
                raise ValueError("pre-outcome receipt mutation detected")
            expected = {
                "receipt_version": "pre-outcome-experiment-receipt.v1",
                "status": "PRE_OUTCOME_READY",
                "experiment_id": plan["plan"].get("experiment_id"),
                "execution_plan_hash": replay_hash,
                "frozen_protocol_hash": plan["plan"].get("frozen_protocol_hash"),
                "binding_hashes": plan.get("binding_hashes"),
            }
            if any(receipt.get(key) != value for key, value in expected.items()):
                raise ValueError("PRE_OUTCOME_RECEIPT_BINDING_MISMATCH")
            self._assert_pre_outcome_closed(receipt, require_authority_fields=True)
        return {
            "experiment_id": plan["experiment_id"],
            "status": "REPLAY_MATCH",
            "execution_plan_hash": replay_hash,
            "outcome_accessed": False,
            "economic_result": NOT_OBSERVED,
        }

    @staticmethod
    def _assert_pre_outcome_closed(value: Mapping[str, Any], *, require_authority_fields=False) -> None:
        if value.get("outcome_accessed") is not False:
            raise PermissionError("dry-run state refuses outcome-bearing data")
        if value.get("economic_result") != NOT_OBSERVED:
            raise PermissionError("dry-run state refuses observed economic results")
        if value.get("outcome_access_authorized", False) is not False:
            raise PermissionError("dry-run state refuses outcome authorization")
        default = None if require_authority_fields else False
        for key in ("economic_experiment_authorized", "prospective_observation_authorized",
                    "real_capital_authorized", "live_trading_authorized"):
            if value.get(key, default) is not False:
                raise PermissionError("PRE_OUTCOME_AUTHORITY_NOT_CLOSED:" + key)

    @staticmethod
    def execution_code_hash() -> str:
        root = Path(__file__).resolve().parents[1]
        paths = [Path(__file__), root / 'expansion/engine_dossiers_v1.py',
                 root / 'engines/builtin.py', root / 'engines/protocol.py',
                 root / 'expansion/archaeology.py', root / 'expansion/persistent_state.py',
                 root / 'expansion/source_adapters_v1.py',
                 root / 'scientific_store.py']
        return sha256_json({str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    @staticmethod
    def execution_environment_hash() -> str:
        import decimal
        context = decimal.getcontext()
        return sha256_json({"python": sys.version, "decimal_context": {
            key:getattr(context, key) for key in ('prec','rounding','Emin','Emax','capitals','clamp')},
            "decimal_traps": {signal.__name__:enabled for signal, enabled in context.traps.items()}})

    def execute(self, plan: Dict[str, Any], inputs: List[Dict[str, Any]], checkpoint_dir: Path) -> Dict[str, Any]:
        """Execute only pinned documentary fact transforms; never a backtest.

        PREPARED survives interruption before COMPLETED. Replay recomputes the
        transform and must match the immutable completed result byte-for-byte.
        """
        from research.research_os.engines.builtin import ENGINE_REGISTRY
        from research.research_os.engines.protocol import EngineContext
        from .archaeology import EdgeArchaeologyEngine
        from .persistent_state import write_immutable_json

        self.replay(plan)
        payload = plan['plan']
        if payload.get('declared_metrics') != ['DOCUMENTARY_FACTS_V1']:
            raise ValueError('execution supports only DOCUMENTARY_FACTS_V1')
        if not inputs or sha256_json(inputs) != payload.get('dataset_manifest_hash'):
            raise ValueError('execution input hash mismatch')
        if payload.get('code_hash') != self.execution_code_hash():
            raise ValueError('execution code hash mismatch')
        if payload.get('environment_hash') != self.execution_environment_hash():
            raise ValueError('execution environment hash mismatch')
        binding = {"execution_plan_hash": plan['execution_plan_hash'],
                   "input_hash": sha256_json(inputs), "state": "PREPARED"}
        key = plan['execution_plan_hash']
        write_immutable_json(Path(checkpoint_dir) / f'{key}.prepared.json', binding)
        records = []
        for item in inputs:
            if set(item) != {'engine_key', 'source'} or 'documentary_packet' not in item['source']:
                raise ValueError('execution requires structured documentary inputs')
            engine = EdgeArchaeologyEngine() if item['engine_key'] == 'archaeology' else ENGINE_REGISTRY[item['engine_key']]
            synthetic = item['source']['documentary_packet'].get('evidence_class') == 'SYNTHETIC'
            output = engine.run(item['source'], EngineContext('DOCUMENTARY_FACTS_V1', synthetic_only=synthetic))
            records.append(output)
        evidence_classes = {r['candidate']['documentary_evidence']['packet']['evidence_class'] for r in records}
        result = {"experiment_id": plan['experiment_id'], "execution_plan_hash": key,
                  "input_hash": binding['input_hash'], "state": "EXECUTED_DRY_RUN",
                  "records": records, "evidence_class": next(iter(evidence_classes)) if len(evidence_classes) == 1 else 'MIXED',
                  "outcome_accessed": False, "economic_result": NOT_OBSERVED}
        result['execution_receipt_hash'] = sha256_json(result)
        write_immutable_json(Path(checkpoint_dir) / f'{key}.completed.json', result)
        return result


def summarize_reproducibility(plans: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = [deepcopy(item) for item in plans]
    return {
        "runner": "dry-run-experiment-runner.v1",
        "plan_count": len(items),
        "ready_count": sum(item["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN" for item in items),
        "blocked_count": sum(item["status"] != "READY_FOR_REPRODUCIBLE_DRY_RUN" for item in items),
        "outcomes_opened": sum(bool(item.get("outcome_accessed")) for item in items),
        "all_plan_hashes_unique": len({item["execution_plan_hash"] for item in items}) == len(items),
        "economic_result_observed": False,
    }
