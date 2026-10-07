"""Identity derivation through the reviewed harness functions ("voie H").

A frozen-content document is converted into the exact harness dataclass and
its identity is computed by the unchanged H function:
``input_manifest_identity``, ``output_manifest_identity`` or
``harness_policy_identity``. This module never calls an ``evaluate_*`` method,
never resolves, injects or builds a trusted root, and writes nothing.

Frozen-content document format (see FROZEN_CONTENT_FORMAT.md):
``{"schema": "A2_FROZEN_CONTENT_V1", "kind": <kind>, "fields": {...}}`` where
enum fields hold their ``.value`` string, tuples are JSON arrays, recipient
pairs are ``[actor_id, role_value]`` arrays and ``None`` is JSON ``null``.
"""
from __future__ import annotations

from dataclasses import fields as dataclass_fields
import json
from pathlib import Path
import sys

SCHEMA = "A2_FROZEN_CONTENT_V1"
KINDS = ("InputManifest", "OutputManifest", "HarnessPolicy")


class FrozenContentError(ValueError):
    """The document does not match the exact frozen-content format."""


def _text(value, name):
    if type(value) is not str:
        raise FrozenContentError(f"{name}:STRING_REQUIRED")
    return value


def _enum(enum_type, value, name):
    if type(value) is not str:
        raise FrozenContentError(f"{name}:ENUM_VALUE_STRING_REQUIRED")
    try:
        return enum_type(value)
    except ValueError as error:
        raise FrozenContentError(f"{name}:UNKNOWN_ENUM_VALUE") from error


def _text_tuple(value, name):
    if type(value) is not list:
        raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
    return tuple(_text(item, name) for item in value)


def _enum_tuple(enum_type, value, name):
    if type(value) is not list:
        raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
    return tuple(_enum(enum_type, item, name) for item in value)


def _null_only(value, name):
    if value is not None:
        raise FrozenContentError(f"{name}:ONLY_NULL_SUPPORTED_IN_THIS_MODE")
    return None


def _recipient_pairs(api, value, name):
    if type(value) is not list:
        raise FrozenContentError(f"{name}:ARRAY_REQUIRED")
    pairs = []
    for item in value:
        if type(item) is not list or len(item) != 2:
            raise FrozenContentError(f"{name}:PAIR_REQUIRED")
        pairs.append((_text(item[0], name), _enum(api.Role, item[1], name)))
    return tuple(pairs)


def _converters(api, kind):
    if kind == "InputManifest":
        return api.InputManifest, {
            "input_id": _text,
            "manifest_version_identity": _text,
            "input_classification": lambda v, n: _enum(api.InputClassification, v, n),
            "source_provenance_class": _text,
            "exact_permitted_fields": _text_tuple,
            "exact_prohibited_fields": _text_tuple,
            "permitted_reader_roles": lambda v, n: _enum_tuple(api.Role, v, n),
            "raw_values_visible": lambda v, n: _enum(api.VisibilityState, v, n),
            "timestamps_visible": lambda v, n: _enum(api.VisibilityState, v, n),
            "frequency_or_count_information_visible": lambda v, n: _enum(api.VisibilityState, v, n),
            "longitudinal_observation_allowed": lambda v, n: _enum(api.PermissionState, v, n),
            "aggregation_allowed": lambda v, n: _enum(api.PermissionState, v, n),
            "cross_source_comparison_allowed": lambda v, n: _enum(api.PermissionState, v, n),
            "efficacy_leakage_assessment": lambda v, n: _enum(api.LeakageAssessment, v, n),
            "access_logging_requirement": lambda v, n: _enum(api.RequirementState, v, n),
            "quarantine_on_ambiguity": lambda v, n: _enum(api.RequirementState, v, n),
            "owner_approval_required": lambda v, n: _enum(api.RequirementState, v, n),
        }
    if kind == "OutputManifest":
        return api.OutputManifest, {
            "output_id": _text,
            "manifest_version_identity": _text,
            "output_type": _text,
            "exact_metric_or_artifact": _text,
            "granularity": _text,
            "permitted_recipients": lambda v, n: _enum_tuple(api.Role, v, n),
            "exportability": lambda v, n: _enum(api.PermissionState, v, n),
            "quarantine_status": lambda v, n: _enum(api.QuarantineState, v, n),
            "cumulative_disclosure_risk": lambda v, n: _enum(api.CumulativeDisclosureState, v, n),
            "efficacy_leakage_assessment": lambda v, n: _enum(api.LeakageAssessment, v, n),
            "release_approval_requirement": lambda v, n: _enum(api.RequirementState, v, n),
            "retention_rule": _text,
            "incident_if_unexpected_information_revealed": _text,
        }
    if kind == "HarnessPolicy":
        return api.HarnessPolicy, {
            "expected_owner_authority_sha": _text,
            "expected_harness_identity": _text,
            "expected_harness_version_or_commit_identity": _text,
            "expected_manifest_version_identity": _text,
            "expected_input_manifest_id": _text,
            "expected_input_manifest_identity": _text,
            "expected_output_manifest_id": _text,
            "expected_output_manifest_identity": _text,
            "allowed_input_classifications": lambda v, n: _enum_tuple(api.InputClassification, v, n),
            "prohibited_input_classifications": lambda v, n: _enum_tuple(api.InputClassification, v, n),
            "fixture_provenance_contract": _null_only,
            "permitted_recipient_actor_roles": lambda v, n: _recipient_pairs(api, v, n),
        }
    raise FrozenContentError("UNKNOWN_KIND")


def build_object(api, document):
    """Return the exact harness dataclass described by ``document``."""
    if type(document) is not dict or set(document) != {"schema", "kind", "fields"}:
        raise FrozenContentError("DOCUMENT_KEYS_MUST_BE_SCHEMA_KIND_FIELDS")
    if document["schema"] != SCHEMA:
        raise FrozenContentError("UNSUPPORTED_SCHEMA")
    kind = document["kind"]
    if kind not in KINDS:
        raise FrozenContentError("UNKNOWN_KIND")
    target, converters = _converters(api, kind)
    declared = tuple(item.name for item in dataclass_fields(target))
    if set(converters) != set(declared) or len(converters) != len(declared):
        raise FrozenContentError("CONVERTER_SPEC_DIFFERS_FROM_HARNESS_DATACLASS")
    values = document["fields"]
    if type(values) is not dict or set(values) != set(declared):
        raise FrozenContentError("FIELDS_MUST_MATCH_HARNESS_DATACLASS_EXACTLY")
    return target(**{name: converters[name](values[name], name) for name in declared})


def identity(api, document) -> str:
    """Identity computed by the unchanged H identity function for the kind."""
    obj = build_object(api, document)
    kind = document["kind"]
    if kind == "InputManifest":
        return api.input_manifest_identity(obj)
    if kind == "OutputManifest":
        return api.output_manifest_identity(obj)
    return api.harness_policy_identity(obj)


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
    if len(argv) != 3 or argv[0] != "--repo-root":
        raise SystemExit("usage: identity_via_harness.py --repo-root <root> <frozen.json>")
    sys.path.insert(0, str(Path(argv[1]).resolve()))
    from research.weather_forward.v4 import a2_harness as api
    document = load_document(Path(argv[2]).read_text(encoding="utf-8"))
    print(json.dumps({"kind": document.get("kind"), "identity": identity(api, document),
                      "way": "H"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
