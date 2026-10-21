from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation


class NoModelAuthorityTests(unittest.TestCase):
    def test_model_backend_protocol_only_generates_bounded_mapping(self):
        src=inspect.getsource(multi_source_ideation.ModelBackend)
        self.assertIn("generate",src)
        for forbidden in ("schedule","execute","validate","adjudicate","trade","candidate"):
            self.assertNotIn(forbidden,src.lower())


if __name__ == "__main__": unittest.main()
