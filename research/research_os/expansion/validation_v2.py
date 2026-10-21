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
    "falsification_scope_present",
    "decision_map_present",
    "documentary_dossier_bound",
    "documentary_dossier_sufficient",
    "documentary_disconfirmation_supported",
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
        and dry_run_plan.get("execution_plan_hash") == sha256_json(dry_run_plan.get('plan'))
        and dry_run_plan.get('plan', {}).get('protocol_hash') == envelope.get('protocol_hash'),
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
    from research.research_os.engines.protocol import validate_engine_output
    try:
        validate_engine_output(engine_output)
        bound = True
    except (ValueError, KeyError, TypeError, AttributeError):
        bound = False
    executed = True
    if evidence is not None:
        evidence = evidence if isinstance(evidence, dict) else {}
        from research.research_os.engines.protocol import EngineContext
        from research.research_os.engines.builtin import ENGINE_REGISTRY
        from .archaeology import EdgeArchaeologyEngine
        try:
            source = {'source_ref':evidence['packet']['source_ref'],
                      'documentary_packet':evidence['packet'], 'freeze_time':evidence['freeze_time']}
            engines = dict(ENGINE_REGISTRY, archaeology=EdgeArchaeologyEngine())
            engine_key = next(key for key, engine in engines.items()
                              if engine.engine_id == engine_output['engine_id'] and engine.family == engine_output['engine_family'])
            if engine_key == 'archaeology':
                source['hypothesis_id'] = candidate['hypothesis_id']
            rebuilt = engines[engine_key].run(source, EngineContext('VALIDATOR-DOCUMENTARY', synthetic_only=engine_output['synthetic_only']))
            bound = bound and rebuilt == engine_output
            bound = bound and sha256_json([{'engine_key':engine_key, 'source':source}]) == dry_run_plan.get('plan', {}).get('dataset_manifest_hash')
            from .source_qualification import qualify_source_route
            for qualified in sources:
                route = qualified.get('canonical_route', {})
                replayed = qualify_source_route(route, freeze_time=evidence['freeze_time'])
                bound = bound and qualified == replayed
                bound = bound and route.get('route_id') == evidence['packet']['content_hash']
                bound = bound and route.get('locator') == evidence['packet']['source_ref']
                bound = bound and route.get('availability_start') == evidence['packet']['available_at']
            bound = bound and dry_run_plan.get('plan', {}).get('source_route_hashes') == sorted(q['route_hash'] for q in sources)

        except (ValueError, KeyError, TypeError, StopIteration, AttributeError):
            bound = False
        run = executed_dry_run if isinstance(executed_dry_run, dict) else {}
        packet = evidence.get("packet")
        packet_class = packet.get("evidence_class") if isinstance(packet, dict) else None
        receipt_payload = {k: v for k, v in run.items() if k != 'execution_receipt_hash'}
        executed = (run.get('state') == 'EXECUTED_DRY_RUN'
                    and run.get('execution_plan_hash') == dry_run_plan.get('execution_plan_hash')
                    and run.get('input_hash') == dry_run_plan.get('plan', {}).get('dataset_manifest_hash')
                    and run.get('execution_receipt_hash') == sha256_json(receipt_payload)
                    and engine_output in run.get('records', [])
                    and run.get('outcome_accessed') is False
                    and run.get('economic_result') == 'NOT_OBSERVED'
                    and run.get('evidence_class') == packet_class)
    add('documentary_evidence_bound', bound, 'Typed documentary facts must reproduce the frozen candidate.')
    add('executed_documentary_transform', executed, 'A documentary plan alone is not an executed dry-run.')

    dossier = None
    if engine_output.get('synthetic_only') is False:
        from .engine_dossiers_v1 import build_engine_dossier
        dossier = build_engine_dossier(engine_output)
        supplied = envelope.get('dry_run_execution', {}).get('dossier')
        add('documentary_dossier_bound', dossier.get('factual_binding_status') == 'PASS' and supplied == dossier,
            'Reconstruct dossier from the registered producer and compare the entire supplied artifact.')
        add('documentary_dossier_sufficient', dossier['status'] == 'PASS',
            'Factual arithmetic or filled sections cannot qualify missing economic premises.')
        add('documentary_disconfirmation_supported',
            dossier.get('dossier', {}).get('disconfirmation_checks', {}).get('status') == 'SUPPORTED',
            'Disconfirmation must bind to the frozen candidate, not caller prose.')

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
        "dossier_hash": dossier.get('dossier_hash') if dossier else None,
        "dossier_blockers": dossier['blockers'] if dossier else [],
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


def _trial_accounting_identity_matches_candidate(readiness_bundle: Dict[str, Any]) -> tuple[bool, str]:
    """Bind optional enriched trial-accounting lineage to the frozen candidate.

    Legacy CP069 packages do not carry lineage fields in ``trial_accounting`` and
    remain valid.  Once either lineage field is present, both become mandatory
    and must exactly match the candidate identity.  This closes the convergence
    seam exposed by Factory-style enriched trial accounting without importing
    the rest of Factory on this historical diagnostic branch.
    """
    candidate = readiness_bundle.get("candidate")
    trial = readiness_bundle.get("trial_accounting")
    if not isinstance(candidate, dict) or not isinstance(trial, dict):
        return True, "Core readiness validation owns missing candidate/trial structure."

    keys = ("hypothesis_id", "generation_id")
    present = tuple(key in trial for key in keys)
    if not any(present):
        return True, "Legacy trial accounting carries no lineage identity."
    if not all(present):
        return False, "Enriched trial accounting must carry hypothesis_id and generation_id together."
    if any(not isinstance(trial.get(key), str) or not trial[key].strip() for key in keys):
        return False, "Enriched trial-accounting lineage identifiers must be non-empty strings."
    if any(trial.get(key) != candidate.get(key) for key in keys):
        return False, "Trial-accounting lineage must exactly match the frozen candidate identity."
    return True, "Trial-accounting lineage matches the frozen candidate identity."


def validator_economic_readiness_v3(*, readiness_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Primary validator entry point for a future frozen economic-test package."""
    from .validation_readiness import validate_economic_test_readiness

    receipt = validate_economic_test_readiness(readiness_bundle)
    identity_ok, identity_detail = _trial_accounting_identity_matches_candidate(readiness_bundle)
    if identity_ok:
        return receipt

    # Preserve the existing public check/reason vocabulary.  This is an identity
    # invariant inside trial accounting, not a new authorization surface.
    check = receipt.setdefault("checks", {}).setdefault("trial_accounting", {})
    check.update({
        "status": "FAIL",
        "reason_code": "TRIAL_ACCOUNTING_INVALID",
        "detail": identity_detail,
    })
    reasons = receipt.setdefault("block_reasons", [])
    if not any(reason.get("check") == "trial_accounting" for reason in reasons if isinstance(reason, dict)):
        reasons.append({
            "code": "TRIAL_ACCOUNTING_INVALID",
            "check": "trial_accounting",
            "detail": identity_detail,
        })
    receipt["status"] = "BLOCK"
    receipt["ready_for_authorized_economic_test"] = False
    receipt["claim_ceiling"] = "BLOCKED_PRE_OUTCOME"
    return receipt
