"""Construction can advance independently of economic access; synthetic fixtures only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from quant.edge_lab.engine import initialize, Lab
from quant.edge_lab.store import Refused, verify


class ConstructionQuestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Lab(self.temp.name)
        initialize(self.temp.name)
        self.lab.evidence({'id': 'build-fixture', 'kind': 'METHOD',
            'url': 'https://example.invalid/implementation', 'version': 'synthetic',
            'passage': 'Missing launch adapter', 'fact': 'Fixture', 'limit': 'No market outcomes'})
        for identity in self.lab.snapshot()[0]['decisions']:
            self.lab.decide(identity, 'WAIT', ['build-fixture'], 'Synthetic implementation gate')
        self.packet = {
            'identity': 'build:eurusd-technical-grid:launch-bridge',
            'parent_decision': 'qualify:eurusd-technical-grid',
            'question': 'Can a reviewed launch bridge preserve both reservation authorities?',
            'decision_use': 'Admit or stop adapter implementation; no market access.',
            'evidence_ids': ['build-fixture']}

    def test_cli_queues_claimable_construction_with_economic_history_unchanged(self):
        before = self.lab.snapshot()[0]
        packet = Path(self.temp.name, 'packet.json')
        packet.write_text(json.dumps(self.packet))
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, '-B', str(root / 'scripts/edge_lab.py'),
            '--state-dir', self.temp.name, 'build-question', str(packet)],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        identity, question = Lab(self.temp.name).next_decision()
        self.assertEqual(identity, self.packet['identity'])
        self.assertEqual(question['reason'], 'CONSTRUCTION_ADMISSION')
        self.assertFalse(question['outcome_access_authorized'])
        self.assertIn('Construction :', Path(self.temp.name, 'STATUS.md').read_text())
        after = self.lab.snapshot()[0]
        verify(after)
        self.assertEqual(after['events'][:-1], before['events'])
        self.assertEqual(after['decisions'][self.packet['parent_decision']],
                         before['decisions'][self.packet['parent_decision']])
        for key in ('baseline', 'imported', 'families', 'looks', 'protocols', 'trial_charges', 'jobs'):
            self.assertEqual(after[key], before[key], key)
        claim = self.lab.claim_decision(identity, 'synthetic-builder')
        with self.assertRaises(Refused):
            self.lab.claim_decision(identity, 'second-builder')
        self.lab.decide(identity, 'CLOSED', ['build-fixture'], 'Synthetic bridge review complete', claim_id=claim)
        self.assertEqual(self.lab.snapshot()[0]['looks'], {})

    def test_duplicates_and_renamed_scopes_cannot_reopen_completed_build(self):
        self.lab.build_question(**self.packet)
        self.lab.decide(self.packet['identity'], 'CLOSED', ['build-fixture'], 'Synthetic closed scope')
        before = self.lab.snapshot()[0]
        renamed = {**self.packet, 'identity': 'build:eurusd-technical-grid:renamed',
                   'question': '  CAN a reviewed launch bridge preserve both reservation authorities?  '}
        for packet in (self.packet, renamed):
            with self.assertRaises(Refused):
                self.lab.build_question(**packet)
            self.assertEqual(self.lab.snapshot()[0], before)

    def test_only_one_pending_build_per_parent_and_parent_provenance_required(self):
        self.lab.evidence({'id': 'unrelated-fixture', 'kind': 'METHOD',
            'url': 'https://example.invalid/unrelated', 'version': 'synthetic',
            'passage': 'Other gate', 'fact': 'Fixture', 'limit': 'No outcomes'})
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.build_question(**{**self.packet, 'evidence_ids': ['unrelated-fixture']})
        self.assertEqual(self.lab.snapshot()[0], before)
        self.lab.build_question(**self.packet)
        before = self.lab.snapshot()[0]
        other = {**self.packet, 'identity': 'build:eurusd-technical-grid:other',
                 'question': 'A distinct implementation question'}
        with self.assertRaises(Refused):
            self.lab.build_question(**other)
        self.assertEqual(self.lab.snapshot()[0], before)

    def test_paused_or_cross_family_build_is_refused_without_mutation(self):
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.build_question(**{**self.packet, 'identity': 'build:hyperliquid-forced-flow:adapter'})
        self.assertEqual(self.lab.snapshot()[0], before)
        self.lab.store.pause(True, 'Synthetic Owner pause')
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.build_question(**self.packet)
        self.assertEqual(self.lab.snapshot()[0], before)

    def test_active_parent_or_rejected_family_cannot_be_reopened_as_build(self):
        with tempfile.TemporaryDirectory() as directory:
            initialize(directory)
            with self.assertRaises(Refused):
                Lab(directory).build_question(**self.packet)
        # Simulate a WAIT access question pointing to an already closed mechanism.
        with self.lab.store.lock():
            state = self.lab.store.read()
            state['decisions']['synthetic:closed-family-access'] = {
                'status': 'WAIT', 'family': 'f1-crypto-carry', 'evidence': ['build-fixture']}
            self.lab.store.save(state)
        before = self.lab.snapshot()[0]
        with self.assertRaises(Refused):
            self.lab.build_question(**{**self.packet, 'identity': 'build:f1-crypto-carry:relaunch',
                'parent_decision': 'synthetic:closed-family-access'})
        self.assertEqual(self.lab.snapshot()[0], before)


if __name__ == '__main__':
    unittest.main()
