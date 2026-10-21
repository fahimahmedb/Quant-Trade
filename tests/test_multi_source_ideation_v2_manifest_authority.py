from __future__ import annotations
from pathlib import Path
import unittest

class ManifestAuthorityTests(unittest.TestCase):
    def test_manifest_records_zero_side_effects_and_closed_authorities(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        for line in ("READY_TASKS_CREATED=0","CANDIDATES_CREATED=0","CONTROL_PLANE_MUTATIONS=0","PRODUCERS_EXECUTED=0","ORACLE_MUTATIONS=0","SCHEDULER_MUTATIONS=0","REAL_CAPITAL_AUTHORIZED=FALSE","LIVE_TRADING_AUTHORIZED=FALSE","PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE","ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE","OUTCOME_ACCESSED=FALSE"):
            self.assertIn(line,text)

if __name__ == "__main__": unittest.main()
