#!/usr/bin/env python3
"""Mechanical proof that a material AI PASS is recoverable from the canonical router.

This extends the existing AI Working Method Gate. It does not create a new
router or memory surface: it verifies that FINAL_HANDOFF completions are
actually published in governance/CURRENT_PROJECT_STATE.md. CHECKPOINT is a
qualified intermediate result and may not claim authoritative PASS.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping


class DurableContinuationError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise DurableContinuationError(f"{path}: expected JSON object")
    return data


def _missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _router_assignment(router_text: str, key: str) -> str | None:
    match = re.search(rf"`{re.escape(key)}=([^`\n]+)`", router_text)
    return match.group(1).strip() if match else None


def validate_durable_continuation(
    contract: Mapping[str, Any],
    admission: Mapping[str, Any],
    completion: Mapping[str, Any],
    *,
    current_router_identity: str,
    router_text: str,
) -> list[str]:
    cfg = contract.get("durable_continuation")
    if cfg is None:
        return []
    if not isinstance(cfg, Mapping) or cfg.get("enabled") is not True:
        return ["INVALID_DURABLE_CONTINUATION_CONTRACT"]

    errors: list[str] = []
    if cfg.get("canonical_router") != "governance/CURRENT_PROJECT_STATE.md":
        errors.append("INVALID_DURABLE_CONTINUATION_ROUTER")
    if cfg.get("admission_field") != "completion_intent":
        errors.append("INVALID_DURABLE_CONTINUATION_ADMISSION_FIELD")

    allowed = cfg.get("allowed_intents")
    if allowed != ["CHECKPOINT", "FINAL_HANDOFF"]:
        errors.append("INVALID_DURABLE_CONTINUATION_INTENTS")

    required_fields = set(contract.get("mission_admission", {}).get("required_fields", []))
    if "completion_intent" not in required_fields:
        errors.append("COMPLETION_INTENT_NOT_REQUIRED_BY_ADMISSION")

    intent = admission.get("completion_intent")
    if intent not in {"CHECKPOINT", "FINAL_HANDOFF"}:
        errors.append("INVALID_COMPLETION_INTENT")
        return errors

    checkpoint_claim = str(cfg.get("checkpoint_claim") or "CHECKPOINT")
    final_claim = str(cfg.get("final_handoff_claim") or "PASS")

    if intent == "CHECKPOINT":
        if completion.get("claim") != checkpoint_claim:
            errors.append("CHECKPOINT_CANNOT_CLAIM_PASS")
        return errors

    for field in ("handoff_result", "handoff_subject_sha", "handoff_reopen_condition"):
        if _missing(admission.get(field)):
            errors.append(f"MISSING_{field.upper()}")

    if completion.get("claim") != final_claim:
        errors.append("FINAL_HANDOFF_MUST_CLAIM_PASS")
    if completion.get("durable_remote_output") is not True:
        errors.append("FINAL_HANDOFF_NOT_DURABLE")

    expected_completion = {
        "handoff_router_identity": current_router_identity,
        "handoff_mission_id": admission.get("mission_id"),
        "handoff_result": admission.get("handoff_result"),
        "handoff_subject_sha": admission.get("handoff_subject_sha"),
        "handoff_next_action": admission.get("next_action_after_pass_fail_block"),
        "handoff_reopen_condition": admission.get("handoff_reopen_condition"),
    }
    for field, expected in expected_completion.items():
        if _missing(completion.get(field)):
            errors.append(f"MISSING_{field.upper()}")
        elif completion.get(field) != expected:
            errors.append(f"{field.upper()}_MISMATCH")

    markers = cfg.get("router_markers")
    if not isinstance(markers, Mapping):
        errors.append("MISSING_DURABLE_CONTINUATION_ROUTER_MARKERS")
        return errors

    router_expected = {
        "mission_id": admission.get("mission_id"),
        "result": admission.get("handoff_result"),
        "subject_sha": admission.get("handoff_subject_sha"),
        "next_action": admission.get("next_action_after_pass_fail_block"),
        "reopen_condition": admission.get("handoff_reopen_condition"),
    }
    for semantic, expected in router_expected.items():
        marker = markers.get(semantic)
        if not marker:
            errors.append(f"MISSING_ROUTER_MARKER_CONFIG_{semantic.upper()}")
            continue
        observed = _router_assignment(router_text, str(marker))
        if observed != str(expected):
            errors.append(f"CANONICAL_HANDOFF_{semantic.upper()}_MISMATCH")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("admission")
    parser.add_argument("completion")
    parser.add_argument("--router-file", required=True)
    parser.add_argument("--current-router-identity", required=True)
    args = parser.parse_args()

    contract = load_json(args.contract)
    admission = load_json(args.admission)
    completion = load_json(args.completion)
    router_text = Path(args.router_file).read_text(encoding="utf-8")

    errors = validate_durable_continuation(
        contract,
        admission,
        completion,
        current_router_identity=args.current_router_identity,
        router_text=router_text,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    if contract.get("durable_continuation") is None:
        print("DURABLE_CONTINUATION_GATE=LEGACY_NOT_ENABLED")
    else:
        print("DURABLE_CONTINUATION_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
