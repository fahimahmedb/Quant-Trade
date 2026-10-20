import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.frontier_source_planner_v2 import plan_frontier_source
from research.research_os.github_state import StateConflict
from research.research_os.oracle_worker_v2 import V2ResearchOSWorker
from research.research_os.queue_replenisher import derive_refill_task, load_source_catalog
from research.research_os.worker_stages import require_stage_authorized


BASE = Path("research/research_os")
AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)


class FrontierSourcePlannerV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = json.loads((BASE / "runtime" / "RESEARCH_FRONTIER.json").read_text())
        cls.catalog = load_source_catalog(BASE)

    def entry(self, frontier_id):
        return next(item for item in self.frontier["frontiers"] if item["frontier_id"] == frontier_id)

    @staticmethod
    def legacy_task(entry, sequence=1):
        return {
            "task_id": f"LEGACY-{entry['frontier_id']}-{sequence}",
            "task_type": entry["task_type"],
            "status": "BLOCKED",
            "inputs": {},
            "derivation": {
                "frontier_id": entry["frontier_id"],
                "sequence": sequence,
                "derivation_key": f"legacy-{entry['frontier_id']}-{sequence}",
            },
        }

    def test_institutional_faq_selected_after_legacy_default_rule_consumed(self):
        entry = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        plan = plan_frontier_source(
            frontier_entry=entry,
            tasks=[self.legacy_task(entry)],
            source_catalog=self.catalog,
        )
        self.assertEqual(plan["status"], "SOURCE_SELECTED")
        self.assertEqual(
            plan["source"]["path"],
            "research/research_os/sources/sec_t1_staff_faq.json",
        )
        self.assertEqual(plan["family"], "INSTITUTIONAL_FLOW")
        self.assertGreaterEqual(plan["qualified_count"], 2)

    def test_event_and_fundamental_defaults_are_truthfully_exhausted(self):
        for frontier_id in ("EVENT_DOCUMENT_DISTINCT_MECHANISM", "FUNDAMENTAL_DISTINCT_THESIS"):
            entry = self.entry(frontier_id)
            plan = plan_frontier_source(
                frontier_entry=entry,
                tasks=[self.legacy_task(entry)],
                source_catalog=self.catalog,
            )
            self.assertEqual(plan["status"], "NO_UNUSED_ADMISSIBLE_SOURCE")
            self.assertIsNone(plan["source"])

    def test_quant_without_qualified_documentary_source_is_noop(self):
        entry = self.entry("QUANT_MECHANISM_DISTINCT")
        plan = plan_frontier_source(
            frontier_entry=entry,
            tasks=[],
            source_catalog=self.catalog,
        )
        self.assertEqual(plan["status"], "NO_ADMISSIBLE_DOCUMENTARY_SOURCE")
        frontier = deepcopy(self.frontier)
        frontier["frontiers"] = [entry]
        result = derive_refill_task(
            frontier=frontier,
            tasks=[],
            created_at="2026-10-20T15:00:00Z",
            source_catalog=self.catalog,
        )
        self.assertEqual(result["status"], "NOOP_NO_ADMISSIBLE_NOVEL_SOURCE")
        self.assertIsNone(result["task"])

    def test_source_aware_refill_skips_exhausted_frontiers_and_binds_faq(self):
        event = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        fundamental = self.entry("FUNDAMENTAL_DISTINCT_THESIS")
        flow = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        tasks = [
            self.legacy_task(event),
            self.legacy_task(fundamental),
            self.legacy_task(flow),
        ]
        catalog = deepcopy(self.catalog)
        faq = "research/research_os/sources/sec_t1_staff_faq.json"
        catalog[faq]["blob_sha"] = "5" * 40
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=tasks,
            created_at="2026-10-20T15:01:00Z",
            source_catalog=catalog,
        )
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        self.assertEqual(result["selected_frontier"], "INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        task = result["task"]
        self.assertEqual(task["inputs"]["documentary_source"], faq)
        self.assertEqual(task["inputs"]["documentary_source_blob"], "5" * 40)
        self.assertEqual(
            task["inputs"]["documentary_source_packet_hash"],
            catalog[faq]["record"]["documentary_packet"]["content_hash"],
        )
        self.assertTrue(all(task["authority"][key] is False for key in AUTHORITY_KEYS))

    def test_capture_support_is_not_a_producer_source(self):
        capture_path = BASE / "sources" / "apple_dividend_announcements_capture.json"
        capture = json.loads(capture_path.read_text())
        entry = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        plan = plan_frontier_source(
            frontier_entry=entry,
            tasks=[],
            source_catalog={
                "research/research_os/sources/apple_dividend_announcements_capture.json": {
                    "record": capture,
                    "blob_sha": "6" * 40,
                }
            },
        )
        self.assertEqual(plan["status"], "NO_ADMISSIBLE_DOCUMENTARY_SOURCE")
        self.assertEqual(plan["qualified_count"], 0)

    def test_bound_source_change_fails_closed(self):
        flow = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        faq = "research/research_os/sources/sec_t1_staff_faq.json"
        catalog = {faq: deepcopy(self.catalog[faq])}
        catalog[faq]["blob_sha"] = "7" * 40
        plan = plan_frontier_source(
            frontier_entry=flow,
            tasks=[],
            source_catalog=catalog,
        )
        source = plan["source"]
        task = {
            "inputs": {
                "documentary_source": source["path"],
                "documentary_source_blob": source["blob_sha"],
                "documentary_source_packet_hash": source["packet_hash"],
                "documentary_source_record_hash": source["record_hash"],
            }
        }

        class Snapshot:
            def __init__(self, blob):
                self.blobs = {faq: blob}

            def read(self, path):
                self.assert_path = path
                return catalog[path]["record"]

        V2ResearchOSWorker._verify_bound_source(Snapshot("7" * 40), task)
        with self.assertRaisesRegex(StateConflict, "V2_DERIVED_SOURCE_BLOB_CHANGED"):
            V2ResearchOSWorker._verify_bound_source(Snapshot("8" * 40), task)

    def test_institutional_frontier_explicitly_authorizes_mechanism_research(self):
        flow = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        task = {
            "allowed_actions": flow["allowed_actions"],
            "forbidden_actions": flow["forbidden_actions"],
        }
        require_stage_authorized(task, "mechanism_research")


if __name__ == "__main__":
    unittest.main()
