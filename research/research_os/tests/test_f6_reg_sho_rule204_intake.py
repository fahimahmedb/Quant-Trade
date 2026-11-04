"""F6 non-economic Rule204 source prequalification and one-task *offline* intake preview."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError
from research.research_os.expansion.engine_dossiers_v1 import (
    build_engine_dossier, qualify_document_packet,
)
from research.research_os.expansion.source_adapters_v1 import reg_sho_rule204_packet
from research.research_os.frontier_source_planner_v2 import plan_frontier_source
from research.research_os.queue_replenisher import (
    derive_refill_task, load_frontier, load_tasks, load_research_policy_context,
    validate_derived_task,
)
from research.research_os.scientific_store import sha256_json

BASE = Path(__file__).resolve().parents[1]
STAGED = BASE / "sources" / "staging" / "reg_sho_rule204_2025.json"
TARGET = "research/research_os/sources/reg_sho_rule204_2025.json"
OLD_T1 = BASE / "sources" / "sec_t1_operative_rule.json"


def source():
    return json.loads(STAGED.read_text())


def frontier_entry():
    frontier = load_frontier(BASE)
    original = next(item for item in frontier["frontiers"]
                    if item["task_type"] == "INSTITUTIONAL_FLOW")
    item = deepcopy(original)
    item["frontier_id"] = "INSTITUTIONAL_FLOW_REGSHO_RULE204_2025"
    item["required_source_rule_kind"] = "REG_SHO_CLOSEOUT_OPERATIVE_RULE"
    item["objective"] = (
        "Evaluate exactly one dated SEC Rule204 equity fail-to-deliver closeout "
        "documentary premise without inferring flows, outcomes or economic results. "
        "Screen Legacy before any freeze; allow NO_CANDIDATE."
    )
    return item


class F6Rule204SourceTests(unittest.TestCase):
    def test_official_capture_reproduces_exact_pinned_packet(self):
        s = source()
        packet = s["documentary_packet"]
        self.assertEqual(reg_sho_rule204_packet(packet["capture"]), packet)
        self.assertEqual(qualify_document_packet(packet, "INSTITUTIONAL_FLOW",
                                                 s["freeze_time"])["status"], "PASS")
        self.assertEqual(packet["content_hash"], sha256_json(
            {k: v for k, v in packet.items() if k != "content_hash"}))
        self.assertEqual(packet["capture"]["source_workflow_run"], 41767148087)

    def test_tampered_primary_receipt_and_text_fail_closed(self):
        s = source()
        for key, value in (
            ("raw_sha256", "0" * 64),
            ("section_text_sha256", "0" * 64),
            ("section_text_zlib_b64", "eJwL"),
            ("section", "17 CFR 240.15c6-1"),
        ):
            tampered = deepcopy(s)
            tampered["documentary_packet"]["capture"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                reg_sho_rule204_packet(tampered["documentary_packet"]["capture"])

    def test_engine_is_documentary_only_and_dossier_not_economic_pass(self):
        output = ENGINE_REGISTRY["institutional_flow"].run(
            source(), EngineContext("F6-RULE204-BOUNDED", synthetic_only=False))
        candidate = output["candidate"]
        self.assertEqual(candidate["documentary_evidence"]["economic_result"], "NOT_OBSERVED")
        self.assertFalse(output.get("outcome_accessed", False))
        self.assertEqual(candidate["hypothesis_id"], "DOC-FLOW-7ddc4c400115df87")
        self.assertIn("UNKNOWN", candidate["claim"])
        dossier = build_engine_dossier(output)
        self.assertEqual(dossier["claim_ceiling"], "DOCUMENTED_FACTS_ONLY")
        self.assertEqual(dossier["status"], "BLOCK")
        self.assertFalse(dossier.get("outcome_accessed", False))

    def test_unsupported_retrospective_claim_cannot_pass_source_qualification(self):
        bad = source()
        bad["documentary_packet"]["facts"]["base_closeout_following_settlement_days"] = "0"
        self.assertEqual(qualify_document_packet(
            bad["documentary_packet"], "INSTITUTIONAL_FLOW", bad["freeze_time"])["status"], "BLOCK")
        with self.assertRaises(EngineContractError):
            ENGINE_REGISTRY["institutional_flow"].run(
                bad, EngineContext("F6-ADVERSARIAL", synthetic_only=False))

    def test_rule_kind_filter_excludes_previous_settlement_source(self):
        entry = frontier_entry()
        catalog = {
            TARGET: source(),
            "research/research_os/sources/sec_t1_operative_rule.json": json.loads(OLD_T1.read_text()),
        }
        plan = plan_frontier_source(frontier_entry=entry, tasks=[], source_catalog=catalog)
        self.assertEqual(plan["status"], "SOURCE_SELECTED")
        self.assertEqual(plan["source"]["path"], TARGET)
        self.assertEqual(plan["source"]["packet_hash"], source()["documentary_packet"]["content_hash"])
        self.assertEqual(len(plan["rejections"]), 1)
        self.assertEqual(plan["rejections"][0]["reason"], "FRONTIER_RULE_KIND_MISMATCH")

    def test_only_existing_12_issued_frontiers_and_one_new_bounded_candidate(self):
        frontier = deepcopy(load_frontier(BASE))
        frontier["frontiers"] = [
            item for item in frontier["frontiers"]
            if item["frontier_id"] != "INSTITUTIONAL_FLOW_RULE204_PIT_RESCUE_EPOCH2"
        ]
        # Production runtime may already contain the first real Rule204 task;
        # isolate the 72 terminal predecessor tasks for this offline preview.
        tasks = [task for task in load_tasks(BASE)
                 if (task.get("derivation") or {}).get("frontier_id")
                 != "INSTITUTIONAL_FLOW_REGSHO_RULE204_2025"]
        catalog = {TARGET: source()}
        task_files_before = {item.name for item in (BASE / "tasks").glob("*.json")}
        result = derive_refill_task(
            frontier=frontier, tasks=tasks, created_at="2026-11-04T03:27:00Z",
            source_catalog=catalog, research_policy_context=load_research_policy_context(BASE))
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        task = result["task"]
        self.assertEqual(task["derivation"]["frontier_id"], "INSTITUTIONAL_FLOW_REGSHO_RULE204_2025")
        self.assertEqual(task["inputs"]["documentary_source"], TARGET)
        self.assertEqual(task["inputs"]["research_intelligence_contract"]["novelty_status"],
                         "UNRESOLVED_NOT_CLAIMED")
        self.assertTrue(task["inputs"]["legacy_gate_required"])
        self.assertFalse(task["authority"]["live_trading_authorized"])
        validate_derived_task(task)
        self.assertEqual({item.name for item in (BASE / "tasks").glob("*.json")},
                         task_files_before,
                         "Offline preview must not mutate the operational research queue")

    def test_operational_one_source_frontier_after_qualified_vm_rebind(self):
        from research.research_os.queue_replenisher import load_source_catalog
        current = deepcopy(load_frontier(BASE))
        current["frontiers"] = [
            item for item in current["frontiers"]
            if item["frontier_id"] != "INSTITUTIONAL_FLOW_RULE204_PIT_RESCUE_EPOCH2"
        ]
        new = next(item for item in current["frontiers"]
                   if item["frontier_id"] == "INSTITUTIONAL_FLOW_REGSHO_RULE204_2025")
        self.assertTrue(new["enabled"], "Separate F6 admission requires qualified real-VM upgrade")
        self.assertEqual(new["required_source_rule_kind"], "REG_SHO_CLOSEOUT_OPERATIVE_RULE")
        self.assertEqual(current["max_new_tasks_per_refill"], 1)
        self.assertFalse(current["producer_execution_same_refill_wake"])
        self.assertFalse(current["recursive_refill_same_wake"])
        self.assertTrue(all(value is False for value in current["authority"].values()))

        actual_tasks = load_tasks(BASE)
        live = [t for t in actual_tasks if (t.get("derivation") or {}).get("frontier_id")
                == new["frontier_id"]]
        self.assertLessEqual(len(live), 1, "Never issue a second Rule204 task")
        historical = [t for t in actual_tasks if t not in live]
        catalog = load_source_catalog(BASE)
        # Production V2 also sees the staged copy. Both copies have the same
        # packet hash and cannot be counted as independent scientific sources.
        catalog["research/research_os/sources/staging/reg_sho_rule204_2025.json"] = {
            "record": source()
        }
        first = derive_refill_task(
            frontier=current, tasks=historical,
            created_at="2026-11-04T11:58:00Z",
            source_catalog=catalog,
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertEqual(first["status"], "DERIVED_ONE_READY_TASK")
        task = first["task"]
        self.assertEqual(task["derivation"]["frontier_id"], new["frontier_id"])
        self.assertEqual(task["inputs"]["documentary_source"], TARGET)
        self.assertEqual(task["inputs"]["documentary_source_packet_hash"],
                         source()["documentary_packet"]["content_hash"])
        validate_derived_task(task)
        second = derive_refill_task(
            frontier=current, tasks=historical + [task],
            created_at="2026-11-04T11:59:00Z",
            source_catalog=catalog,
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertEqual(second["status"], "NOOP_QUEUE_NOT_EMPTY")
        self.assertIsNone(second["task"])
        terminal = deepcopy(task)
        terminal["status"] = "COMPLETE"
        third = derive_refill_task(
            frontier=current, tasks=historical + [terminal],
            created_at="2026-11-04T12:10:00Z",
            source_catalog=catalog,
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertIsNone(third["task"], "Same packet under staging alias must never refill twice")

    def test_new_epoch_candidate_is_only_staged_until_governed_activation(self):
        # Successor epoch was predeclared before its future 15:30Z opening.
        from datetime import datetime, timezone
        from research.research_os.expansion.v2_core import (
            build_epoch_manifest, assert_epoch_blinding,
        )
        from research.research_os.expansion.v2_stage_executor import _source_pit
        from research.research_os.queue_replenisher import load_source_catalog

        staged = BASE / "runtime" / "epoch_admissions"
        prior = json.loads((staged / "F6_RULE204_PREDECESSOR_EPOCH_20261020.json").read_text())
        successor = json.loads((staged / "F6_RULE204_EPOCH_20261104.json").read_text())
        active_epoch = json.loads((BASE / "runtime" / "V2_ACTIVE_EPOCH.json").read_text())
        self.assertEqual(active_epoch, successor, "Runtime epoch must be the qualified predeclared snapshot")
        frontier = json.loads((staged / "F6_RULE204_FRONTIER_20261104.json").read_text())
        new_id = "INSTITUTIONAL_FLOW_RULE204_PIT_RESCUE_EPOCH2"
        source_packet = source()["documentary_packet"]
        to_time = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
        self.assertEqual(prior["research_epoch_id"], "ORACLE-V2-EPOCH-20261020-001")
        self.assertEqual(prior["knowledge_cutoff"], "2026-10-20T01:00:00Z")
        self.assertEqual(successor["parent_epoch_id"], prior["research_epoch_id"])
        self.assertEqual(successor["epoch_knowledge_parent"], prior["research_epoch_id"])
        self.assertEqual(successor["epoch_feedback_dependencies"], [])
        self.assertFalse(successor["first_evaluation_export_accepted"])
        self.assertEqual(successor["max_candidate_exports"], 1)
        self.assertTrue(to_time(source_packet["available_at"]) < to_time(successor["knowledge_cutoff"])
                        < to_time(successor["opened_at"]))
        manifest = build_epoch_manifest(successor)
        self.assertEqual(assert_epoch_blinding(
            manifest, owner_status=successor["owner_outcome_blinding_status"],
            supervisor_status=successor["supervisor_outcome_blinding_status"],
        )["epoch_blinding_integrity"], "PASS")
        packet_output = {"candidate": {"documentary_evidence": {"packet": source_packet}}}
        self.assertEqual(_source_pit(packet_output, prior)["source_pit"], "FAIL")
        self.assertEqual(_source_pit(packet_output, successor)["source_pit"], "PASS")
        self.assertEqual([entry["frontier_id"] for entry in frontier["frontiers"] if not entry["enabled"]],
                         [new_id], "Staging never activates the successor frontier")
        self.assertEqual(frontier["frontiers"][:-1], load_frontier(BASE)["frontiers"][:5])
        self.assertTrue(all(flag is False for flag in frontier["authority"].values()))

        historical_tasks = load_tasks(BASE)
        blocked = [t for t in historical_tasks if t.get("task_id") ==
                   "FRONTIER-INSTITUTIONAL-FLOW-REGSHO-RULE204-2025-001"]
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0]["status"], "BLOCKED")
        self.assertNotIn("mechanism_research",
                         (blocked[0].get("execution") or {}).get("completed_stages") or {})
        ready_frontier = deepcopy(frontier)
        ready_frontier["frontiers"][-1]["enabled"] = True
        result = derive_refill_task(
            frontier=ready_frontier, tasks=historical_tasks,
            created_at="2026-11-04T15:31:00Z",
            source_catalog=load_source_catalog(BASE),
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        task = result["task"]
        self.assertEqual(task["derivation"]["frontier_id"], new_id)
        self.assertEqual(task["inputs"]["documentary_source"], TARGET)
        self.assertEqual(task["inputs"]["documentary_source_packet_hash"],
                         source_packet["content_hash"])
        validate_derived_task(task)
        self.assertTrue(all(task["authority"][flag] is False for flag in (
            "economic_experiment_authorized", "prospective_observation_authorized",
            "real_capital_authorized", "live_trading_authorized",
        )))
        self.assertEqual(task["authority"]["scope"], "BOUNDED_FRONTIER_DISCOVERY_AND_FREEZE_ONLY")
        again = derive_refill_task(
            frontier=ready_frontier, tasks=historical_tasks + [task],
            created_at="2026-11-04T15:41:00Z",
            source_catalog=load_source_catalog(BASE),
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertIsNone(again["task"], "No second source issuance when READY exists")
        done = deepcopy(task)
        done["status"] = "BLOCKED"
        again_terminal = derive_refill_task(
            frontier=ready_frontier, tasks=historical_tasks + [done],
            created_at="2026-11-04T15:51:00Z",
            source_catalog=load_source_catalog(BASE),
            research_policy_context=load_research_policy_context(BASE),
        )
        self.assertIsNone(again_terminal["task"], "Terminal source identity cannot be reused")

    def test_preflight_no_matching_source_yields_no_task(self):
        frontier = deepcopy(load_frontier(BASE))
        frontier["frontiers"].append(frontier_entry())
        old_tasks = [task for task in load_tasks(BASE)
                     if (task.get("derivation") or {}).get("frontier_id")
                     != "INSTITUTIONAL_FLOW_REGSHO_RULE204_2025"]
        result = derive_refill_task(
            frontier=frontier, tasks=old_tasks, created_at="2026-11-04T03:27:00Z",
            source_catalog={"research/research_os/sources/sec_t1_operative_rule.json":
                            json.loads(OLD_T1.read_text())},
            research_policy_context=load_research_policy_context(BASE))
        self.assertIsNone(result["task"])


if __name__ == "__main__":
    unittest.main()
