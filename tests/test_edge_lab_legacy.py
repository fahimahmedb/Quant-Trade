"""Admission boundary checks: metadata does not authorize legacy execution."""
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.legacy import inspect_eurusd, QUESTION, PREFIX, FROZEN_COMMIT
from quant.edge_lab.store import Refused


class LegacyPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        initialize(self.temp.name)
        self.lab = Lab(self.temp.name)
        self.lab.evidence({'id': 'legacy-fixture', 'kind': 'METHOD', 'url': 'https://example.invalid/code',
            'version': 'synthetic', 'passage': 'Frozen fixture', 'fact': 'Fixture', 'limit': 'No market'})
        self.lab.decide('qualify:eurusd-technical-grid', 'WAIT', ['legacy-fixture'], 'Synthetic admission')
        self.lab.build_question(QUESTION, 'qualify:eurusd-technical-grid', 'Synthetic exact bridge?',
                                'Admission only', ['legacy-fixture'])
        self.claim = self.lab.claim_decision(QUESTION, 'synthetic-builder')
        self.state, self.control = self.lab.snapshot()
        manifest = json.dumps({'utc_outcome': ['2025-02-01T00:00:00Z', '2026-10-01T00:00:00Z'],
                               'archive_jobs': [{}] * 21, 'trial_accounting': {'expressions': 3}}).encode()
        # Deliberately invalid Python: a metadata check must never import this fixture.
        source = b'raise AssertionError("legacy module imported")\n'
        frozen = json.dumps({'files': {'run.py': hashlib.sha256(source).hexdigest(),
            'manifest.json': hashlib.sha256(manifest).hexdigest()}, 'runtime_data': {},
            'reservation_ref': 'refs/heads/looks/eurusd-range-grid-001-exploratory-01',
            'fixed_output': '/not-a-real-market-output/result.json'}).encode()
        self.blobs = {'HEAD:research/edge_lab/STATE.json': json.dumps(self.state).encode(),
                      'HEAD:research/edge_lab/CONTROL.json': json.dumps(self.control).encode(),
                      FROZEN_COMMIT+':'+PREFIX+'freeze.json': frozen,
                      FROZEN_COMMIT+':'+PREFIX+'run.py': source,
                      FROZEN_COMMIT+':'+PREFIX+'manifest.json': manifest}
        self.freeze_hash = hashlib.sha256(frozen).hexdigest()

    def read_git(self, repo, args, deadline):
        if deadline <= time.monotonic():
            raise AssertionError('Deadline required')
        blob = self.blobs[args[-1]]
        return str(len(blob)).encode() if args[0] == 'cat-file' else blob

    def inspect(self):
        with patch('quant.edge_lab.legacy._git', side_effect=self.read_git), \
             patch('quant.edge_lab.legacy.FREEZE_SHA256', self.freeze_hash):
            return inspect_eurusd(self.lab, Path(self.temp.name), self.claim)

    def test_verified_fixture_remains_blocked_read_only_and_preserves_history(self):
        report = self.inspect()
        self.assertTrue(report['checks']['bundle_identity_verified'])
        self.assertFalse(report['launch_admitted'])
        self.assertFalse(report['outcome_access_authorized'])
        self.assertFalse(report['original_ref_creation_within_scope'])
        self.assertEqual(report['contract']['archive_jobs'], 21)
        self.assertEqual(self.lab.snapshot(), (self.state, self.control))

    def test_pause_wrong_claim_and_expired_claim_stop_before_any_git_access(self):
        with patch('quant.edge_lab.legacy._git', side_effect=AssertionError('Must not read metadata')):
            with self.assertRaises(Refused):
                inspect_eurusd(self.lab, '.', 'wrong-claim')
            with self.lab.store.lock():
                state = self.lab.store.read()
                state['decisions'][QUESTION]['claimed_at'] = '2000-01-01T00:00:00Z'
                self.lab.store.save(state)
            with self.assertRaises(Refused):
                inspect_eurusd(self.lab, '.', self.claim)
            self.lab.store.pause(True, 'Synthetic pause')
            with self.assertRaises(Refused):
                inspect_eurusd(self.lab, '.', self.claim)

    def test_unpublished_claim_or_code_tampering_cannot_pass(self):
        self.blobs['HEAD:research/edge_lab/STATE.json'] = b'{}'
        with self.assertRaises(Refused):
            self.inspect()
        self.blobs['HEAD:research/edge_lab/STATE.json'] = json.dumps(self.state).encode()
        self.blobs[FROZEN_COMMIT+':'+PREFIX+'run.py'] += b'# tampered\n'
        with self.assertRaises(Refused):
            self.inspect()

    def test_metadata_ceiling_stops_before_any_blob_body(self):
        with self.lab.store.lock():
            control = self.lab.store.control()
            control['limits']['metadata_bytes_per_tick'] = 1
            from quant.state import write_json
            write_json(self.lab.store.control_path, control)
        calls = []
        def read(repo, args, deadline):
            calls.append(args[0])
            return self.read_git(repo, args, deadline)
        with patch('quant.edge_lab.legacy._git', side_effect=read):
            with self.assertRaises(Refused):
                inspect_eurusd(self.lab, '.', self.claim)
        self.assertEqual(calls, ['cat-file'])

    def test_missing_timezone_dependency_is_unqualified_not_a_launch(self):
        key = FROZEN_COMMIT+':'+PREFIX+'freeze.json'
        frozen = json.loads(self.blobs[key])
        frozen['runtime_data'] = {str(Path(self.temp.name, 'absent-timezone')): '0' * 64}
        self.blobs[key] = json.dumps(frozen).encode()
        self.freeze_hash = hashlib.sha256(self.blobs[key]).hexdigest()
        report = self.inspect()
        self.assertFalse(report['checks']['timezone_matches'])
        self.assertFalse(report['launch_admitted'])


if __name__ == '__main__':
    unittest.main()
