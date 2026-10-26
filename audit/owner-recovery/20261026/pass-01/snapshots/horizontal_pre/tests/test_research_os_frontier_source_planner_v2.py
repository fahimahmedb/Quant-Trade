import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from research.research_os.frontier_source_planner_v2 import plan_frontier_source
from research.research_os.github_state import StateConflict
from research.research_os.oracle_worker_v2 import V2ResearchOSWorker
from research.research_os.oracle_worker import ResearchOSWorker
from research.research_os.queue_replenisher import derive_refill_task, load_source_catalog
from research.research_os.worker_stages import require_stage_authorized


BASE = Path("research/research_os")
AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)
PRODUCER_STAGE = {
    "FUNDAMENTAL_RESEARCH": "document_or_fundamental_research",
    "EVENT_DOCUMENT": "document_or_fundamental_research",
    "INSTITUTIONAL_FLOW": "mechanism_research",
    "QUANT_MECHANISM": "mechanism_research",
}


class FrontierSourcePlannerV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = json.loads((BASE / "runtime" / "RESEARCH_FRONTIER.json").read_text())
        cls.catalog = load_source_catalog(BASE)

    def entry(self, frontier_id):
        return next(item for item in self.frontier["frontiers"] if item["frontier_id"] == frontier_id)

    @staticmethod
    def historical_task(entry, sequence=1, *, producer_completed=False):
        task = {
            "task_id": f"HIST-{entry['frontier_id']}-{sequence}",
            "task_type": entry["task_type"],
            "status": "BLOCKED",
            "inputs": {},
            "derivation": {
                "frontier_id": entry["frontier_id"],
                "sequence": sequence,
                "derivation_key": f"historical-{entry['frontier_id']}-{sequence}",
            },
            "execution": {"completed_stages": {}},
        }
        if producer_completed:
            stage = PRODUCER_STAGE[entry["task_type"]]
            task["execution"]["completed_stages"][stage] = {
                "artifact": f"artifacts/{task['task_id']}/{stage}.json",
                "artifact_hash": "a" * 64,
            }
        return task

    def test_preproducer_block_does_not_consume_institutional_default(self):
        entry = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        plan = plan_frontier_source(
            frontier_entry=entry,
            tasks=[self.historical_task(entry, producer_completed=False)],
            source_catalog=self.catalog,
        )
        self.assertEqual(plan["status"], "SOURCE_SELECTED")
        self.assertEqual(
            plan["source"]["path"],
            "research/research_os/sources/sec_t1_operative_rule.json",
        )
        self.assertEqual(plan["source"]["evidence_kind"], "STANDARD_SETTLEMENT_OPERATIVE_RULE")
        self.assertEqual(plan["source"]["evidence_authority_rank"], 0)

    def test_institutional_faq_selected_only_after_default_rule_really_consumed(self):
        entry = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        plan = plan_frontier_source(
            frontier_entry=entry,
            tasks=[self.historical_task(entry, producer_completed=True)],
            source_catalog=self.catalog,
        )
        self.assertEqual(plan["status"], "SOURCE_SELECTED")
        self.assertEqual(
            plan["source"]["path"],
            "research/research_os/sources/sec_t1_staff_faq.json",
        )
        self.assertEqual(plan["source"]["evidence_kind"], "STANDARD_SETTLEMENT_CONSTRAINT_EXPLANATION")
        self.assertGreater(plan["source"]["evidence_authority_rank"], 0)
        self.assertEqual(plan["family"], "INSTITUTIONAL_FLOW")
        self.assertGreaterEqual(plan["qualified_count"], 2)

    def test_event_and_fundamental_defaults_are_exhausted_only_after_producer_completion(self):
        for frontier_id in ("EVENT_DOCUMENT_DISTINCT_MECHANISM", "FUNDAMENTAL_DISTINCT_THESIS"):
            entry = self.entry(frontier_id)
            unused = plan_frontier_source(
                frontier_entry=entry,
                tasks=[self.historical_task(entry, producer_completed=False)],
                source_catalog=self.catalog,
            )
            self.assertEqual(unused["status"], "SOURCE_SELECTED")
            consumed = plan_frontier_source(
                frontier_entry=entry,
                tasks=[self.historical_task(entry, producer_completed=True)],
                source_catalog=self.catalog,
            )
            self.assertEqual(consumed["status"], "NO_UNUSED_ADMISSIBLE_SOURCE")
            self.assertIsNone(consumed["source"])

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

    def test_source_aware_refill_binds_strongest_unused_institutional_source(self):
        event = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        fundamental = self.entry("FUNDAMENTAL_DISTINCT_THESIS")
        flow = self.entry("INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        tasks = [
            self.historical_task(event, producer_completed=True),
            self.historical_task(fundamental, producer_completed=True),
            self.historical_task(flow, producer_completed=False),
        ]
        catalog = deepcopy(self.catalog)
        rule = "research/research_os/sources/sec_t1_operative_rule.json"
        catalog[rule]["blob_sha"] = "5" * 40
        result = derive_refill_task(
            frontier=self.frontier,
            tasks=tasks,
            created_at="2026-10-20T15:01:00Z",
            source_catalog=catalog,
        )
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        self.assertEqual(result["selected_frontier"], "INSTITUTIONAL_FLOW_DISTINCT_MECHANISM")
        task = result["task"]
        self.assertEqual(task["inputs"]["documentary_source"], rule)
        self.assertEqual(task["inputs"]["documentary_source_blob"], "5" * 40)
        self.assertEqual(
            task["inputs"]["documentary_source_packet_hash"],
            catalog[rule]["record"]["documentary_packet"]["content_hash"],
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
        rule = "research/research_os/sources/sec_t1_operative_rule.json"
        catalog = {rule: deepcopy(self.catalog[rule])}
        catalog[rule]["blob_sha"] = "7" * 40
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
                self.blobs = {rule: blob}

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

    def test_renamed_reserved_content_is_not_novel_for_any_bound_identity(self):
        entry = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        original = "research/research_os/sources/apple_dividend_announcements.json"
        alias = "research/research_os/sources/renamed_packet.json"
        catalog = {alias: deepcopy(self.catalog[original])}
        catalog[alias]["blob_sha"] = "a" * 40
        source = plan_frontier_source(frontier_entry=entry, tasks=[], source_catalog=catalog)["source"]
        for field, value in (("packet_hash", source["packet_hash"]),
                             ("record_hash", source["record_hash"]), ("blob", "a" * 40)):
            with self.subTest(identity=field):
                task = self.historical_task(entry)
                task["inputs"] = {"documentary_source": original, "documentary_source_" + field: value}
                plan = plan_frontier_source(frontier_entry=entry, tasks=[task], source_catalog=catalog)
                self.assertEqual(plan["status"], "NO_UNUSED_ADMISSIBLE_SOURCE")
                self.assertIsNone(plan["source"])

    def test_consumption_is_frontier_scoped_and_new_version_is_eligible(self):
        entry = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        path = "research/research_os/sources/apple_dividend_announcements.json"
        source = plan_frontier_source(frontier_entry=entry, tasks=[],
                                      source_catalog={path: self.catalog[path]})["source"]
        task = self.historical_task(entry)
        task["inputs"] = {"documentary_source": path, "documentary_source_packet_hash": source["packet_hash"]}
        other = deepcopy(task)
        other["derivation"]["frontier_id"] = "OTHER_FRONTIER"
        self.assertEqual(plan_frontier_source(frontier_entry=entry, tasks=[other],
                         source_catalog={path: self.catalog[path]})["status"], "SOURCE_SELECTED")
        task["inputs"]["documentary_source_packet_hash"] = "previous-immutable-version"
        self.assertEqual(plan_frontier_source(frontier_entry=entry, tasks=[task],
                         source_catalog={path: self.catalog[path]})["status"], "SOURCE_SELECTED")

    def test_alias_cannot_manufacture_a_refill_task(self):
        entry = self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")
        path = "research/research_os/sources/apple_dividend_announcements.json"
        source = plan_frontier_source(frontier_entry=entry, tasks=[],
                                      source_catalog={path: self.catalog[path]})["source"]
        task = self.historical_task(entry)
        task["inputs"] = {"documentary_source": path, "documentary_source_packet_hash": source["packet_hash"]}
        frontier = deepcopy(self.frontier)
        frontier["frontiers"] = [entry]
        result = derive_refill_task(frontier=frontier, tasks=[task], created_at="2026-10-20T20:00:00Z",
                                   source_catalog={"research/research_os/sources/alias.json": self.catalog[path]})
        self.assertEqual(result["status"], "NOOP_NO_ADMISSIBLE_NOVEL_SOURCE")
        self.assertIsNone(result["task"])

    def source_aware_task(self):
        frontier = deepcopy(self.frontier)
        frontier["frontiers"] = [self.entry("EVENT_DOCUMENT_DISTINCT_MECHANISM")]
        catalog = deepcopy(self.catalog)
        for entry in catalog.values():
            entry["blob_sha"] = "a" * 40
        return derive_refill_task(frontier=frontier, tasks=[], created_at="2026-10-20T20:00:00Z",
                                 source_catalog=catalog)["task"]

    def test_derived_selection_mismatch_blocks_before_reading_source(self):
        task = self.source_aware_task()
        class NoReads:
            def read(self, path):
                raise AssertionError("must reject task binding before source access")
        for key in ("documentary_source", "documentary_source_blob",
                    "documentary_source_packet_hash", "documentary_source_record_hash"):
            for change in ("remove", "replace"):
                with self.subTest(field=key, change=change):
                    altered = deepcopy(task)
                    if change == "remove":
                        altered["inputs"].pop(key)
                    else:
                        altered["inputs"][key] = "different"
                    with self.assertRaisesRegex(StateConflict, "V2_DERIVED_SOURCE_BINDING_INVALID"):
                        V2ResearchOSWorker._verify_bound_source(NoReads(), altered)

    def test_source_aware_binding_cannot_downgrade_to_legacy_fallback(self):
        task = self.source_aware_task()
        for binding in (None, {}, [], "invalid"):
            altered = deepcopy(task)
            altered["derivation"]["source_binding"] = binding
            with self.subTest(binding=binding), self.assertRaisesRegex(StateConflict, "BINDING_INVALID"):
                V2ResearchOSWorker._verify_bound_source(object(), altered)
        altered = deepcopy(task)
        del altered["derivation"]["source_binding"]
        with self.assertRaisesRegex(StateConflict, "BINDING_INVALID"):
            V2ResearchOSWorker._verify_bound_source(object(), altered)
        # Actual producer input/content remains admissible at any task status.
        class Snapshot:
            blobs = {task["inputs"]["documentary_source"]: "a" * 40}
            def read(inner, path):
                return self.catalog[path]["record"]
        for status in ("READY", "CLAIMED"):
            task["status"] = status
            V2ResearchOSWorker._verify_bound_source(Snapshot(), task)
        task["inputs"]["documentary_source_blob"] = None
        task["derivation"]["source_binding"]["blob_sha"] = None
        V2ResearchOSWorker._verify_bound_source(Snapshot(), task)
        V2ResearchOSWorker._verify_bound_source(object(), {"inputs": {}, "derivation": {
            "type": "EMPTY_QUEUE_FRONTIER_REFILL"}})

    def test_selection_and_lease_recheck_the_original_source_selection(self):
        task = self.source_aware_task()
        task["inputs"]["documentary_source"] = "research/research_os/sources/switched.json"
        worker = object.__new__(V2ResearchOSWorker)
        with patch.object(ResearchOSWorker, "_select", return_value=(task, "lane")):
            with self.assertRaisesRegex(StateConflict, "BINDING_INVALID"):
                worker._select(object())
        with patch.object(ResearchOSWorker, "_verify_lease", return_value=(task, {})):
            with self.assertRaisesRegex(StateConflict, "BINDING_INVALID"):
                worker._verify_lease(object(), task["task_id"], 1, "session", "lane")


if __name__ == "__main__":
    unittest.main()
