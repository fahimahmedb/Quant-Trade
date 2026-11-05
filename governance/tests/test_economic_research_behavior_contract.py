"""Project-owned static policy challenges. NOT an LLM behavioral E2E witness."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
class EconomicBehaviorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads((ROOT/"governance/AI_WORKING_METHOD_V1.json").read_text())
        cls.b=cls.contract["behavioral_economic_research"]
        cls.method=(ROOT/"governance/AI_WORKING_METHOD_V1.md").read_text()
        cls.agents=(ROOT/"AGENTS.md").read_text()

    def test_fresh_and_long_context_are_separately_bound(self):
        self.assertEqual(set(self.b["context_profiles"]),{"FRESH_CONTEXT","LONG_CONTEXT"})
        for role in self.b["context_profiles"]:
            self.assertIn(role,self.method)
            self.assertIn(role,self.agents)
            self.assertGreaterEqual(len(self.b["profile_obligations"][role]),3)
        self.assertIn("## 5.2 Economic research behavior",self.method)
        self.assertIn("Economic research for fresh and long-context AI",self.agents)

    def test_strict_economic_evidence_ceiling(self):
        self.assertEqual(self.b["evidence_ladder"],[
            "MECHANISM_DOCUMENTED","ACCESS_VERIFIED","PIT_SIGNAL_ADMISSIBLE",
            "OBSERVED_INDICATIVE_PRICES","EXECUTION_MODEL_TESTED",
            "NET_EXECUTION_OBSERVED","REPEATABILITY_PROVEN"])
        self.assertEqual(self.b["economic_edge_status_until_proven"],"UNKNOWN")
        self.assertTrue(self.b["never_infer_profit_from_workflow_success"])
        self.assertTrue(self.b["never_infer_arbitrage_from_normalized_bars"])
        self.assertFalse(self.b["economic_authority_granted"])
        self.assertFalse(self.b["capital_or_live_authority_granted"])
        self.assertEqual(self.b["behavioral_e2e_witness"],"NOT_PROVEN")

    def test_adversarial_cases_cover_both_profiles(self):
        cases=self.b["behavioral_challenges"]
        ids=[x["id"] for x in cases]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(cases),14)
        for x in cases:
            self.assertIn(x["profile"],{"BOTH","FRESH_CONTEXT","LONG_CONTEXT"})
            self.assertTrue(x["situation"])
            self.assertTrue(x["expected_action"])
            self.assertTrue(x["forbidden_action"])
        for required in (
            "PUSH_RUN_PR_FILTER","SAME_WINDOW_REDOWNLOAD","YAHOO_OHLCV_ARBITRAGE",
            "NEGATIVE_ORACLE_SCOPING","F1_NEGATIVE_FROZEN_EXPRESSION",
            "RUSSELL_SOURCE_BLOCK","ODDLOT_CUTOFF","BROKER_TAX_ACCESS",
            "FRESH_RECONCILE","LONG_CONTEXT_ANCHOR","NO_PROFIT_WITHOUT_EXECUTIONS",
            "DATA_CONVENIENCE_BIAS","RESTATEMENT_CONTROL",
            "PROSPECTIVE_PROTOCOL_LOCK","LOCAL_BLOCK_SCOPE"):
            self.assertIn(required,ids)

    def test_regression_old_authority_and_gate_contract(self):
        c=self.contract
        self.assertEqual(c["contract_version"],1)
        self.assertEqual(c["two_branch_mode"],"ENFORCED")
        self.assertEqual(c["post_migration_remote_branches"],["project/canonical","code/canonical"])
        self.assertEqual([g["id"] for g in c["finish_gates"]],[
            "F0_TWO_BRANCH_AUTHORITY","F1_RECOVERABLE_CANONICAL_STATE",
            "F2_EXACT_HEAD_ENGINEERING_QUALIFICATION","F3_REAL_VM_MULTI_WAKE",
            "F4_GLOBAL_MISSION_CONTINUATION","F5_IDENTITY_CONSERVING_E2E",
            "F6_OPERATIONAL_HANDOFF"])
        self.assertEqual(c["mission_admission"]["receipt_path"],".quant/MISSION_ADMISSION.json")
        self.assertEqual(c["mission_admission"]["material_change_exempt_prefixes"],["data/feeds/"])
        self.assertFalse(c["hard_laws"]["code_pass_grants_scientific_or_capital_authority"])
        self.assertFalse(c["hard_laws"]["primary_evidence_contradiction_may_be_overridden"])
        self.assertTrue(c["behavioral_opportunity_rescue"]["terminal_disposition_required"])
        self.assertEqual(c["concurrency"]["max_active_decision_lanes"],2)
        self.assertEqual(c["concurrency"]["max_mutating_builders_per_capability"],1)

    def test_context_and_reopen_do_not_fabricate_facts(self):
        self.assertEqual(self.b["on_head_change"],"RECONCILE_BEFORE_DECIDING")
        self.assertEqual(self.b["on_undocumented_claim"],"UNKNOWN_SOURCE")
        self.assertTrue(self.b["no_new_gate_or_router"])
        for s in (self.method,self.agents):
            self.assertIn("PIT",s)
            self.assertIn("fresh",s.lower())
            self.assertIn("historical",s.lower())

if __name__=="__main__":
    unittest.main()
