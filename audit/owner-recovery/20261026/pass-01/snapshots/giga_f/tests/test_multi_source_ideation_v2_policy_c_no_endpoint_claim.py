from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import DeterministicFakeBackend

class FakeBackendTruthTests(unittest.TestCase):
    def test_fixture_backend_does_not_claim_live_endpoint(self):
        b=DeterministicFakeBackend({})
        self.assertEqual(b.backend_identity,"deterministic-fake")
        self.assertEqual(b.model_identity,"fixture-v1")
        self.assertFalse(hasattr(b,"endpoint"))

if __name__ == "__main__": unittest.main()
