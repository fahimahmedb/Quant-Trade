"""Capacity observations must not bypass claims or become economic admission."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.resources import probe_eurusd, QUESTION, FROZEN_COMMIT, PREFIX
from quant.edge_lab.store import Refused


class ResourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        initialize(self.temp.name)
        self.lab = Lab(self.temp.name)
        self.lab.evidence({'id': 'resource-fixture', 'kind': 'METHOD', 'url': 'https://example.invalid/code',
            'version': 'synthetic', 'passage': 'Fixture', 'fact': 'Fixture', 'limit': 'No market'})
        self.lab.decide('qualify:eurusd-technical-grid', 'WAIT', ['resource-fixture'], 'Admission')
        self.lab.build_question(QUESTION, 'qualify:eurusd-technical-grid', 'Resource bounds?',
                                'Admission only', ['resource-fixture'])
        self.claim = self.lab.claim_decision(QUESTION, 'synthetic-builder')
        self.state, self.control = self.lab.snapshot()
        code = b'raise AssertionError("parent must never import legacy code")\n'
        freeze = json.dumps({'files': {n: hashlib.sha256(code).hexdigest()
            for n in ('engine.py', 'safety_kernel.py')}, 'runtime_data': {}}).encode()
        self.freeze_hash = hashlib.sha256(freeze).hexdigest()
        self.blobs = {'HEAD:research/edge_lab/STATE.json': json.dumps(self.state).encode(),
            'HEAD:research/edge_lab/CONTROL.json': json.dumps(self.control).encode(),
            FROZEN_COMMIT+':'+PREFIX+'freeze.json': freeze}
        for n in ('engine.py', 'safety_kernel.py'):
            self.blobs[FROZEN_COMMIT+':'+PREFIX+n] = code

    def read_git(self, repo, args, deadline):
        self.assertGreater(deadline, time.monotonic())
        blob = self.blobs[args[-1]]
        return str(len(blob)).encode() if args[0] == 'cat-file' else blob

    def probe(self, child):
        with patch('quant.edge_lab.resources._git', side_effect=self.read_git), \
             patch('quant.edge_lab.resources.FREEZE_SHA256', self.freeze_hash), \
             patch('quant.edge_lab.resources.subprocess.run', side_effect=child):
            return probe_eurusd(self.lab, '.', self.claim)

    def test_wrong_expired_or_paused_claim_stops_before_source_or_worker(self):
        with patch('quant.edge_lab.resources._git', side_effect=AssertionError('No reads permitted')):
            with self.assertRaises(Refused):
                probe_eurusd(self.lab, '.', 'wrong')
            with self.lab.store.lock():
                state = self.lab.store.read()
                state['decisions'][QUESTION]['claimed_at'] = '2000-01-01T00:00:00Z'
                self.lab.store.save(state)
            with self.assertRaises(Refused):
                probe_eurusd(self.lab, '.', self.claim)
            self.lab.store.pause(True, 'Synthetic pause')
            with self.assertRaises(Refused):
                probe_eurusd(self.lab, '.', self.claim)

    def test_unpublished_or_tampered_code_never_starts_worker(self):
        def forbidden(*args, **kwargs):
            raise AssertionError('Worker must not start')
        self.blobs['HEAD:research/edge_lab/STATE.json'] = b'{}'
        with self.assertRaises(Refused):
            self.probe(forbidden)
        self.blobs['HEAD:research/edge_lab/STATE.json'] = json.dumps(self.state).encode()
        self.blobs[FROZEN_COMMIT+':'+PREFIX+'engine.py'] += b'# altered\n'
        with self.assertRaises(Refused):
            self.probe(forbidden)

    def test_completed_capacity_sample_cannot_admit_protocol_or_mutate_history(self):
        def child(argv, **kwargs):
            self.assertIn('-I', argv)
            self.assertIn('-B', argv)
            self.assertLessEqual(kwargs['timeout'], 90)
            root = Path(kwargs['cwd'])
            self.assertEqual(sorted(p.name for p in root.iterdir()),
                             ['engine.py', 'fixture.py', 'safety_kernel.py'])
            return subprocess.CompletedProcess(argv, 0, b'{"wall_seconds":1,"finalize_completed":true}', b'')
        report = self.probe(child)
        self.assertFalse(report['full_protocol_admitted'])
        self.assertFalse(report['outcome_access_authorized'])
        self.assertEqual(self.lab.snapshot(), (self.state, self.control))

    def test_timeout_is_saved_as_incomplete_without_worker_retry_or_look(self):
        calls = []
        def child(argv, **kwargs):
            calls.append(argv)
            raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
        report = self.probe(child)
        self.assertEqual(len(calls), 1)
        self.assertEqual(report['observation']['status'], 'SYNTHETIC_WALL_LIMIT_REACHED')
        self.assertFalse(report['full_protocol_admitted'])
        self.assertEqual(self.lab.snapshot(), (self.state, self.control))

    def test_global_cpu_ceiling_cannot_be_satisfied_by_a_child_only_meter(self):
        with self.lab.store.lock():
            from quant.state import write_json
            control = self.lab.store.control()
            control['limits']['cpu_seconds_total'] = 1000
            write_json(self.lab.store.control_path, control)
        with patch('quant.edge_lab.resources._git', side_effect=AssertionError('No reads permitted')):
            with self.assertRaisesRegex(Refused, 'BUDGET_UNMEASURED'):
                probe_eurusd(self.lab, '.', self.claim)


if __name__ == '__main__':
    unittest.main()
