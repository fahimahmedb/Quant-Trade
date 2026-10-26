from __future__ import annotations
from pathlib import Path
import unittest

class ContractGptTests(unittest.TestCase):
    def test_contract_requires_live_runtime_proof_and_no_paid_fallback(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        for phrase in ("backend identity","model identity","endpoint/runtime identity","genuine request/response","no silent paid fallback","EXTERNAL_RUNTIME_MISSING"):
            self.assertIn(phrase,text)

if __name__ == "__main__": unittest.main()
