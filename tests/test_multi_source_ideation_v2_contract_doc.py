from __future__ import annotations

from pathlib import Path
import unittest


class ContractDocTests(unittest.TestCase):
    def test_contract_records_all_closed_authorities(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_CONTRACT_20261021.md").read_text(encoding="utf-8")
        for flag in ("REAL_CAPITAL_AUTHORIZED=FALSE","LIVE_TRADING_AUTHORIZED=FALSE","PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE","ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE","OUTCOME_ACCESSED=FALSE"):
            self.assertIn(flag,text)
        self.assertIn("ELIGIBLE_FOR_DISCOVERY != READY",text)
        self.assertIn("GPT_OSS_LIVE=TRUE",text)


if __name__ == "__main__": unittest.main()
