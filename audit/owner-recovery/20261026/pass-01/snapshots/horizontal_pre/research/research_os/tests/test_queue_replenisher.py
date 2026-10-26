from __future__ import annotations

import unittest
from copy import deepcopy
import json
from pathlib import Path

from research.research_os.queue_replenisher import (
    derive_refill_task,
    load_frontier,
    queue_summary,
    validate_derived_task,
)


class QueueReplenisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = Path(__file__).resolve().parents[1]
        cls.frontier = load_frontier(cls.base)
        cls.now = "2026-10-15T17:40:00Z"

    def terminal_task(self, task_id: str = "OLD-001"):
        return {"task_id": task_id, "status": "COMPLETE"}

    def test_empty_queue_derives_exactly_one_safe_ready_task(self) -> None:
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=[self.terminal_task()],
            created_at=self.now,
        )
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        task = result["task"]
        self.assertEqual(task["status"], "READY")
        self.assertEqual(task["lease"]["generation"], 0)
        self.assertIsNone(task["lease"]["owner"])
        self.assertTrue(task["inputs"]["legacy_gate_required"])
        self.assertEqual(task["derivation"]["steward_lane"], "integrator_portfolio")
        self.assertTrue(all(value is False for key, value in task["authority"].items() if key.endswith("_authorized")))
        validate_derived_task(task)

    def test_nonempty_queue_never_refills(self) -> None:
        ready = {"task_id": "READY-001", "status": "READY"}
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=[ready],
            created_at=self.now,
        )
        self.assertEqual(result["status"], "NOOP_QUEUE_NOT_EMPTY")
        self.assertIsNone(result["task"])

    def test_claimed_task_also_blocks_refill(self) -> None:
        claimed = {"task_id": "CLAIMED-001", "status": "CLAIMED"}
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=[claimed],
            created_at=self.now,
        )
        self.assertEqual(result["status"], "NOOP_QUEUE_NOT_EMPTY")

    def test_every_contract_task_state_is_accounted_for(self) -> None:
        contract = json.loads((self.base / "contracts/research-task.schema.json").read_text())
        states = contract["properties"]["status"]["enum"]
        for state in states:
            with self.subTest(state=state):
                summary = queue_summary([{"task_id": "CONTRACT-STATE", "status": state}])
                self.assertEqual(summary["unknown_count"], 0)
                self.assertEqual(summary["active_count"] + summary["terminal_count"], 1)
                self.assertEqual(summary["active_count"], int(state in {"READY", "CLAIMED"}))
        # Retain the historical terminal spelling already accepted by this reader.
        self.assertEqual(queue_summary([{"status": "KILLED"}])["terminal_count"], 1)

    def test_unrecognized_task_states_block_refill_with_an_explicit_disposition(self) -> None:
        for state in ("UNKNOWN", "UNSUPPORTED_FUTURE_STATE", None):
            with self.subTest(state=state):
                result = derive_refill_task(
                    frontier=self.frontier,
                    tasks=[{"task_id": "UNRESOLVED", "status": state}],
                    created_at=self.now,
                )
                self.assertEqual(result["status"], "BLOCKED_UNKNOWN_TASK_STATUS")
                self.assertEqual(result["queue"]["unknown_count"], 1)
                self.assertIsNone(result["task"])

    def test_missing_status_does_not_mean_an_empty_queue(self) -> None:
        result = derive_refill_task(
            frontier=self.frontier, tasks=[{"task_id": "NO-STATUS"}], created_at=self.now,
        )
        self.assertEqual(result["status"], "BLOCKED_UNKNOWN_TASK_STATUS")
        self.assertIsNone(result["task"])

    def test_failed_task_is_terminal_without_preventing_legitimate_followup(self) -> None:
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=[{"task_id": "FAILED-ATTEMPT", "status": "FAILED"}],
            created_at=self.now,
        )
        self.assertEqual(result["queue"]["terminal_count"], 1)
        self.assertEqual(result["queue"]["unknown_count"], 0)
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        self.assertTrue(all(result["task"]["authority"][key] is False for key in (
            "economic_experiment_authorized", "prospective_observation_authorized",
            "real_capital_authorized", "live_trading_authorized")))

    def test_selection_rotates_by_durable_issue_count(self) -> None:
        first = derive_refill_task(
            frontier=self.frontier,
            tasks=[self.terminal_task()],
            created_at=self.now,
        )["task"]
        first_done = deepcopy(first)
        first_done["status"] = "COMPLETE"
        second = derive_refill_task(
            frontier=self.frontier,
            tasks=[self.terminal_task(), first_done],
            created_at="2026-10-15T18:40:00Z",
        )["task"]
        self.assertNotEqual(first["derivation"]["frontier_id"], second["derivation"]["frontier_id"])
        self.assertNotEqual(first["derivation"]["derivation_key"], second["derivation"]["derivation_key"])

    def test_no_recursive_same_state_invention(self) -> None:
        first_result = derive_refill_task(
            frontier=self.frontier,
            tasks=[self.terminal_task()],
            created_at=self.now,
        )
        first = first_result["task"]
        # Once the derived task exists it is READY, so the queue is not empty.
        second_result = derive_refill_task(
            frontier=self.frontier,
            tasks=[self.terminal_task(), first],
            created_at=self.now,
        )
        self.assertEqual(second_result["status"], "NOOP_QUEUE_NOT_EMPTY")

    def test_frontier_exhaustion_stops_cleanly(self) -> None:
        frontier = deepcopy(self.frontier)
        frontier["max_issued_per_frontier"] = 1
        tasks = [self.terminal_task()]
        for entry in frontier["frontiers"]:
            tasks.append({
                "task_id": f"DONE-{entry['frontier_id']}",
                "status": "COMPLETE",
                "derivation": {
                    "frontier_id": entry["frontier_id"],
                    "derivation_key": f"done-{entry['frontier_id']}",
                },
            })
        result = derive_refill_task(frontier=frontier, tasks=tasks, created_at=self.now)
        self.assertEqual(result["status"], "NOOP_FRONTIER_EXHAUSTED")
        self.assertIsNone(result["task"])

    def test_unsafe_authority_is_rejected(self) -> None:
        frontier = deepcopy(self.frontier)
        frontier["authority"]["economic_experiment_authorized"] = True
        with self.assertRaises(ValueError):
            derive_refill_task(frontier=frontier, tasks=[self.terminal_task()], created_at=self.now)


if __name__ == "__main__":
    unittest.main()
