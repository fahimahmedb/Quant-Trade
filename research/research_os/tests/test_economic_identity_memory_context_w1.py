from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.final_shape import economic_identity_v1
from research.research_os.expansion.portfolio_v2 import structural_identity


class EconomicIdentityMemoryContextW1Tests(unittest.TestCase):
    def test_mixed_known_and_invalid_nested_atoms_do_not_qualify_structural_fields(self):
        cases = (
            ("payer", {"desk": "dealer", "forced": True}),
            ("mechanism", {"rule": "rebalance", "detail": "UNKNOWN"}),
            ("economic_exposure", {"factor": "duration", "loading": float("nan")}),
            ("source_identity", {"provider": "official", "version": None}),
        )
        for field, value in cases:
            with self.subTest(field=field):
                projected = structural_identity({
                    "hypothesis_id": "H-NESTED",
                    "generation_id": "GEN-1",
                    "payer": "dealer",
                    "mechanism": "constraint",
                    "timing_clock": "close",
                    field: value,
                })
                self.assertEqual(projected["fields"][field]["status"], "UNKNOWN")
                self.assertEqual(projected["fields"][field]["value"], "UNKNOWN")

    def test_documentary_memory_ref_is_side_context_not_documentary_rewrite(self):
        source_path = Path(__file__).resolve().parents[1] / "sources/apple_fy2025_statement_cells.json"
        output = ENGINE_REGISTRY["fundamental"].run(
            json.loads(source_path.read_text()),
            EngineContext("W1-ECON-MEMORY-CONTEXT", synthetic_only=False),
        )
        produced = economic_identity_v1(output, {})
        baseline = structural_identity(produced)

        contextual = deepcopy(produced)
        contextual["memory_refs"] = ["NEGATIVE-KNOWLEDGE-HASH-EXAMPLE"]
        projected = structural_identity(contextual)

        self.assertEqual(projected["identity_hash"], baseline["identity_hash"])
        self.assertEqual(projected["memory_context"]["refs"], ["NEGATIVE-KNOWLEDGE-HASH-EXAMPLE"])
        self.assertTrue(projected["memory_context"]["structural_context_only"])
        self.assertFalse(projected["memory_context"]["empirical_correlation_inferred"])
        self.assertFalse(projected["memory_context"]["expected_alpha_inferred"])

    def test_malformed_memory_context_fails_closed(self):
        for bad in ("not-a-list", [True], ["UNKNOWN"], ["valid-ref", None]):
            with self.subTest(bad=bad):
                value = {
                    "hypothesis_id": "H-MEM",
                    "generation_id": "GEN-1",
                    "payer": "dealer",
                    "mechanism": "constraint",
                    "timing_clock": "close",
                    "memory_refs": bad,
                }
                with self.assertRaises(ValueError):
                    structural_identity(value)


if __name__ == "__main__":
    unittest.main()
