from __future__ import annotations
import inspect
import unittest
from research.research_os import policy_c_safe

class PolicyCSafeNoFallbackTests(unittest.TestCase):
    def test_safe_wrapper_contains_no_provider_fallback(self):
        src=inspect.getsource(policy_c_safe.safe_policy_c).lower()
        for provider in ("openai","anthropic","gemini","fallback_backend","paid_fallback"):
            self.assertNotIn(provider,src)
        self.assertIn("source_failed",src)

if __name__ == "__main__": unittest.main()
