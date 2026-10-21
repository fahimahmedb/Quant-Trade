from __future__ import annotations
from pathlib import Path
import unittest

class ContractBaseTests(unittest.TestCase):
    def test_contract_records_exact_immutable_base_and_branch(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        self.assertIn("2b99d8aeb8a342f1ef32544247d366cb8a26037e",text); self.assertIn("builder/multi-source-ideation-intake-20261021",text)

if __name__ == "__main__": unittest.main()
