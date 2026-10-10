"""Claim persistence and its derived CLI view; synthetic, no network/outcomes."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from quant.edge_lab.engine import initialize
from quant.edge_lab.store import verify


class ClaimDisplayTests(unittest.TestCase):
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
