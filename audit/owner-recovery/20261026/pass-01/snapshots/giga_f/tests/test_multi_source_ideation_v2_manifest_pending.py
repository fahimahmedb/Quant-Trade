from __future__ import annotations
from pathlib import Path
import unittest

class ManifestPendingTests(unittest.TestCase):
    def test_manifest_does_not_self_certify_before_exact_head_ci(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        self.assertIn("SAFE_TO_INTEGRATE=PENDING_EXACT_HEAD_CI",text)
        self.assertIn("FINAL_SHA=PENDING_EXACT_HEAD",text)

if __name__ == "__main__": unittest.main()
