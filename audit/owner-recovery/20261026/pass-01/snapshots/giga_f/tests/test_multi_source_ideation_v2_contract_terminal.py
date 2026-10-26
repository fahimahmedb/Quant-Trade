from __future__ import annotations
from pathlib import Path
import unittest

class ContractTerminalTests(unittest.TestCase):
    def test_contract_lists_all_terminal_statuses(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        for status in ("PROPOSAL_EMITTED","SEED_EMITTED","NO_PROPOSAL","NO_ADMISSIBLE_NOVEL_SOURCE","FRONTIER_EXHAUSTED","BLOCKED","SOURCE_UNAVAILABLE","SOURCE_FAILED","INVALID_INPUT","NO_ACTION"):
            self.assertIn(status,text)

if __name__ == "__main__": unittest.main()
