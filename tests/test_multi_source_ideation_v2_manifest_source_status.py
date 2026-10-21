from __future__ import annotations
from pathlib import Path
import unittest

class ManifestSourceStatusTests(unittest.TestCase):
    def test_manifest_distinguishes_implemented_sources_from_live_gpt_oss(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        self.assertIn("SOURCE_A_STATUS=IMPLEMENTED_CANONICAL_SOURCE_PLANNER_BINDING",text)
        self.assertIn("SOURCE_B_STATUS=IMPLEMENTED_RESEARCH_INTELLIGENCE_REUSE_BINDING",text)
        self.assertIn("SOURCE_C_STATUS=IMPLEMENTED_MODEL_BACKEND_PROTOCOL_FAKE_PROOF_ONLY",text)
        self.assertIn("GPT_OSS_STATUS=EXTERNAL_RUNTIME_MISSING",text)

if __name__ == "__main__": unittest.main()
