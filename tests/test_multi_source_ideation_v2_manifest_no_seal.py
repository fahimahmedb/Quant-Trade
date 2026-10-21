from __future__ import annotations
from pathlib import Path
import unittest

class ManifestNoSealTests(unittest.TestCase):
    def test_manifest_does_not_emit_wave2_integrated_sha_assignment(self):
        text=Path("research/research_os/MULTISOURCE_IDEATION_V2_MANIFEST_20261021.md").read_text(encoding="utf-8")
        self.assertNotIn("WAVE2_INTEGRATED_SHA=",text)

if __name__ == "__main__": unittest.main()
