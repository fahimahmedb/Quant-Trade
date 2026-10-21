from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import light_implementability


class UnknownImplementabilityTests(unittest.TestCase):
    def test_unknown_required_dimensions_are_missing_not_assumed(self):
        got=light_implementability({"mechanism":"UNKNOWN","falsifier":"f","universe":"u"})
        self.assertFalse(got["admissible"]); self.assertIn("mechanism",got["missing"])


if __name__ == "__main__": unittest.main()
