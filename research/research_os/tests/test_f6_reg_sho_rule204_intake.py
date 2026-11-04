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
        frontier["frontiers"].append(frontier_entry())
        tasks = load_tasks(BASE)
        catalog = {TARGET: source()}
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
        self.assertFalse((BASE / "tasks" / (task["task_id"] + ".json")).exists(),
                         "Preview must never publish to the operational research queue")

    def test_preflight_no_matching_source_yields_no_task(self):
        frontier = deepcopy(load_frontier(BASE))
        frontier["frontiers"].append(frontier_entry())
        result = derive_refill_task(
            frontier=frontier, tasks=load_tasks(BASE), created_at="2026-11-04T03:27:00Z",
            source_catalog={"research/research_os/sources/sec_t1_operative_rule.json":
                            json.loads(OLD_T1.read_text())},
            research_policy_context=load_research_policy_context(BASE))
        self.assertIsNone(result["task"])


if __name__ == "__main__":
    unittest.main()
