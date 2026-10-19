from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from research.research_os.worker_preflight import (
    WorkerPreflightBlock,
    compare_current_identities,
    current_corpus_overlap_map,
    git_blob_sha,
    load_current_hypothesis_corpus,
    normalize_hypothesis,
    verify_materialized_legacy,
    verify_task_authority,
)


BASE = Path(__file__).resolve().parents[1]


class WorkerPreflightTests(unittest.TestCase):
    def test_current_repository_corpus_normalizes_without_silent_omission(self):
        corpus = load_current_hypothesis_corpus(BASE)
        files = sorted((BASE / "hypotheses").glob("*.json"))
        self.assertEqual(corpus["count"], len(files))
        self.assertGreater(corpus["count"], 0)
        self.assertEqual(
            {item["hypothesis_id"] for item in corpus["identities"]},
            {path.stem for path in files},
        )
        self.assertEqual(len(corpus["snapshot_hash"]), 64)

    def test_asml_service_and_pricing_real_pair_requires_overlap_review(self):
        corpus = load_current_hypothesis_corpus(BASE)
        identities = {item["hypothesis_id"]: item for item in corpus["identities"]}
        service = identities["FUND-ASML-CAPACITY-SERVICE-001"]
        pricing = identities["FUND-ASML-CAPACITY-PRICING-001"]
        relation = compare_current_identities(service, pricing)
        self.assertEqual(
            relation["classification"], "HIGH_CURRENT_EXPOSURE_OVERLAP_REVIEW"
        )
        self.assertTrue(relation["review_required"])
        self.assertIn("entity", relation["basis"])
        self.assertGreaterEqual(relation["mechanism_overlap"], 0.22)

        overlap = current_corpus_overlap_map(corpus)
        pair = next(
            item
            for item in overlap["review_pairs"]
            if {item["left"], item["right"]}
            == {
                "FUND-ASML-CAPACITY-SERVICE-001",
                "FUND-ASML-CAPACITY-PRICING-001",
            }
        )
        self.assertTrue(pair["review_required"])

    def test_alternate_generation_thesis_schema_is_normalized(self):
        record = {
            "hypothesis_id": "ALT-1",
            "generation": 2,
            "issuer": "Example Corp",
            "thesis": "Capacity scarcity supports pricing power",
            "causal_chain": ["demand exceeds supply", "pricing remains firm"],
            "status": "FROZEN_FOR_INDEPENDENT_VALIDATION",
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        value = normalize_hypothesis(record, path="ALT-1.json")
        self.assertEqual(value["generation_id"], "G2")
        self.assertEqual(value["entity"], "example corp")
        self.assertIn("capacity", value["mechanism_tokens"])
        self.assertIn("scarcity", value["mechanism_tokens"])

    def test_candidate_id_mechanism_family_schema_is_normalized(self):
        record = {
            "candidate_id": "EVENT-ALT-1",
            "generation": 1,
            "mechanism_family": "STAPLED_CONTINGENT_VALUE_RIGHT",
            "primary_document": {"issuer": "Example Bio, Inc."},
            "candidate_hypothesis": {
                "claim": "A stapled contingent right changes the bundled claim.",
                "causal_chain": ["right attached", "state transition changes entitlement"],
            },
            "status": "FROZEN_FOR_INDEPENDENT_VALIDATION",
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        value = normalize_hypothesis(record, path="EVENT-ALT-1.json")
        self.assertEqual(value["hypothesis_id"], "EVENT-ALT-1")
        self.assertEqual(value["generation_id"], "G1")
        self.assertEqual(value["family_id"], "stapled_contingent_value_right")
        self.assertEqual(value["entity"], "example bio inc")
        self.assertIn("stapled", value["mechanism_tokens"])

    def test_candidate_id_must_match_file_identity(self):
        record = {
            "candidate_id": "OTHER-ID",
            "generation": 1,
            "mechanism_family": "EVENT_FAMILY",
            "candidate_hypothesis": {"claim": "bounded event mechanism"},
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        with self.assertRaisesRegex(
            WorkerPreflightBlock, "CURRENT_CANDIDATE_ID_PATH_MISMATCH"
        ):
            normalize_hypothesis(record, path="EXPECTED-ID.json")

    def test_unsupported_generation_fails_closed(self):
        record = {
            "hypothesis_id": "BAD-1",
            "mechanism": "some valid mechanism text",
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        with self.assertRaisesRegex(
            WorkerPreflightBlock, "CURRENT_HYPOTHESIS_GENERATION_UNSUPPORTED"
        ):
            normalize_hypothesis(record, path="BAD-1.json")

    def test_hypothesis_authority_must_remain_closed(self):
        record = {
            "hypothesis_id": "BAD-AUTH",
            "generation_id": "G1",
            "mechanism": "bounded documentary mechanism",
            "authority": {
                "economic_experiment_authorized": True,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        with self.assertRaisesRegex(
            WorkerPreflightBlock, "CURRENT_HYPOTHESIS_AUTHORITY_UNSAFE"
        ):
            normalize_hypothesis(record, path="BAD-AUTH.json")

    def test_unknown_identity_is_not_auto_distinct(self):
        left = {
            "hypothesis_id": "H1",
            "family_id": "UNKNOWN",
            "entity": "UNKNOWN",
            "mechanism_tokens": ["capacity", "scarcity"],
        }
        right = {
            "hypothesis_id": "H2",
            "family_id": "UNKNOWN",
            "entity": "UNKNOWN",
            "mechanism_tokens": ["different", "clock"],
        }
        relation = compare_current_identities(left, right)
        self.assertEqual(
            relation["classification"], "UNKNOWN_CURRENT_EXPOSURE_RELATION"
        )
        self.assertTrue(relation["review_required"])

    def test_exact_current_id_duplicate_blocks(self):
        base = {
            "hypothesis_id": "SAME",
            "family_id": "family",
            "entity": "entity",
            "mechanism_tokens": ["one", "two"],
        }
        relation = compare_current_identities(base, dict(base))
        self.assertEqual(relation["classification"], "BLOCK_EXACT_CURRENT_DUPLICATE")
        self.assertTrue(relation["review_required"])

    def test_task_authority_and_status_fail_closed(self):
        task = {
            "status": "READY",
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        }
        self.assertEqual(
            verify_task_authority(task),
            {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
        )
        bad = json.loads(json.dumps(task))
        bad["authority"]["real_capital_authorized"] = True
        with self.assertRaisesRegex(WorkerPreflightBlock, "TASK_AUTHORITY_UNSAFE"):
            verify_task_authority(bad)
        terminal = json.loads(json.dumps(task))
        terminal["status"] = "COMPLETE"
        with self.assertRaisesRegex(WorkerPreflightBlock, "TASK_NOT_ADMISSIBLE_FOR_WAKE"):
            verify_task_authority(terminal)

    def test_materialized_legacy_missing_or_wrong_blob_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "legacy").mkdir()
            manifest = {
                "source_commit": "1" * 40,
                "ledger_blob_sha": "0" * 40,
                "schema_version": "legacy-research-ledger-v1",
                "reconciliation_status": "PARTIAL_WITH_EXPLICIT_GAPS",
                "historical_research_items_found": 1,
                "known_duplicate_or_variant_items": 0,
                "prospective_validated": 0,
                "global_effective_trials": "UNKNOWN",
                "governance": {
                    "REAL_CAPITAL_AUTHORIZED": False,
                    "LIVE_TRADING_AUTHORIZED": False,
                    "historical_result_immutability": True,
                },
            }
            (base / "legacy" / "source_manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(
                WorkerPreflightBlock, "LEGACY_LEDGER_NOT_MATERIALIZED"
            ):
                verify_materialized_legacy(base)

            ledger = {
                "schema_version": "legacy-research-ledger-v1",
                "governance": {
                    "REAL_CAPITAL_AUTHORIZED": False,
                    "LIVE_TRADING_AUTHORIZED": False,
                    "historical_result_immutability": True,
                },
                "records": [{"HYPOTHESIS_ID": "L1"}],
            }
            data = json.dumps(ledger).encode()
            (base / "legacy" / "LEGACY_RESEARCH_LEDGER.imported.json").write_bytes(data)
            with self.assertRaisesRegex(
                WorkerPreflightBlock, "LEGACY_LEDGER_BLOB_MISMATCH"
            ):
                verify_materialized_legacy(base)

            manifest["ledger_blob_sha"] = git_blob_sha(data)
            (base / "legacy" / "source_manifest.json").write_text(json.dumps(manifest))
            result = verify_materialized_legacy(base)
            self.assertEqual(result["loaded_record_count"], 1)
            self.assertEqual(result["ledger_blob_sha"], git_blob_sha(data))


if __name__ == "__main__":
    unittest.main()
