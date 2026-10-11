import copy
import json
import tempfile
import unittest
from pathlib import Path

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.store import Refused, digest
from quant.edge_lab.planning import register, project, reconcile_software
from quant.edge_lab.worker import start, queue


class Remote:
    def __init__(self, lab, lose=False):
        self.state, self.control = lab.snapshot()
        self.lose, self.published = lose, None

    def snapshot(self):
        return {"sha": "a"*40, "state": copy.deepcopy(self.state), "control": self.control}

    def claim(self, state, parent):
        if self.lose:
            raise Refused("CAS lost")
        self.published = copy.deepcopy(state)
        self.state = copy.deepcopy(state)
        return "b"*40


class PlanningTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        initialize(temp.name); self.lab = Lab(temp.name)
        self.evidence = {"id": "fixture", "kind": "METHOD", "url": "https://example.invalid/docs",
            "version": "synthetic", "passage": "Synthetic catalogue only", "fact": "An unresolved timing question",
            "limit": "No real provider access or outcome"}
        self.lab.evidence(self.evidence)
        for identity in self.lab.snapshot()[0]["decisions"]:
            self.lab.decide(identity,"WAIT",["fixture"],"Fixture blocked")
        self.parent = "qualify:treasury-auction-zf"
        self.row = {"id":"fixture-source", "qualification":"SEARCH_IDENTIFIED", "primary_url":"https://example.invalid/docs"}
        folder=Path(temp.name)/"sources";folder.mkdir()
        (folder/"SOURCE_INVENTORY.json").write_text(json.dumps({"sources":[self.row]}))
        self.packet={"id":"source-one", "source_id":self.row["id"], "source_version":digest(self.row),
            "parent_decision":self.parent, "question_id":"build:treasury-auction-zf:source-clock",
            "question":"Can the unexamined first-reception clock be qualified?", "decision_use":"Admit or park the clock",
            "unresolved_fact":"Release time versus first receipt", "primary_urls":[self.row["primary_url"]],
            "evidence_ids":["fixture"], "trigger_evidence_id":"fixture", "priority":1,
            "bounds":{"max_requests":2,"max_payload_bytes":2000,"timeout_seconds":10,"retries":0,"outcome_access":False}}

    def test_empty_due_queue_promotes_and_claims_once_in_the_same_cas(self):
        register(self.lab,self.packet); before=self.lab.snapshot()[0]
        authority=Remote(self.lab)
        receipt=start(self.lab,authority,"fixture",invocation_id="run")
        self.assertEqual(receipt["status"],"STARTED")
        self.assertEqual(receipt["next"]["id"],self.packet["question_id"])
        self.assertEqual(receipt["next"]["claim_id"],receipt["claim_id"])
        self.assertEqual(authority.published["decisions"][self.packet["question_id"]]["status"],"RESEARCHING")
        self.assertEqual(authority.published["worker_sessions"]["run"]["planning_option"],"source-one")
        for key in ("looks","jobs","protocols","baseline","imported","trial_charges"):
            self.assertEqual(before[key],authority.published[key])

    def test_losing_cas_never_returns_work_or_changes_remote(self):
        register(self.lab,self.packet); authority=Remote(self.lab,lose=True); before=copy.deepcopy(authority.state)
        with self.assertRaisesRegex(Refused,"CAS lost"): start(self.lab,authority,"fixture")
        self.assertEqual(authority.state,before)
        self.assertIsNone(authority.published)

    def test_resolved_option_cannot_return_as_hourly_work_or_renamed_source(self):
        register(self.lab,self.packet); authority=Remote(self.lab)
        r=start(self.lab,authority,"fixture",invocation_id="one")
        self.lab.decide(r["next"]["id"],"WAIT",["fixture"],"Exact source inaccessible",r["claim_id"])
        p=project(*self.lab.snapshot());self.assertEqual(p["consumed"],["source-one"]);self.assertFalse(p["pending"])
        with self.assertRaisesRegex(Refused,"already considered"):
            register(self.lab,{**self.packet,"id":"renamed","question_id":"build:treasury-auction-zf:renamed"})

    def test_due_existing_question_wins_and_future_window_does_not_block_other_source(self):
        self.lab.build_question("build:treasury-auction-zf:future", self.parent,"Future source","After source opens",["fixture"],"2080-01-01T00:00:00Z")
        other=copy.deepcopy(self.packet);other["parent_decision"]="qualify:eurusd-technical-grid";other["question_id"]="build:eurusd-technical-grid:source-clock"
        register(self.lab,other)
        r=start(self.lab,Remote(self.lab),"fixture")
        self.assertEqual(r["next"]["id"],other["question_id"])
        self.assertEqual(self.lab.snapshot()[0]["decisions"]["build:treasury-auction-zf:future"]["status"],"OPEN")

    def test_exhausted_plan_records_honest_idle_and_future_date(self):
        self.lab.build_question("build:treasury-auction-zf:future",self.parent,"Future","Wait",["fixture"],"2080-01-01T00:00:00Z")
        authority=Remote(self.lab);r=start(self.lab,authority,"fixture",invocation_id="idle")
        self.assertEqual(r["status"],"IDLE");self.assertIsNone(r["claim_id"])
        self.assertEqual(authority.published["worker_sessions"]["idle"]["idle_reason"],"WAIT_FOR_DATE")
        self.assertFalse(authority.published["worker_sessions"]["idle"]["delivery_verified"])

    def test_known_blocked_source_changed_catalogue_and_tighter_bounds_fail_closed(self):
        for patch in ({"bounds":{**self.packet["bounds"],"outcome_access":True}},
                      {"bounds":{**self.packet["bounds"],"max_requests":100}}, {"source_version":"0"*64}):
            with self.assertRaises(Refused):register(self.lab,{**self.packet,**patch})
        register(self.lab,self.packet)
        p=Path(self.lab.store.root)/"sources/SOURCE_INVENTORY.json"
        p.write_text(json.dumps({"sources":[{**self.row,"qualification":"RIGHTS_BLOCKED"}]}))
        authority=Remote(self.lab)
        with self.assertRaisesRegex(Refused,"source changed"): start(self.lab,authority,"fixture")
        self.assertIsNone(authority.published)

    def test_existing_session_and_paused_authority_prevent_promotion(self):
        register(self.lab,self.packet);authority=Remote(self.lab);authority.control={**authority.control,"paused":True};before=self.lab.snapshot()[0]
        with self.assertRaisesRegex(Refused,"PAUSED"):start(self.lab,authority,"fixture")
        self.assertEqual(before,self.lab.snapshot()[0])

    def test_software_reconciliation_keeps_original_wait_and_economic_gate(self):
        self.lab.build_question("build:treasury-auction-zf:old",self.parent,"Old software","Code",["fixture"])
        self.lab.decide("build:treasury-auction-zf:old","WAIT",["fixture"],"Needs software")
        self.lab.build_question("build:treasury-auction-zf:done","build:treasury-auction-zf:old","Finish software","Code",["fixture"])
        self.lab.decide("build:treasury-auction-zf:done","QUALIFIED",["fixture"],"Software only")
        before=self.lab.snapshot()[0]
        reconcile_software(self.lab,"build:treasury-auction-zf:old","build:treasury-auction-zf:done",["fixture"],self.parent,"Synthetic completion; source still blocked")
        state,control=self.lab.snapshot();self.assertEqual(state["decisions"],before["decisions"])
        q=queue(state,control);self.assertEqual(q["counts"]["waiting"],queue(before,control)["counts"]["waiting"]-1)
        self.assertEqual(state["decisions"][self.parent]["status"],"WAIT")
        with self.assertRaises(Refused):reconcile_software(self.lab,self.parent,"build:treasury-auction-zf:done",["fixture"],self.parent,"Cannot close economic wait")
        with self.lab.store.lock():
            state=self.lab.store.read();state["decision_reconciliations"]={}
            with self.assertRaises(Refused):self.lab.store.save(state)


if __name__=="__main__": unittest.main()
