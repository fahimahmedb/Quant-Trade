from __future__ import annotations
import inspect
import unittest
from research.research_os import multi_source_ideation

class NoModelTruthTests(unittest.TestCase):
    def test_model_backend_protocol_has_no_scientific_truth_methods(self):
        src=inspect.getsource(multi_source_ideation.ModelBackend).lower()
        for token in ("verdict","validate","approve","reject","scientific","economic"):
            self.assertNotIn(token,src)

if __name__ == "__main__": unittest.main()
