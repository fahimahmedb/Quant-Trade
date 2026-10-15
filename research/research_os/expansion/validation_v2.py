from __future__ import annotations

from typing import Any, Dict, Iterable, List


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
) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    sources = list(source_qualifications)
    checks: Dict[str, Dict[str, Any]] = {}

    def add(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"status": "PASS" if passed else "FAIL", "detail": detail}

    add(
        "producer_independence",
        bool(validation_v1.get("independent_from_producer"))
        and validation_v1.get("producer_engine") != validation_v1.get("validator"),
        "Validator identity must differ from producing engine.",
    )
    add(
        "protocol_frozen",
        envelope.get("status") == "FROZEN_READY_NO_OUTCOME" and bool(envelope.get("protocol_hash")),
        "Protocol hash must exist before any outcome access.",
    )
    add(
        "source_pit",
        bool(sources) and all(item.get("point_in_time_qualified") is True for item in sources),
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
        and bool(dry_run_plan.get("execution_plan_hash")),
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
        trial_record.get("observed_attempt_count") is not None
        and trial_record.get("effective_trials_status") in {"KNOWN", "UNKNOWN"},
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
