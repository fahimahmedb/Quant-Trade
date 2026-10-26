from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import POLICIES


class PolicyNamesTests(unittest.TestCase):
    def test_exact_three_policy_names(self):
        self.assertEqual(POLICIES,("SYSTEMATIC_COVERAGE","INFORMATION_VALUE","DIVERGENT_EXPLORATION"))


if __name__ == "__main__": unittest.main()
