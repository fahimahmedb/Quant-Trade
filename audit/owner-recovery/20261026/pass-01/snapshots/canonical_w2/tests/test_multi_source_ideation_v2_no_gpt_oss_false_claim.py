from __future__ import annotations
from pathlib import Path
import unittest

class NoGptOssFalseClaimTests(unittest.TestCase):
    def test_manifest_keeps_gpt_oss_live_false_without_runtime_proof(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        self.assertIn("GPT_OSS_LIVE=FALSE",text); self.assertIn("EXTERNAL_RUNTIME_MISSING",text)
        self.assertNotIn("GPT_OSS_LIVE=TRUE",text)

if __name__ == "__main__": unittest.main()
