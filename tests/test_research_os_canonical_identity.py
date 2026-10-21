"""Scientific principals must be attributed while research unknowns remain valid."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.expansion.v2_core import (
    V2ContractError, build_candidate, build_epoch_manifest, build_research_trial,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from tests import test_research_os_v2_core as core_fixtures


class CanonicalIdentityTests(unittest.TestCase):
    def bundle(self):
        return json.loads(Path("tests/fixtures/oracle_v2_core_fixture.json").read_text())

    def test_invalid_principal_identifiers_block_before_hashing(self):
        bundle = self.bundle()
        for kind, builder, fields in (
            ("epoch", build_epoch_manifest, ("research_epoch_id",)),
            ("trial", build_research_trial, ("research_trial_id", "research_epoch_id")),
            ("candidate", build_candidate, ("hypothesis_id", "generation_id", "research_trial_id", "research_epoch_id")),
        ):
            for field in fields:
                for value in (None, False, 0, 1.5, [], {}, "", " \t", "UNKNOWN", " unknown ",
                              "UNRESOLVED", "NOT_APPLICABLE", "NOT_YET_MEASURABLE"):
                    with self.subTest(kind=kind, field=field, value=value):
                        payload = deepcopy(bundle[kind])
                        payload[field] = value
                        before = deepcopy(payload)
                        with self.assertRaisesRegex(V2ContractError, "INVALID_IDENTIFIER:" + field):
                            builder(payload)
                        self.assertEqual(payload, before)

    def test_epoch_and_four_family_hashes_are_unchanged_with_attributed_trial(self):
        bundle = self.bundle()
        self.assertEqual(build_epoch_manifest(bundle["epoch"])["epoch_manifest_hash"],
                         "8486b35bb1558efca9d33cbe74e331fa191227f7c458b213d3d95c385e759457")
        proposal = bundle["trial"]["generated_proposals"][0]
        candidate = build_candidate(bundle["candidate"])
        self.assertTrue(all(proposal[key] == candidate[key]
                            for key in ("hypothesis_id", "generation_id", "candidate_hash")))
        self.assertEqual(build_research_trial(bundle["trial"])["trial_hash"],
                         "a02058400aec467b836985f030f2a1694f5a0c78eedefa7c270b21c24b92ae47")
        expected = {"fundamental": "73bedcc4cf9fa2ae2887b2342f23caea10fa14062a332459d81fa2be69ebf4b1",
                    "event": "8355c998707d92865c54a2db4c5a622f0d7c50cbef55c91fa2062965528f2dc2",
                    "forced_flow": "10d6ed7e58bb728297d0f467aec2ed8f6ecbfff93b49b21612bed549792e2d43",
                    "quant": "3e3bc367fbad029edb977057c4f1c5b0d9b2476c1341a06494b8909d529e3b17"}
        for family, fingerprint in expected.items():
            self.assertEqual(build_candidate(core_fixtures.V2CoreContractTests().candidate_payload(family))["candidate_hash"], fingerprint)

    def test_nullable_root_ancestry_and_scientific_unknowns_remain_supported(self):
        epoch = self.bundle()["epoch"]
        self.assertIsNone(build_epoch_manifest(epoch)["parent_epoch_id"])
        candidate = core_fixtures.V2CoreContractTests().candidate_payload("fundamental")
        candidate["extension"]["business_driver"] = "UNKNOWN"
        candidate["extension"]["valuation_transmission"] = "UNRESOLVED"
        candidate["hypothesis_id"] = "legacy:EXAMPLE-2026.01"
        output = build_candidate(candidate)
        self.assertEqual(output["extension"], candidate["extension"])
        self.assertEqual(output["hypothesis_id"], candidate["hypothesis_id"])

    def test_mutually_equal_null_references_cannot_qualify_whole_pipeline(self):
        bundle = self.bundle()
        for kind, fields in {"epoch": ("research_epoch_id",),
                             "trial": ("research_epoch_id", "research_trial_id"),
                             "candidate": ("research_epoch_id", "research_trial_id", "hypothesis_id", "generation_id"),
                             "validator": ("hypothesis_id", "generation_id")}.items():
            for field in fields:
                bundle[kind][field] = None
        with self.assertRaisesRegex(V2ContractError, "EPOCH_INVALID_IDENTIFIER"):
            run_pre_outcome_pipeline(bundle)


if __name__ == "__main__":
    unittest.main()
