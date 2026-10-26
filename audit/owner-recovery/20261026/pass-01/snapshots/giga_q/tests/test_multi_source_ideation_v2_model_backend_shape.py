from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend


class ModelBackendShapeTests(unittest.TestCase):
    def test_fake_backend_is_deterministic_and_defensively_copies(self):
        response={"alternatives":[{"summary":"x"}],"selected_alternative_index":0}
        backend=DeterministicFakeBackend(response)
        a=backend.generate({}); a["alternatives"][0]["summary"]="changed"
        b=backend.generate({}); self.assertEqual(b["alternatives"][0]["summary"],"x")


if __name__ == "__main__": unittest.main()
