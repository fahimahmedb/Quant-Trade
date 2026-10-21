from __future__ import annotations

from pathlib import Path
import unittest


class NoWaveSealTests(unittest.TestCase):
    def test_implementation_does_not_emit_wave2_integrated_sha(self):
        root=Path("research/research_os")
        paths=(root/"multi_source_ideation.py",root/"multi_source_ideation_bindings.py",root/"multi_source_ideation_hardening.py",root/"ideation_cycle.py")
        text="\n".join(p.read_text(encoding="utf-8") for p in paths)
        self.assertNotIn("WAVE2_INTEGRATED_SHA=",text)


if __name__ == "__main__": unittest.main()
