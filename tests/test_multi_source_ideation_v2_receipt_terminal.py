from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import raw_proposal_receipt


class ReceiptTerminalTests(unittest.TestCase):
    def test_nonterminal_or_unknown_artifact_is_rejected(self):
        with self.assertRaises(ValueError): raw_proposal_receipt(cycle_id="c",artifact={"policy_kind":"SYSTEMATIC_COVERAGE","status":"RUNNING"},provenance={})


if __name__ == "__main__": unittest.main()
