#!/usr/bin/env python3
"""Synthetic structural discriminants for the authoritative Gate-B evidence schema.

These fixtures are schema tests only. They are not Gate-B evidence and do not prove
external digest retrievability, global run uniqueness/history, or target-host facts.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - environment/dependency guard
    raise SystemExit(
        "jsonschema is required to run Gate-B evidence-schema discriminants"
    ) from exc


HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "TARGET_HOST_GATE_B_EVIDENCE_SCHEMA_2026-09-21.json"
FIXTURE_PATH = (
    HERE
    / "fixtures"
    / "gate_b_evidence_schema_positive_pass_2026-09-21.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mutate(base: dict, fn) -> dict:
    payload = copy.deepcopy(base)
    fn(payload)
    return payload


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    base = load_json(FIXTURE_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    cases: list[tuple[str, bool, dict]] = [
        (
            "D1_PASS_REVIEW_FAIL",
            False,
            mutate(
                base,
                lambda p: p["independent_review"].__setitem__("verdict", "FAIL"),
            ),
        ),
        (
            "D2_PASS_MISSING_REVIEW_CI_RUNS",
            False,
            mutate(base, lambda p: p["independent_review"].pop("ci_runs")),
        ),
        (
            "D3_PASS_SUB_ARTIFACT_UNKNOWN",
            False,
            mutate(
                base,
                lambda p: p["sub_artifacts"][0].__setitem__(
                    "classification", "UNKNOWN"
                ),
            ),
        ),
        (
            "D4_PASS_SUB_ARTIFACT_REAL_DEFECT",
            False,
            mutate(
                base,
                lambda p: p["sub_artifacts"][0].__setitem__(
                    "defect_classification", "REAL_DEFECT"
                ),
            ),
        ),
        (
            "D5_PASS_SUB_ARTIFACT_MISSING_PROOF",
            False,
            mutate(
                base,
                lambda p: p["sub_artifacts"][0].__setitem__(
                    "defect_classification", "MISSING_PROOF"
                ),
            ),
        ),
        (
            "D6_PASS_MISSING_RESTRICTED_REFERENCE",
            False,
            mutate(base, lambda p: p["sub_artifacts"][0].pop("restricted_reference")),
        ),
        (
            "D7_PASS_EXACT_DUPLICATE_SUB_ARTIFACT",
            False,
            mutate(
                base,
                lambda p: p["sub_artifacts"].append(
                    copy.deepcopy(p["sub_artifacts"][0])
                ),
            ),
        ),
        (
            "C1_MANDATORY_DOMAIN_FAIL",
            False,
            mutate(base, lambda p: p["time_authority"].__setitem__("verdict", "FAIL")),
        ),
        (
            "C2_MANDATORY_DOMAIN_MISSING_PROOF",
            False,
            mutate(
                base,
                lambda p: p["time_authority"].__setitem__(
                    "defect_classification", "MISSING_PROOF"
                ),
            ),
        ),
        (
            "C3_MISSING_MANDATORY_DOMAIN",
            False,
            mutate(base, lambda p: p.pop("time_authority")),
        ),
        (
            "C4_REAL_SEC_REQUEST_COUNT_1",
            False,
            mutate(
                base,
                lambda p: p["synthetic_campaign_network_activity"].__setitem__(
                    "real_sec_requests_made", 1
                ),
            ),
        ),
        (
            "C5_T0_DECLARED_TRUE",
            False,
            mutate(base, lambda p: p.__setitem__("t0_declared", True)),
        ),
        (
            "C6_WRONG_CANDIDATE_SHA",
            False,
            mutate(base, lambda p: p.__setitem__("candidate_sha", "0" * 40)),
        ),
        (
            "C7_WRONG_GIT_TREE",
            False,
            mutate(base, lambda p: p.__setitem__("git_tree", "0" * 40)),
        ),
        (
            "C8_WRONG_INPUT_TREE_DIGEST",
            False,
            mutate(
                base,
                lambda p: p.__setitem__(
                    "verified_input_tree_digest", "sha256:" + "0" * 64
                ),
            ),
        ),
        ("P1_COMPLETE_SYNTHETIC_PASS", True, copy.deepcopy(base)),
    ]

    failures = 0
    print("| case | expected | observed | result |")
    print("| --- | --- | --- | --- |")
    for name, expected_valid, payload in cases:
        observed_valid = validator.is_valid(payload)
        expected = "ACCEPTED" if expected_valid else "REJECTED"
        observed = "ACCEPTED" if observed_valid else "REJECTED"
        result = "PASS" if observed_valid == expected_valid else "FAIL"
        if result == "FAIL":
            failures += 1
        print(f"| {name} | {expected} | {observed} | {result} |")

    if failures:
        print(f"SCHEMA_DISCRIMINANT_SUITE = FAIL ({failures} mismatch(es))")
        return 1

    print("SCHEMA_DISCRIMINANT_SUITE = PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
