"""Independent identity recomputation with the standard library only ("voie indépendante").

This module must not import the harness, ``identity_via_harness`` or any
harness canonicalization helper. It re-derives the canonical payload directly
from a frozen-content JSON document using its own field and enum-value
specification, written from the reviewed H recipe (harness.py, lines 149-261):

* discriminator ``manifest_kind`` (InputManifest, OutputManifest) or
  ``contract_kind`` (HarnessPolicy);
* every dataclass field under its exact name;
* enum fields as their value strings;
* string and enum-value lists sorted, duplicates kept;
* recipient pairs as ``[actor_id, role_value]`` sorted by (actor_id, role_value);
* ``fixture_provenance_contract`` as JSON null (only null is supported here);
* ``json.dumps(ensure_ascii=True, separators=(",", ":"), sort_keys=True)``,
  UTF-8, SHA-256, prefix ``sha256:``.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "A2_FROZEN_CONTENT_V1"

ENUM_VALUES = {
    "InputClassification": frozenset({"DOCUMENTATION_ONLY", "NON_ECONOMIC_SYNTHETIC",
                                      "REAL_TECHNICAL_METADATA", "PROHIBITED", "UNKNOWN"}),
    "Role": frozenset({"PHASE_OWNER", "EXECUTOR", "CUSTODY_ADMIN", "RESEARCH_VIEWER",
                       "RELEASE_APPROVER", "INCIDENT_AUTHORITY"}),
    "VisibilityState": frozenset({"VISIBLE", "HIDDEN", "UNRESOLVED"}),
    "PermissionState": frozenset({"ALLOWED", "DENIED", "UNRESOLVED"}),
    "LeakageAssessment": frozenset({"CLEAR", "UNRESOLVED", "BLOCKED"}),
    "RequirementState": frozenset({"REQUIRED", "NOT_REQUIRED", "UNRESOLVED"}),
    "QuarantineState": frozenset({"CLEAR", "QUARANTINED", "BLOCKED_PENDING_OWNER_REVIEW"}),
    "CumulativeDisclosureState": frozenset({"CLEAR", "UNRESOLVED", "BLOCKED"}),
}

# (field name, rule). Rules: "text", ("enum", E), ("text_list",), ("enum_list", E),
# ("null",), ("pairs",).
SPECS = {
    "InputManifest": ("manifest_kind", (
        ("input_id", ("text",)),
        ("manifest_version_identity", ("text",)),
        ("input_classification", ("enum", "InputClassification")),
        ("source_provenance_class", ("text",)),
        ("exact_permitted_fields", ("text_list",)),
        ("exact_prohibited_fields", ("text_list",)),
        ("permitted_reader_roles", ("enum_list", "Role")),
        ("raw_values_visible", ("enum", "VisibilityState")),
        ("timestamps_visible", ("enum", "VisibilityState")),
        ("frequency_or_count_information_visible", ("enum", "VisibilityState")),
        ("longitudinal_observation_allowed", ("enum", "PermissionState")),
        ("aggregation_allowed", ("enum", "PermissionState")),
        ("cross_source_comparison_allowed", ("enum", "PermissionState")),
        ("efficacy_leakage_assessment", ("enum", "LeakageAssessment")),
        ("access_logging_requirement", ("enum", "RequirementState")),
        ("quarantine_on_ambiguity", ("enum", "RequirementState")),
        ("owner_approval_required", ("enum", "RequirementState")),
    )),
    "OutputManifest": ("manifest_kind", (
        ("output_id", ("text",)),
        ("manifest_version_identity", ("text",)),
        ("output_type", ("text",)),
        ("exact_metric_or_artifact", ("text",)),
        ("granularity", ("text",)),
        ("permitted_recipients", ("enum_list", "Role")),
        ("exportability", ("enum", "PermissionState")),
        ("quarantine_status", ("enum", "QuarantineState")),
        ("cumulative_disclosure_risk", ("enum", "CumulativeDisclosureState")),
        ("efficacy_leakage_assessment", ("enum", "LeakageAssessment")),
        ("release_approval_requirement", ("enum", "RequirementState")),
        ("retention_rule", ("text",)),
        ("incident_if_unexpected_information_revealed", ("text",)),
    )),
    "HarnessPolicy": ("contract_kind", (
        ("expected_owner_authority_sha", ("text",)),
        ("expected_harness_identity", ("text",)),
        ("expected_harness_version_or_commit_identity", ("text",)),
        ("expected_manifest_version_identity", ("text",)),
        ("expected_input_manifest_id", ("text",)),
        ("expected_input_manifest_identity", ("text",)),
        ("expected_output_manifest_id", ("text",)),
        ("expected_output_manifest_identity", ("text",)),
        ("allowed_input_classifications", ("enum_list", "InputClassification")),
        ("prohibited_input_classifications", ("enum_list", "InputClassification")),
        ("fixture_provenance_contract", ("null",)),
        ("permitted_recipient_actor_roles", ("pairs",)),
    )),
}


class FrozenContentError(ValueError):
    """The document does not match the exact frozen-content format."""


def _text(value, name):
    if type(value) is not str:
        raise FrozenContentError(f"{name}:STRING_REQUIRED")
    return value


def _enum_value(enum_name, value, name):
    if type(value) is not str or value not in ENUM_VALUES[enum_name]:
        raise FrozenContentError(f"{name}:UNKNOWN_{enum_name}_VALUE")
    return value


def _canonical_field(rule, value, name):
    kind = rule[0]
    if kind == "text":
        return _text(value, name)
    if kind == "enum":
        return _enum_value(rule[1], value, name)
    if kind == "text_list":
        if type(value) is not list:
            raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
        return sorted(_text(item, name) for item in value)
    if kind == "enum_list":
        if type(value) is not list:
            raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
        return sorted(_enum_value(rule[1], item, name) for item in value)
    if kind == "null":
        if value is not None:
            raise FrozenContentError(f"{name}:ONLY_NULL_SUPPORTED_IN_THIS_MODE")
        return None
    if kind == "pairs":
        if type(value) is not list:
            raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
        pairs = []
        for item in value:
            if type(item) is not list or len(item) != 2:
                raise FrozenContentError(f"{name}:PAIR_REQUIRED")
            pairs.append([_text(item[0], name), _enum_value("Role", item[1], name)])
        return sorted(pairs, key=lambda pair: (pair[0], pair[1]))
    raise FrozenContentError(f"{name}:UNKNOWN_RULE")


def canonical_payload(document) -> dict:
    if type(document) is not dict or set(document) != {"schema", "kind", "fields"}:
        raise FrozenContentError("DOCUMENT_KEYS_MUST_BE_SCHEMA_KIND_FIELDS")
    if document["schema"] != SCHEMA:
        raise FrozenContentError("UNSUPPORTED_SCHEMA")
    kind = document["kind"]
    if kind not in SPECS:
        raise FrozenContentError("UNKNOWN_KIND")
    discriminator, spec = SPECS[kind]
    values = document["fields"]
    names = tuple(name for name, _ in spec)
    if type(values) is not dict or set(values) != set(names):
        raise FrozenContentError("FIELDS_MUST_MATCH_SPEC_EXACTLY")
    payload = {discriminator: kind}
    for name, rule in spec:
        payload[name] = _canonical_field(rule, values[name], name)
    return payload


def digest(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, separators=(",", ":"),
                         sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def identity(document) -> str:
    return digest(canonical_payload(document))


def load_document(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise FrozenContentError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def reject_constant(value):
        raise FrozenContentError("NON_JSON_NUMBER")
    return json.loads(text, object_pairs_hook=unique, parse_constant=reject_constant)


def main(argv) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: identity_stdlib.py <frozen.json>")
    document = load_document(Path(argv[0]).read_text(encoding="utf-8"))
    print(json.dumps({"kind": document.get("kind"), "identity": identity(document),
                      "way": "STDLIB"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
