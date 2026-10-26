"""JSON-equivalent containers must agree at the pre-outcome membrane."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY, FORBIDDEN_OUTCOME_KEYS, V2ContractError,
    build_frozen_export_intent, canonical_hash,
)
from research.research_os.expansion.v2_pipeline import (
    _FORBIDDEN_RESEARCH_KEYS, run_pre_outcome_pipeline,
)


class SerializableOutcomeMembraneTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())

    def test_pipeline_refuses_nested_mixed_array_contamination_before_export(self):
        for key in sorted(_FORBIDDEN_RESEARCH_KEYS):
            for wrap in (lambda v: (v,), lambda v: [({'inner': (v,)},)],
                         lambda v: (([v],),)):
                for location in ('export', 'ignored_metadata'):
                    with self.subTest(key=key, location=location, wrap=wrap):
                        bundle = self.bundle()
                        value = wrap({key.upper(): 'SYNTHETIC_MEMBRANE_MARKER'})
                        if location == 'export':
                            bundle['export']['review_context'] = value
                        else:
                            bundle[location] = value
                        before = deepcopy(bundle)
                        with patch('research.research_os.expansion.v2_pipeline.build_frozen_export_intent') as export:
                            with self.assertRaisesRegex(V2ContractError, 'OUTCOME_DATA_VISIBLE_TO_RESEARCH:.*' + key.upper()):
                                run_pre_outcome_pipeline(bundle)
                            export.assert_not_called()
                        self.assertEqual(bundle, before)

    def test_direct_export_preserves_its_full_forbidden_vocabulary_for_tuples(self):
        for key in sorted(FORBIDDEN_OUTCOME_KEYS):
            with self.subTest(key=key):
                payload = self.bundle()['export']
                payload['review_context'] = ({'notes': ([{key: 'SYNTHETIC_MEMBRANE_MARKER'}],)},)
                before = deepcopy(payload)
                with self.assertRaisesRegex(V2ContractError, 'OUTCOME_DATA_IN_RESEARCH_EXPORT:.*' + key):
                    build_frozen_export_intent(payload)
                self.assertEqual(payload, before)

    def test_actual_reproduction_and_json_round_trip_have_identical_denial(self):
        bundle = self.bundle()
        bundle['export']['review_context'] = ({'outcome': 'SYNTHETIC_MEMBRANE_MARKER'},)
        normalized = json.loads(json.dumps(bundle))
        self.assertEqual(canonical_hash(bundle), canonical_hash(normalized))
        for value in (bundle, normalized):
            with self.assertRaisesRegex(V2ContractError, 'OUTCOME_DATA_VISIBLE_TO_RESEARCH:.*review_context\\[0\\].outcome'):
                run_pre_outcome_pipeline(value)
            with self.assertRaisesRegex(V2ContractError, 'OUTCOME_DATA_IN_RESEARCH_EXPORT:.*review_context\\[0\\].outcome'):
                build_frozen_export_intent(value['export'])

    def test_benign_json_arrays_replay_identically_without_hash_or_authority_changes(self):
        bundle = self.bundle()
        result = run_pre_outcome_pipeline(bundle)
        self.assertEqual(result['receipt_hash'], '48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8')
        # Literal text is not a forbidden field; do not add heuristic string scans.
        bundle['export']['review_context'] = ({'notes': ('outcome', ['DECLARED_ONLY'])},)
        before = deepcopy(bundle)
        normalized = json.loads(json.dumps(bundle))
        self.assertEqual(canonical_hash(bundle), canonical_hash(normalized))
        self.assertEqual(build_frozen_export_intent(bundle['export'])['export_bundle_hash'],
                         build_frozen_export_intent(normalized['export'])['export_bundle_hash'])
        actual = run_pre_outcome_pipeline(bundle)
        self.assertEqual(actual, run_pre_outcome_pipeline(normalized))
        self.assertEqual(actual['authority'], CLOSED_AUTHORITY)
        self.assertFalse(actual['outcome_accessed'])
        self.assertFalse(actual['economic_claim_authorized'])
        self.assertEqual(bundle, before)


if __name__ == '__main__':
    unittest.main()
