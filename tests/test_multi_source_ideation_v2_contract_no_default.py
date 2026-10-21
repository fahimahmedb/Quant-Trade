from __future__ import annotations
from pathlib import Path
import unittest

class ContractNoDefaultTests(unittest.TestCase):
    def test_contract_uses_exact_base_not_default_branch_as_law(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        self.assertIn("Base: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`",text)

if __name__ == "__main__": unittest.main()
