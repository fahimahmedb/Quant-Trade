from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.ideation_cycle import (
    ideation_cycle,
    raw_proposal_receipt,
    validate_raw_proposal_receipt,
)
from research.research_os.multi_source_ideation import (
    POLICIES,
    build_context_snapshot,
    raw_artifact,
    side_effect_zeroes,
)
from research.research_os.multi_source_ideation_hardening import (
    DurableProposalLedger,
    proposal_identity,
)


def context():
    refs = {
        "memory_snapshot_ref": "memory://1",
        "ancestry_snapshot_ref": "ancestry://1",
        "frontier_snapshot_ref": "frontier://1",
        "evidence_snapshot_ref": "evidence://1",
        "source_catalog_snapshot_ref": "catalog://1",
        "capability_snapshot_ref": "capability://1",
        "authority_snapshot_ref": "authority://closed",
        "active_work_snapshot_ref": "work://1",
    }
    return build_context_snapshot(
        ideation_cycle_id="CYCLE-INTEGRITY-1",
        created_at="2026-10-21T20:15:00Z",
        refs=refs,
        relevant_schema_versions={"ideation": "v2"},
    )


def terminal_artifacts(snapshot):
    h = snapshot["context_snapshot_hash"]
    return [
        raw_artifact(
            policy_kind=policy,
            status="NO_ACTION",
            context_snapshot_hash=h,
            reason="fixture-terminal",
        )
        for policy in POLICIES
    ]


def exact_receipts(cycle_id, artifacts):
    return [
        raw_proposal_receipt(
            cycle_id=cycle_id,
            artifact=artifact,
            provenance={"source_ref": f"fixture://{artifact['policy_kind']}"},
        )
        for artifact in artifacts
    ]


class Wave2C2MultiSourceIntegrityRepairTests(unittest.TestCase):
    def test_raw_receipt_rejects_nested_outcome_in_artifact(self):
        artifact = {
            "policy_kind": POLICIES[0],
            "status": "PROPOSAL_EMITTED",
            "artifact_kind": "IDEA_PROPOSAL",
            "context_snapshot_hash": "a" * 64,
            "payload": {"nested": [{"return_series": [0.01]}]},
        }
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            raw_proposal_receipt(cycle_id="C1", artifact=artifact, provenance={"source": "fixture"})

    def test_raw_receipt_rejects_nested_outcome_in_provenance(self):
        snapshot = context()
        artifact = terminal_artifacts(snapshot)[0]
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            raw_proposal_receipt(
                cycle_id="C1",
                artifact=artifact,
                provenance={"model": {"diagnostics": {"pnl": 1.0}}},
            )

    def test_proposal_identity_rejects_outcome_payload_and_provenance(self):
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            proposal_identity(
                policy_kind=POLICIES[0],
                context_snapshot_hash="b" * 64,
                payload={"mechanism": "m", "metrics": {"sharpe": 2.0}},
                provenance={"source": "fixture"},
            )
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            proposal_identity(
                policy_kind=POLICIES[0],
                context_snapshot_hash="b" * 64,
                payload={"mechanism": "m"},
                provenance={"source": "fixture", "nested": {"equity_curve": [1, 2]}},
            )

    def test_durable_ledger_rejects_nested_outcome_injected_by_caller(self):
        ledger = DurableProposalLedger()
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            ledger.persist({
                "proposal_id": "P1",
                "payload": {"mechanism": "m", "nested": [{"unrealized_pnl": 1.0}]},
            })
        self.assertEqual(ledger.snapshot(), [])

    def test_duplicate_receipts_for_same_policy_fail_closed(self):
        snapshot = context()
        artifacts = terminal_artifacts(snapshot)
        receipts = exact_receipts("C1", artifacts)
        receipts.append(deepcopy(receipts[0]))
        with self.assertRaisesRegex(ValueError, "duplicate raw proposal receipt"):
            ideation_cycle(
                cycle_id="C1",
                context_snapshot=snapshot,
                artifacts=artifacts,
                receipts=receipts,
            )

    def test_forged_artifact_hash_is_rejected(self):
        snapshot = context()
        artifact = terminal_artifacts(snapshot)[0]
        receipt = raw_proposal_receipt(
            cycle_id="C1", artifact=artifact, provenance={"source": "fixture"}
        )
        forged = deepcopy(receipt)
        forged["artifact_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact_hash mismatch"):
            validate_raw_proposal_receipt(forged, artifact, cycle_id="C1")

    def test_forged_receipt_metadata_is_rejected(self):
        snapshot = context()
        artifact = terminal_artifacts(snapshot)[0]
        receipt = raw_proposal_receipt(
            cycle_id="C1", artifact=artifact, provenance={"source": "fixture"}
        )
        for key, value in (
            ("status", "BLOCKED"),
            ("artifact_kind", "IDEA_PROPOSAL"),
            ("context_snapshot_hash", "f" * 64),
        ):
            forged = deepcopy(receipt)
            forged[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "mismatch"):
                validate_raw_proposal_receipt(forged, artifact, cycle_id="C1")

    def test_forged_receipt_id_is_rejected(self):
        snapshot = context()
        artifact = terminal_artifacts(snapshot)[0]
        receipt = raw_proposal_receipt(
            cycle_id="C1", artifact=artifact, provenance={"source": "fixture"}
        )
        forged = deepcopy(receipt)
        forged["receipt_id"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "receipt id mismatch"):
            validate_raw_proposal_receipt(forged, artifact, cycle_id="C1")

    def test_receipt_without_matching_artifact_is_rejected(self):
        snapshot = context()
        artifacts = terminal_artifacts(snapshot)
        receipts = exact_receipts("C1", artifacts)
        foreign = deepcopy(receipts[0])
        foreign["policy_kind"] = "NOT_A_POLICY"
        with self.assertRaisesRegex(ValueError, "invalid policy"):
            ideation_cycle(
                cycle_id="C1",
                context_snapshot=snapshot,
                artifacts=artifacts,
                receipts=[foreign, *receipts[1:]],
            )

    def test_legitimate_exact_receipts_preserve_passive_cycle(self):
        snapshot = context()
        artifacts = terminal_artifacts(snapshot)
        receipts = exact_receipts("C1", artifacts)
        result = ideation_cycle(
            cycle_id="C1",
            context_snapshot=snapshot,
            artifacts=artifacts,
            receipts=receipts,
        )
        self.assertEqual(result["status"], "BARRIER_COMPLETE")
        self.assertTrue(result["intake_allowed"])
        self.assertFalse(result["outcome_accessed"])
        self.assertEqual(result["ready_tasks_created"], 0)
        self.assertEqual(result["candidates_created"], 0)
        self.assertEqual(side_effect_zeroes(), {
            "READY_TASKS_CREATED": 0,
            "CONTROL_PLANE_MUTATIONS": 0,
            "PRODUCERS_EXECUTED": 0,
            "ORACLE_MUTATIONS": 0,
            "SCHEDULER_MUTATIONS": 0,
            "CANDIDATES_CREATED": 0,
        })


if __name__ == "__main__":
    unittest.main()
