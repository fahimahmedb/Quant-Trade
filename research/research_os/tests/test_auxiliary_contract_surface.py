"""Actual producer outputs must fit their durable auxiliary contracts.

Install development requirements from requirements-contract-tests.txt. These tests
exercise the published JSON Schema with a complete Draft 2020-12 validator rather
than treating required-key inclusion as schema qualification.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from research.research_os.expansion.final_shape import (
    assess_implementability,
    freeze_experiment_envelope,
    run_aggressive_pipeline,
)
from research.research_os.tests.test_implementability_depth import _complete_meta, _engine_output


BASE = Path(__file__).resolve().parents[1]


class AuxiliaryContractSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((BASE / 'contracts/expansion-auxiliary.schema.json').read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def assert_admitted(self, value):
        # Exercise a real durable JSON round trip, not a separate schema-shaped fixture.
        restored = json.loads(json.dumps(value, allow_nan=False))
        errors = list(self.validator.iter_errors(restored))
        self.assertEqual(errors, [], '\n'.join(str(error) for error in errors))
        self.assertEqual(restored, value)

    def test_pass_park_block_and_unknown_implementability_outputs_are_representable(self):
        variants = (
            ('PASS', _complete_meta()),
            ('PARK_IMPLEMENTABILITY', dict(_complete_meta(), source_available=False)),
            ('BLOCK_IMPLEMENTABILITY', dict(_complete_meta(), cost_model_feasible=False)),
            ('BLOCK_IMPLEMENTABILITY', {}),
        )
        for expected, meta in variants:
            with self.subTest(expected=expected, meta=meta):
                result = assess_implementability(_engine_output(), meta)
                self.assertEqual(result['status'], expected)
                self.assert_admitted(result)

    def test_every_unknown_feasibility_family_has_a_durable_schema_representation(self):
        for field in ('source_available', 'pit_feasible', 'expression_feasible',
                      'cost_model_feasible', 'capacity_observable'):
            with self.subTest(field=field):
                meta = _complete_meta()
                del meta[field]
                result = assess_implementability(_engine_output(), meta)
                self.assertEqual(result[field], 'UNKNOWN')
                self.assertEqual(result['status'], 'BLOCK_IMPLEMENTABILITY')
                self.assert_admitted(result)

    def test_frozen_and_not_frozen_envelopes_preserve_protocol_body_representation(self):
        for meta in (_complete_meta(), {}):
            with self.subTest(meta=meta):
                assessment = assess_implementability(_engine_output(), meta)
                envelope = freeze_experiment_envelope(_engine_output(), assessment, {})
                self.assertIn('protocol_payload', envelope)
                if assessment['status'] == 'PASS':
                    self.assertIsInstance(envelope['protocol_payload'], dict)
                    self.assertEqual(envelope['protocol_payload']['candidate'], _engine_output()['candidate'])
                else:
                    self.assertIsNone(envelope['protocol_payload'])
                self.assert_admitted(envelope)

    def test_all_registered_auxiliary_producer_families_validate(self):
        fixture = json.loads((BASE / 'simulations/aggressive_architecture_fixture.json').read_text())
        result = run_aggressive_pipeline(fixture)
        for family in ('implementability', 'experiment_envelopes', 'forward_farm'):
            for record in result[family]:
                with self.subTest(family=family, hypothesis=record.get('hypothesis_id')):
                    self.assert_admitted(record)
        self.assert_admitted(result['decay'])

    def test_new_assessment_fields_do_not_admit_authority_or_mutation_claims(self):
        baseline = assess_implementability(_engine_output(), _complete_meta())
        for flag in ('economic_experiment_authorized', 'prospective_observation_authorized',
                     'real_capital_authorized', 'live_trading_authorized'):
            for nested in (False, True):
                with self.subTest(flag=flag, nested=nested):
                    changed = deepcopy(baseline)
                    target = changed['authority'] if nested else changed
                    target[flag] = True
                    self.assertFalse(self.validator.is_valid(changed))
        changed = deepcopy(baseline)
        changed['candidate_mutated'] = True
        self.assertFalse(self.validator.is_valid(changed))
        changed = deepcopy(baseline)
        changed['unsupported_assessment_field'] = 'not a declared surface'
        self.assertFalse(self.validator.is_valid(changed))

    def test_legacy_minimal_records_remain_readable(self):
        assessment = assess_implementability(_engine_output(), _complete_meta())
        envelope = freeze_experiment_envelope(_engine_output(), assessment, {})
        legacy_assessment = {key: assessment[key] for key in (
            'hypothesis_id', 'status', 'source_available', 'pit_feasible',
            'expression_feasible', 'cost_model_feasible', 'capacity_observable',
            'operational_complexity', 'blockers', 'mechanism_rewritten',
            'research_decision_rewritten',
        )}
        legacy_envelope = {key: value for key, value in envelope.items() if key != 'protocol_payload'}
        self.assert_admitted(legacy_assessment)
        self.assert_admitted(legacy_envelope)


if __name__ == '__main__':
    unittest.main()
