from __future__ import annotations
from pathlib import Path
import unittest

class ManifestBoundaryTests(unittest.TestCase):
    def test_manifest_stops_at_discovery_eligibility(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        self.assertIn("FINAL_BOUNDARY=ELIGIBLE_FOR_DISCOVERY",text)
        self.assertIn("SECOND_QUEUE_CREATED=FALSE",text); self.assertIn("SECOND_MEMORY_CREATED=FALSE",text)

if __name__ == "__main__": unittest.main()
