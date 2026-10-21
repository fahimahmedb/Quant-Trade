from __future__ import annotations

import inspect
import unittest

from research.research_os import multi_source_ideation


class NoSilentPaidFallbackTests(unittest.TestCase):
    def test_policy_c_has_no_provider_specific_fallback(self):
        src=inspect.getsource(multi_source_ideation.policy_c).lower()
        for provider in ("openai", "anthropic", "gemini", "paid_fallback", "fallback_backend"):
            self.assertNotIn(provider,src)
        self.assertIn("source_unavailable",src)


if __name__ == "__main__": unittest.main()
