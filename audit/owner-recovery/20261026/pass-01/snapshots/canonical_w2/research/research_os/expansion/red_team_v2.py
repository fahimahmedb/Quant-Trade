from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


ALLOWED_BLOCKERS = {
    "BLOCK_DATA",
    "BLOCK_LEAKAGE",
    "BLOCK_CLOCK",
    "BLOCK_PIT",
    "BLOCK_MULTIPLICITY",
    "BLOCK_TRIAL_ACCOUNTING",
    "BLOCK_IMPLEMENTABILITY",
    "BLOCK_COST_MODEL",
    "BLOCK_CAPACITY",
    "BLOCK_CLAIM_LEVEL",
    "BLOCK_REPRODUCIBILITY",
    "BLOCK_ECONOMIC_IDENTITY",
    "BLOCK_PORTFOLIO_DUPLICATION",
}

CHECK_TO_BLOCKER = {
    "candidate_immutability": "BLOCK_REPRODUCIBILITY",
    "producer_independence": "BLOCK_CLAIM_LEVEL",
    "legacy_screening_evidence": "BLOCK_CLAIM_LEVEL",
    "source_provenance": "BLOCK_DATA",
    "pit": "BLOCK_PIT",
    "clock": "BLOCK_CLOCK",
    "universe_definition": "BLOCK_DATA",
    "economic_expression_completeness": "BLOCK_ECONOMIC_IDENTITY",
    "implementability_declaration": "BLOCK_IMPLEMENTABILITY",
    "protocol_freeze": "BLOCK_REPRODUCIBILITY",
    "reproducibility_binding": "BLOCK_REPRODUCIBILITY",
    "multiplicity_declaration": "BLOCK_MULTIPLICITY",
    "trial_accounting": "BLOCK_TRIAL_ACCOUNTING",
    "cost_model_declaration": "BLOCK_COST_MODEL",
    "capacity_declaration": "BLOCK_CAPACITY",
    "falsification": "BLOCK_CLAIM_LEVEL",
    "decision_map": "BLOCK_CLAIM_LEVEL",
    "no_outcome_access": "BLOCK_LEAKAGE",
}


def red_team_negative_rights_v2(
    validator_receipt: Dict[str, Any],
    *,
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Exercise negative rights only against a pre-outcome validator receipt."""
    receipt_before = deepcopy(validator_receipt)
    context = context if isinstance(context, dict) else {}
    blocks: List[str] = []

    checks = validator_receipt.get("checks")
    if not isinstance(checks, dict):
        blocks.append("BLOCK_CLAIM_LEVEL")
        checks = {}

    for check, blocker in CHECK_TO_BLOCKER.items():
        record = checks.get(check)
        if not isinstance(record, dict) or record.get("status") != "PASS":
            blocks.append(blocker)

    if validator_receipt.get("status") not in {"READY_FOR_AUTHORIZED_ECONOMIC_TEST", "BLOCK"}:
        blocks.append("BLOCK_CLAIM_LEVEL")

    if context.get("data_integrity_status") == "FAIL":
        blocks.append("BLOCK_DATA")
    if context.get("leakage_status") == "FAIL":
        blocks.append("BLOCK_LEAKAGE")
    if context.get("clock_status") == "FAIL":
        blocks.append("BLOCK_CLOCK")
    if context.get("pit_status") == "FAIL":
        blocks.append("BLOCK_PIT")
    if context.get("economic_identity_status") == "FAIL":
        blocks.append("BLOCK_ECONOMIC_IDENTITY")
    if context.get("portfolio_duplication_status") == "FAIL":
        blocks.append("BLOCK_PORTFOLIO_DUPLICATION")

    blocks = sorted(set(blocks))
    if not set(blocks) <= ALLOWED_BLOCKERS:
        raise ValueError("Red Team emitted a blocker outside its negative-rights contract.")

    mutated = validator_receipt != receipt_before
    return {
        "hypothesis_id": validator_receipt.get("hypothesis_id"),
        "generation_id": validator_receipt.get("generation_id"),
        "red_team": "red-team.v2",
        "status": "PASS" if not blocks else "BLOCK",
        "negative_rights": blocks,
        "repair_attempted": False,
        "signal_repair_attempted": False,
        "candidate_mutated": False,
        "validator_receipt_mutated": mutated,
        "parameters_optimized": False,
        "outcomes_opened": False,
        "retuned_until_profitable": False,
        "economic_test_authorized": False,
        "capital_authorized": False,
    }
