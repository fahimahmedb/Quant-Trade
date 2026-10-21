from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import light_implementability


class LightImplementabilityTests(unittest.TestCase):
    def test_missing_mechanism_falsifier_or_universe_blocks(self):
        for missing in ("mechanism","falsifier","universe"):
            p={"mechanism":"m","falsifier":"f","universe":"u"}; p.pop(missing)
            with self.subTest(missing=missing): self.assertFalse(light_implementability(p)["admissible"])

    def test_contradicted_actor_or_clock_blocks_without_scientific_verdict(self):
        for key in ("actor","clock"):
            p={"mechanism":"m","falsifier":"f","universe":"u",key:"CONTRADICTED"}
            with self.subTest(key=key):
                got=light_implementability(p); self.assertFalse(got["admissible"]); self.assertIn(key,got["contradictions"])


if __name__ == "__main__": unittest.main()
