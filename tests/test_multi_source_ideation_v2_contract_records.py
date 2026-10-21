from __future__ import annotations
from pathlib import Path
import unittest

class ContractRecordsTests(unittest.TestCase):
    def test_contract_lists_required_records(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        for name in ("IdeationContextSnapshot","IdeationCycle","RawProposalReceipt","RawIdeationArtifact","IDEATION_SEED","IDEA_PROPOSAL","Proposal Ledger"):
            self.assertIn(name,text)

if __name__ == "__main__": unittest.main()
