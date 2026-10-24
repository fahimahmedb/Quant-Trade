"""Re-prove H-C1 schema handoffs against actual canonical producer output."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from research.research_os.expansion.final_shape import assess_implementability, freeze_experiment_envelope
from research.research_os.tests.test_implementability_depth import _complete_meta, _engine_output


def validator():
    from jsonschema import Draft202012Validator
    path = Path(__file__).resolve().parents[1] / "research/research_os/contracts/expansion-auxiliary.schema.json"
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.mark.parametrize("variant", ["PASS", "PARK", "BLOCK", "source_available", "pit_feasible",
                                     "expression_feasible", "cost_model_feasible", "capacity_observable"])
def test_actual_implementability_states_have_a_wire_representation(variant):
    meta = _complete_meta()
    if variant == "PARK":
        meta["source_available"] = False
    elif variant == "BLOCK":
        meta["cost_model_feasible"] = False
    elif variant != "PASS":
        del meta[variant]
    actual = assess_implementability(_engine_output(), meta)
    restored = json.loads(json.dumps(actual))
    assert not list(validator().iter_errors(restored))


@pytest.mark.parametrize("frozen", [True, False])
def test_frozen_protocol_body_and_null_have_a_wire_representation(frozen):
    output = _engine_output()
    assessment = assess_implementability(output, _complete_meta() if frozen else {})
    envelope = freeze_experiment_envelope(output, assessment, {})
    assert not list(validator().iter_errors(json.loads(json.dumps(envelope))))


def test_wire_extensions_cannot_grant_authority_or_mutation():
    actual = assess_implementability(_engine_output(), _complete_meta())
    for target, key in ((actual, "candidate_mutated"), (actual, "real_capital_authorized"),
                        (actual["authority"], "live_trading_authorized")):
        changed = deepcopy(actual)
        (changed["authority"] if target is actual["authority"] else changed)[key] = True
        assert not validator().is_valid(changed)
