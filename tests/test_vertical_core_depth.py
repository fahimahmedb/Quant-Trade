"""Canonical replay and serializer/guard composition within Research Core."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY, V2ContractError, assert_authority_closed, build_candidate,
    build_epoch_manifest, build_frozen_export_intent, build_negative_memory,
    build_research_trial, build_validator_result,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


BUILDERS = [
    ("epoch", build_epoch_manifest, "epoch_manifest_hash"),
    ("trial", build_research_trial, "trial_hash"),
    ("candidate", build_candidate, "candidate_hash"),
    ("validator", build_validator_result, "validator_hash"),
    ("negative_memory", build_negative_memory, "negative_knowledge_hash"),
    ("export", build_frozen_export_intent, "export_bundle_hash"),
]


def bundle():
    return json.loads((Path(__file__).parent / "fixtures/oracle_v2_core_fixture.json").read_text())


@pytest.mark.parametrize("key,builder,digest", BUILDERS)
def test_canonical_build_survives_serialized_reconstruction(key, builder, digest):
    original = bundle()[key]
    before = deepcopy(original)
    built = builder(original)
    assert original == before
    # Reordering, reconstructing and rebuilding must not create a new identity.
    restored = json.loads(json.dumps(dict(reversed(list(built.items())))))
    for _ in range(3):
        restored = builder(restored)
        assert restored == built
    changed = deepcopy(original)
    changed["fixture_extra"] = {"nested": ["version-drift"]}
    assert builder(changed)[digest] != built[digest]


@pytest.mark.parametrize("sequence", [list, tuple])
@pytest.mark.parametrize("key", ["pnl", "RETURNS", "evaluation_result", "outcome"])
def test_export_guard_covers_nested_json_serializable_sequences(sequence, key):
    payload = bundle()["export"]
    payload["fixture_extra"] = {"layer": sequence([{"layer": sequence([{key: 123}])}])}
    # Python tuples become JSON arrays. Both in-memory and wire forms must block.
    for value in (payload, json.loads(json.dumps(payload))):
        with pytest.raises(V2ContractError, match="OUTCOME_DATA_IN_RESEARCH_EXPORT"):
            build_frozen_export_intent(value)


def test_pipeline_cannot_accept_tuple_hidden_outcome_then_claim_no_outcome_access():
    payload = bundle()
    payload["negative_memory"]["source_context"]["fixture_extra"] = ({"pnl": 123},)
    with pytest.raises(V2ContractError, match="OUTCOME_DATA_VISIBLE_TO_RESEARCH"):
        run_pre_outcome_pipeline(payload)


@pytest.mark.parametrize("value", [None, 0, 1, "false", "FALSE", "true", [], {}, True])
def test_authority_never_coerces_false_like_values(value):
    for key in CLOSED_AUTHORITY:
        authority = dict(CLOSED_AUTHORITY, **{key: value})
        with pytest.raises(V2ContractError):
            assert_authority_closed(authority)


def test_clean_pipeline_stays_closed_after_replay():
    payload = bundle()
    first = run_pre_outcome_pipeline(payload)
    for key, builder, _ in BUILDERS:
        if key != "export":  # AUTO export references are resolved by the pipeline.
            payload[key] = json.loads(json.dumps(builder(payload[key])))
    assert run_pre_outcome_pipeline(payload) == first
    assert first["authority"] == CLOSED_AUTHORITY
    assert first["outcome_accessed"] is False
