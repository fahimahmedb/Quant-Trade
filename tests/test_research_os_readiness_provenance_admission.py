"""Readiness source/actor joins use only synthetic declared metadata."""
from copy import deepcopy
import json
import unittest

from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness
from research.research_os.expansion.validation_readiness import validate_economic_test_readiness, READY
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.tests.test_economic_readiness_validation import _fixture


class ReadinessProvenanceAdmissionTests(unittest.TestCase):
    def assert_direct_block(self, package, code):
        before = deepcopy(package)
        result = validate_economic_test_readiness(package)
        self.assertEqual(result['status'], 'BLOCK')
        self.assertIn(code, [r['code'] for r in result['block_reasons']])
        self.assertFalse(result['economic_test_authorized'])
        self.assertFalse(result['outcome_access_authorized'])
        self.assertEqual(package, before)
        return result

    def test_post_cutoff_route_cannot_hide_behind_older_snapshot_clock(self):
        for route_clock in ('2026-10-15T10:00:00.000001Z', '2026-10-15T10:59:00Z'):
            package = fixture()
            package['sources'][0]['route']['availability_start'] = route_clock
            package['runner_meta']['dataset_manifest_hash'] = sha256_json(package['sources'])
            before = deepcopy(package)
            result = economic_test_readiness(package, legacy=legacy())
            self.assertEqual(result['source_qualifications'][0]['status'], 'PASS')
            self.assertEqual(result['status'], 'BLOCK')
            self.assertIn('PIT_QUALIFICATION_FAILED', result['block_reasons'])
            self.assertEqual(package, before)
            self.assertTrue(all(v is False for v in result['authority'].values()))

    def test_both_clocks_require_explicit_timezones_in_direct_validator(self):
        for key in ('available_at', 'route_available_at'):
            for value in (None, '', False, 0, [], {}, '2026-10-15', '2026-10-15T09:00:00',
                          '2026-10-15T10:00:00.000001Z'):
                package = _fixture()
                package['sources']['pit_metadata'][0][key] = value
                self.assert_direct_block(package, 'PIT_QUALIFICATION_FAILED')
            package = _fixture()
            del package['sources']['pit_metadata'][0][key]
            self.assert_direct_block(package, 'PIT_QUALIFICATION_FAILED')

    def test_one_old_pit_row_cannot_cover_two_rebound_source_snapshots(self):
        # JSON round-trip breaks fixture aliases, then all unrelated hashes rebind.
        package = json.loads(json.dumps(_fixture()))
        package['sources']['snapshot_hashes'].append('b'*64)
        package['protocol']['protocol_payload']['source_snapshot_hashes'].append('b'*64)
        package['protocol']['protocol_hash'] = sha256_json(package['protocol']['protocol_payload'])
        package['reproducibility']['binding_payload'].update(
            protocol_hash=package['protocol']['protocol_hash'],
            source_snapshot_hashes=package['sources']['snapshot_hashes'])
        package['reproducibility']['binding_hash'] = sha256_json(package['reproducibility']['binding_payload'])
        result = self.assert_direct_block(package, 'SOURCE_PROVENANCE_INCOMPLETE')
        self.assertEqual(result['checks']['protocol_freeze']['status'], 'PASS')
        self.assertEqual(result['checks']['reproducibility_binding']['status'], 'PASS')
        second = deepcopy(package['sources']['pit_metadata'][0])
        second.update(source_id='SRC-2', snapshot_hash='b'*64)
        package['sources']['pit_metadata'].append(second)
        self.assertEqual(validate_economic_test_readiness(package)['status'], READY)
        for key, value in (('snapshot_hash', 'c'*64), ('snapshot_hash', None), ('source_id', False)):
            altered = deepcopy(package)
            altered['sources']['pit_metadata'][1][key] = value
            self.assert_direct_block(altered, 'SOURCE_PROVENANCE_INCOMPLETE' if key == 'snapshot_hash'
                                     else 'PIT_QUALIFICATION_FAILED')
        package['sources']['pit_metadata'].append(second)
        self.assert_direct_block(package, 'SOURCE_PROVENANCE_INCOMPLETE')
        # Integer parsing accepts signs/whitespace, which are not digest bytes.
        for prefix in ('+', '-', ' '):
            malformed = json.loads(json.dumps(_fixture()))
            digest = prefix + 'a'*63
            malformed['sources']['snapshot_hashes'] = [digest]
            malformed['sources']['pit_metadata'][0]['snapshot_hash'] = digest
            malformed['protocol']['protocol_payload']['source_snapshot_hashes'] = [digest]
            malformed['protocol']['protocol_hash'] = sha256_json(malformed['protocol']['protocol_payload'])
            malformed['reproducibility']['binding_payload'].update(
                protocol_hash=malformed['protocol']['protocol_hash'], source_snapshot_hashes=[digest])
            malformed['reproducibility']['binding_hash'] = sha256_json(malformed['reproducibility']['binding_payload'])
            self.assert_direct_block(malformed, 'SOURCE_PROVENANCE_INCOMPLETE')

    def test_producer_and_validator_must_be_explicit_literal_identifiers(self):
        for actor in ('producer_id', 'validator_id'):
            for value in (None, '', ' ', False, 0, 1, [], {}, 'UNKNOWN', 'UNRESOLVED', 'NULL', 'NOT_APPLICABLE'):
                package = _fixture()
                package[actor] = value
                self.assert_direct_block(package, 'PRODUCER_VALIDATOR_NOT_INDEPENDENT')
            package = _fixture()
            del package[actor]
            self.assert_direct_block(package, 'PRODUCER_VALIDATOR_NOT_INDEPENDENT')
        package = _fixture()
        package['validator_id'] = package['producer_id']
        self.assert_direct_block(package, 'PRODUCER_VALIDATOR_NOT_INDEPENDENT')

    def test_valid_offset_clocks_and_declared_content_aliases_keep_their_scope(self):
        package = fixture()
        package['sources'][0]['route']['availability_start'] = '2026-10-15T11:00:00+01:00'
        package['sources'][0]['available_at'] = '2026-10-15T06:00:00-04:00'
        package['runner_meta']['dataset_manifest_hash'] = sha256_json(package['sources'])
        before = deepcopy(package)
        result = economic_test_readiness(package, legacy=legacy())
        self.assertEqual(result['status'], READY, result['block_reasons'])
        pit = result['experiment_plan']['frozen_protocol']['source_pit_metadata'][0]
        self.assertEqual(pit['snapshot_hash'], package['sources'][0]['snapshot_hash'])
        self.assertEqual(pit['available_at'], package['sources'][0]['available_at'])
        self.assertEqual(pit['route_available_at'], package['sources'][0]['route']['availability_start'])
        self.assertEqual(package, before)
        direct = _fixture()
        direct['sources']['snapshot_hashes'].append(direct['sources']['snapshot_hashes'][0])
        alias = deepcopy(direct['sources']['pit_metadata'][0])
        alias['source_id'] = 'DECLARED-ALIAS'
        direct['sources']['pit_metadata'].append(alias)
        # Fixture aliases share the same snapshot list, so preserve protocol bindings.
        direct['protocol']['protocol_hash'] = sha256_json(direct['protocol']['protocol_payload'])
        direct['reproducibility']['binding_payload']['protocol_hash'] = direct['protocol']['protocol_hash']
        direct['reproducibility']['binding_hash'] = sha256_json(direct['reproducibility']['binding_payload'])
        self.assertEqual(validate_economic_test_readiness(direct)['status'], READY)
        self.assertEqual(direct['trial_accounting']['effective_trials_status'], 'UNKNOWN')
        for marker in (False, None, 'false', 0):
            disguised = fixture()
            disguised['engine_output']['synthetic_only'] = marker
            blocked = economic_test_readiness(disguised, legacy=legacy())
            self.assertEqual(blocked['status'], 'BLOCK')
            self.assertIn('FIXTURE_SOURCE_REQUIRES_SYNTHETIC_SCOPE', blocked['block_reasons'])
        self.assertIs(result['synthetic_only'], True)
