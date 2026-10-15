from __future__ import annotations

from typing import Any, Dict, Iterable, List
from research.research_os.scientific_store import sha256_json
import math


CRITICAL_CHECKS = {
    "producer_independence",
    "protocol_frozen",
    "source_pit",
    "source_revision_policy",
    "source_survivorship_policy",
    "reproducible_plan",
    "no_outcome_access",
    "trial_accounting_explicit",
    "multiplicity_declared",
    "documentary_evidence_bound",
    "executed_documentary_transform",
    "implementability_passed",
}


def validator_diagnostics_v2(
    *,
    engine_output: Dict[str, Any],
    validation_v1: Dict[str, Any],
    source_qualifications: Iterable[Dict[str, Any]],
    envelope: Dict[str, Any],
    dry_run_plan: Dict[str, Any],
    trial_record: Dict[str, Any],
    experiment_meta: Dict[str, Any],
    executed_dry_run: Dict[str, Any] = None,
) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    sources = list(source_qualifications)
    checks: Dict[str, Dict[str, Any]] = {}

    def add(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"status": "PASS" if passed else "FAIL", "detail": detail}

    add(
        "producer_independence",
        validation_v1.get("independent_from_producer") is True
        and bool(validation_v1.get("validator"))
        and validation_v1.get("producer_engine") == engine_output.get("engine_id")
        and validation_v1.get("producer_engine") != validation_v1.get("validator"),
        "Validator identity must differ from producing engine.",
    )
    from .final_shape import _hash
    protocol = envelope.get('protocol_payload')
    protocol_valid = (isinstance(protocol, dict)
                      and _hash(protocol) == envelope.get('protocol_hash')
                      and protocol.get('candidate') == candidate)
    add(
        "protocol_frozen",
        envelope.get("status") == "FROZEN_READY_NO_OUTCOME" and protocol_valid,
        "Protocol hash must exist before any outcome access.",
    )
    add(
        "source_pit",
        bool(sources) and all(item.get("status") == "PASS" and item.get("point_in_time_qualified") is True for item in sources),
        "Every route must be explicitly point-in-time qualified.",
    )
    add(
        "source_revision_policy",
        bool(sources)
        and all(item.get("canonical_route", {}).get("revision_policy") not in (None, "", "UNKNOWN") for item in sources),
        "Revision handling must be declared for every route.",
    )
    add(
        "source_survivorship_policy",
        bool(sources)
        and all(item.get("canonical_route", {}).get("survivorship_policy") not in (None, "", "UNKNOWN") for item in sources),
        "Survivorship handling must be declared for every route.",
    )
    add(
        "reproducible_plan",
        dry_run_plan.get("status") == "READY_FOR_REPRODUCIBLE_DRY_RUN"
        and dry_run_plan.get("execution_plan_hash") == sha256_json(dry_run_plan.get('plan')),
        "Execution plan must be replayable before economic execution.",
    )
    add(
        "no_outcome_access",
        envelope.get("outcome_opened") is False
        and dry_run_plan.get("outcome_accessed") is False
        and all(item.get("outcome_accessed") is False for item in sources),
        "No source, envelope or runner may contain opened outcomes in this build phase.",
    )
    add(
        "trial_accounting_explicit",
        type(trial_record.get("observed_attempt_count")) is int
        and trial_record["observed_attempt_count"] >= 0
        and (trial_record.get("effective_trials_status") == 'UNKNOWN' and trial_record.get('estimated_effective_trials') is None
             or trial_record.get("effective_trials_status") == 'KNOWN' and type(trial_record.get('estimated_effective_trials')) in (int, float)
             and math.isfinite(trial_record['estimated_effective_trials'])
             and trial_record['estimated_effective_trials'] >= 0),
        "Observed attempts and effective trials must remain distinct.",
    )
    add(
        "multiplicity_declared",
        experiment_meta.get("multiplicity_accounting_declared") is True,
        "Multiplicity accounting must be declared before economic evidence.",
    )
    add(
        "falsification_scope_present",
        bool(candidate.get("falsification_scope")),
        "Candidate must state what evidence can falsify the claim.",
    )
    add(
        "decision_map_present",
        bool(candidate.get("decision_map")),
        "Candidate must carry a preregistered decision map.",
    )

    add('implementability_passed', validation_v1.get('implementability_status') == 'PASS',
        'Scientific readiness cannot override an implementability blocker.')
    evidence = candidate.get('documentary_evidence')
    bound, executed = True, True
    if evidence is not None:
        from types import SimpleNamespace
        from research.research_os.engines.protocol import EngineContext
        from .engine_dossiers_v1 import documentary_candidate
        try:
            source = {'documentary_packet': evidence['packet'], 'freeze_time': evidence['freeze_time']}
            rebuilt = documentary_candidate(
                SimpleNamespace(engine_id=engine_output['engine_id'], family=engine_output['engine_family']),
                source, EngineContext('VALIDATOR-DOCUMENTARY'), candidate['hypothesis_id'],
            )
            bound = rebuilt == engine_output
        except (ValueError, KeyError, TypeError):
            bound = False
        run = executed_dry_run or {}
        receipt_payload = {k: v for k, v in run.items() if k != 'execution_receipt_hash'}
        executed = (run.get('state') == 'EXECUTED_DRY_RUN'
                    and run.get('execution_plan_hash') == dry_run_plan.get('execution_plan_hash')
                    and run.get('input_hash') == dry_run_plan.get('plan', {}).get('dataset_manifest_hash')
                    and run.get('execution_receipt_hash') == sha256_json(receipt_payload)
                    and engine_output in run.get('records', [])
                    and run.get('outcome_accessed') is False)
    add('documentary_evidence_bound', bound, 'Typed documentary facts must reproduce the frozen candidate.')
    add('executed_documentary_transform', executed, 'A documentary plan alone is not an executed dry-run.')

    failures: List[str] = sorted(name for name, record in checks.items() if record["status"] != "PASS")
    critical_failures = sorted(set(failures) & CRITICAL_CHECKS)
    claim_ceiling = "DESIGN_ONLY"
    if not critical_failures and not failures:
        claim_ceiling = "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY"
    elif not critical_failures:
        claim_ceiling = "DESIGN_WITH_NONCRITICAL_GAPS"

    return {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "validator": "independent-validator.v2",
        "status": "PASS" if not critical_failures else "BLOCK",
        "checks": checks,
        "failures": failures,
        "critical_failures": critical_failures,
        "claim_ceiling": claim_ceiling,
        "economic_claim_authorized": False,
        "claim_mutated": False,
    }


def validator_portfolio_summary(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(records)
    return {
        "validator": "independent-validator.v2",
        "candidate_count": len(items),
        "pass_count": sum(item["status"] == "PASS" for item in items),
        "block_count": sum(item["status"] != "PASS" for item in items),
        "economic_claims_authorized": 0,
        "claim_ceilings": {item["hypothesis_id"]: item["claim_ceiling"] for item in items},
    }
