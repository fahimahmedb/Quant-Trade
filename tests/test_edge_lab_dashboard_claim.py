"""Claim persistence and its derived CLI view; synthetic, no network/outcomes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from quant.edge_lab.engine import initialize, Lab
from quant.edge_lab.store import verify, Refused


class ClaimDisplayTests(unittest.TestCase):
    def test_new_family_queues_one_admission_question_without_economic_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            initialize(directory)
            lab = Lab(directory)
            lab.evidence({'id': 'synthetic-access', 'kind': 'ACCESS',
                'url': 'https://example.invalid/metadata', 'version': 'synthetic',
                'passage': 'No market data', 'fact': 'Fixture', 'limit': 'Synthetic only'})
            for identity in lab.snapshot()[0]['decisions']:
                lab.decide(identity, 'WAIT', ['synthetic-access'], 'Synthetic access unavailable')
            self.assertIsNone(lab.next_decision())
            before = lab.snapshot()[0]
            lab.family('new-mechanism', 'Distinct synthetic mechanism', 'synthetic-dataset', ['synthetic-access'])
            identity, question = lab.next_decision()
            self.assertEqual(identity, 'qualify:new-mechanism')
            self.assertEqual(question['status'], 'OPEN')
            after = lab.snapshot()[0]
            self.assertEqual(after['events'][:len(before['events'])], before['events'])
            self.assertEqual(after['looks'], before['looks'])
            self.assertEqual(after['trial_charges'], before['trial_charges'])
            self.assertEqual(after['protocols'], before['protocols'])
            with self.assertRaises(Refused):
                lab.family('new-mechanism', 'Distinct synthetic mechanism', 'synthetic-dataset', ['synthetic-access'])
            self.assertEqual(sum(d['status'] == 'OPEN' for d in lab.snapshot()[0]['decisions'].values()), 1)

    def test_cli_claim_succeeds_after_persisting_one_claim_without_next_action(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            initialize(directory)
            result = subprocess.run(
                [sys.executable, '-B', str(root / 'scripts/edge_lab.py'),
                 '--state-dir', directory, 'claim-question',
                 'qualify:eurusd-technical-grid', '--actor', 'synthetic-test'],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(result.stdout.splitlines()[0])
            state = json.loads(Path(directory, 'STATE.json').read_text())
            verify(state)
            decision = state['decisions']['qualify:eurusd-technical-grid']
            self.assertEqual(decision['claim_id'], receipt['claim_id'])
            self.assertEqual(decision['status'], 'RESEARCHING')
            self.assertNotIn('next_action', decision)
            self.assertEqual(sum(e['kind'] == 'QUESTION_CLAIMED' for e in state['events']), 1)
            self.assertEqual(state['looks'], {})
            self.assertEqual(state['trial_charges'], {})
            self.assertIn('RESEARCHING', Path(directory, 'STATUS.md').read_text())


if __name__ == '__main__':
    unittest.main()
