from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import TERMINAL_STATES, raw_artifact


class TerminalMatrixTests(unittest.TestCase):
    def test_required_terminal_vocabulary_is_exactly_present(self):
        required={"PROPOSAL_EMITTED","SEED_EMITTED","NO_PROPOSAL","NO_ADMISSIBLE_NOVEL_SOURCE","FRONTIER_EXHAUSTED","BLOCKED","SOURCE_UNAVAILABLE","SOURCE_FAILED","INVALID_INPUT","NO_ACTION"}
        self.assertEqual(TERMINAL_STATES,required)

    def test_non_emission_terminals_cannot_carry_proposal(self):
        for status in TERMINAL_STATES-{"PROPOSAL_EMITTED","SEED_EMITTED"}:
            with self.subTest(status=status):
                with self.assertRaises(ValueError): raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status=status,context_snapshot_hash="h",artifact_kind="IDEA_PROPOSAL")


if __name__ == "__main__": unittest.main()
