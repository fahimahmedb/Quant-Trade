from __future__ import annotations
from pathlib import Path
import unittest

class ContractNoSealTests(unittest.TestCase):
    def test_contract_denies_wave2_integrated_sha_authority(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        self.assertIn("never authorized to emit `WAVE2_INTEGRATED_SHA`",text)

if __name__ == "__main__": unittest.main()
