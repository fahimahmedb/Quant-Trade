"""Actual Python observer packets through the imported JS mapper/reducer.

Site acceptance is a local fixture: this is not production ingress/SSE proof.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from deploy.oracle_live_projection import ACTIVITIES, LANES, LiveProjection
from research.research_os.live_lab_contract import LANE_UI, STAGE_ACTIVITY
from tests import test_oracle_live_projection as fixtures

LAB = Path(__file__).resolve().parents[1] / "research/live_lab_ux"
JS = """
import fs from 'node:fs';
import {createInitialState,reduceScene} from './core/state-machine.js';
import {mapNativeWorkerEvent,mapNativeSnapshot} from './adapters/platform-native.js';
import {EVENT} from './core/model.js';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
let state=reduceScene(createInitialState({mode:'LIVE'}),{
 id:'connected',seq:1,stream:'transport',at:'2026-10-20T10:00:00Z',kind:EVENT.CONNECTED});
const states=[];
for(const action of input){
 const mapped=action.snapshot ? mapNativeSnapshot(action.snapshot) : mapNativeWorkerEvent(action.event);
 if(mapped) state=reduceScene(state,mapped);
 states.push(state);
}
process.stdout.write(JSON.stringify(states));
"""


class OracleLiveCompositionTests(unittest.TestCase):
    def project(self, site, source_id="source-1", lane="fundamental_events", stage="document_or_fundamental_research"):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        projection = LiveProjection(site, Path(temporary.name))
        self.addCleanup(projection.stop.set)
        event = dict(event_id=source_id + "-start", session_id=source_id,
                     worker_id="oracle-research." + lane, action_id="test-task",
                     generation=42, event_seq=1, emitted_at="2026-10-20T11:00:00Z",
                     event_type="ACTION_STARTED")
        projection.started(event, lane, stage, "a" * 40)
        return projection, event

    def states(self, actions):
        result = subprocess.run(["node", "--input-type=module", "-e", JS],
                                input=json.dumps(actions), text=True, capture_output=True,
                                cwd=LAB, timeout=15, check=True)
        return json.loads(result.stdout)

    def packets(self, site):
        return [deepcopy(packet) for route, packet in site.requests if route == "event"]

    def test_runtime_and_frontend_share_exact_explicit_metadata_taxonomy(self):
        self.assertEqual(LANES, LANE_UI)
        self.assertEqual(ACTIVITIES, STAGE_ACTIVITY)
        self.assertNotIn("calculation-economic-look", ACTIVITIES.values())

    def test_real_observer_packet_shapes_drive_factual_roles_and_unknown_progress(self):
        for lane, stage in (("market_discovery", "mechanism_research"),
                            ("fundamental_events", "document_or_fundamental_research"),
                            ("independent_challenge", "independent_validation"),
                            ("evidence_data", "provenance_check"),
                            ("integrator_portfolio", "portfolio_map")):
            with self.subTest(lane=lane):
                site = fixtures.NativeSite()
                projection, _ = self.project(site, lane=lane, stage=stage)
                start = self.packets(site)[0]
                agent = self.states([{"event": start}])[0]["agents"][start["worker_id"]]
                self.assertEqual(agent["role"], LANES[lane][0])
                self.assertEqual(agent["label"], LANES[lane][1])
                self.assertEqual(agent["progress"], {"mode": "UNKNOWN"})
                self.assertTrue(agent["animationRunning"])
                self.assertEqual(start["generation"], 1)  # Site generation, not canonical 42.
                self.assertEqual(projection.source["generation"], 42)
                projection.stop.set()

    def test_completion_snapshot_and_duplicate_do_not_replay_business_motion(self):
        site = fixtures.NativeSite()
        projection, event = self.project(site)
        start = self.packets(site)[0]
        projection._post_event("WORKER_HEARTBEAT", "heartbeat", {}, event["emitted_at"])
        heartbeat = self.packets(site)[-1]
        projection.terminal = dict(event, event_id="terminal", event_type="ACTION_COMPLETED",
                                   event_seq=2, source_commit="b" * 40)
        projection.finished(b'{"status":"BLOCKED","hosted_model_calls":0}\n', 0)
        terminal = self.packets(site)[-2]
        self.assertEqual(self.states([{"event": heartbeat}])[0]["agents"], {})
        states = self.states([{"event": start}, {"event": heartbeat}, {"event": terminal},
                              {"snapshot": {"generated_at": "2026-10-20T11:01:00Z", "events": [start, terminal]}},
                              {"event": start}])
        self.assertTrue(states[0]["agents"][start["worker_id"]]["animationRunning"])
        self.assertTrue(states[1]["agents"][start["worker_id"]]["animationRunning"])
        for state in states[2:]:
            self.assertFalse(state["agents"][start["worker_id"]]["animationRunning"])

    def test_late_old_site_generation_cannot_restart_a_completed_new_wake(self):
        site = fixtures.NativeSite()
        old, _ = self.project(site, "old")
        old.stop.set()
        old_start = self.packets(site)[0]
        current, event = self.project(site, "new")
        current_start = self.packets(site)[-1]
        current.terminal = dict(event, event_id="new-terminal", event_type="ACTION_COMPLETED",
                                event_seq=2, source_commit="c" * 40)
        current.finished(b'{"status":"BLOCKED"}\n', 0)
        terminal = self.packets(site)[-2]
        actions = [{"event": packet} for packet in (old_start, current_start, terminal, old_start)]
        states = self.states(actions)
        self.assertFalse(states[-1]["agents"][old_start["worker_id"]]["animationRunning"])
