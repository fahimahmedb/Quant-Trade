import test from 'node:test';
import assert from 'node:assert/strict';
import {ACTIVITY,EVENT,PROGRESS} from '../core/model.js';
import {createInitialState,reduceScene} from '../core/state-machine.js';
import {mapNativeSnapshot,mapNativeWorkerEvent} from '../adapters/platform-native.js';
import {gestureFamily} from '../ui/motion-authority.js';

const oracle=(overrides={})=>({
  event_id:'oracle-live-event-1',
  session_id:'FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-TEST-g5-abc',
  worker_id:'oracle-research.fundamental_events',
  action_id:'FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-TEST',
  event_type:'ACTION_STARTED',
  event_seq:1,
  generation:5,
  emitted_at:'2026-10-20T02:10:00Z',
  accepted_at:'2026-10-20T02:10:01Z',
  payload:{
    stage:'document_or_fundamental_research',
    label:'Fundamental research stage',
    ui_activity:ACTIVITY.DOCUMENT_READING,
    ui_role:'researcher',
    ui_label:'Oracle · Documents',
  },
  ...overrides,
});

test('explicit authenticated Oracle UI facts survive mapper and reducer without invented progress',()=>{
  const mapped=mapNativeWorkerEvent(oracle());
  assert.equal(mapped.kind,EVENT.WORK_STARTED);
  assert.equal(mapped.role,'researcher');
  assert.equal(mapped.displayName,'Oracle · Documents');
  assert.equal(mapped.activity,ACTIVITY.DOCUMENT_READING);
  assert.deepEqual(mapped.progress,{mode:PROGRESS.UNKNOWN});

  let state=reduceScene(createInitialState({mode:'LIVE'}),{id:'connected',seq:1,stream:'transport',at:'2026-10-20T02:10:00Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,mapped);
  const agent=state.agents['oracle-research.fundamental_events'];
  assert.equal(agent.role,'researcher');
  assert.equal(agent.label,'Oracle · Documents');
  assert.equal(agent.animationRunning,true);
  assert.deepEqual(agent.progress,{mode:PROGRESS.UNKNOWN});
});

test('heartbeat remains presence-only even when payload tries to supply UI work metadata',()=>{
  const heartbeat=mapNativeWorkerEvent(oracle({
    event_id:'oracle-hb',event_type:'WORKER_HEARTBEAT',event_seq:2,
    payload:{ui_activity:ACTIVITY.HYPOTHESIS_GENERATION,ui_role:'researcher',ui_label:'Oracle · Discovery'},
  }));
  assert.equal(heartbeat.kind,EVENT.HEARTBEAT);
  assert.equal(heartbeat.workerId,undefined);
  let state=reduceScene(createInitialState({mode:'LIVE'}),{id:'connected',seq:1,stream:'transport',at:'2026-10-20T02:10:00Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,heartbeat);
  assert.deepEqual(state.agents,{});
});

test('non-allowlisted identity cannot become Owner or another invented role',()=>{
  const mapped=mapNativeWorkerEvent(oracle({payload:{ui_role:'owner',ui_label:'Owner',ui_activity:ACTIVITY.HYPOTHESIS_GENERATION}}));
  assert.equal(mapped.role,'worker');
  assert.equal(mapped.displayName,'Owner');
  assert.notEqual(mapped.role,'owner');
});

test('snapshot may reconstruct explicit Oracle identity but cannot replay business motion',()=>{
  const snapshot=mapNativeSnapshot({generated_at:'2026-10-20T02:11:00Z',cursor:'oracle-live-event-1',events:[oracle()]});
  let state=reduceScene(createInitialState({mode:'LIVE'}),{id:'connected',seq:1,stream:'transport',at:'2026-10-20T02:10:00Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,snapshot);
  const agent=state.agents['oracle-research.fundamental_events'];
  assert.equal(agent.role,'researcher');
  assert.equal(agent.label,'Oracle · Documents');
  assert.equal(agent.animationRunning,false);
  assert.equal(state.transport.resumeRequiresBusinessEvent,true);
});

test('hypothesis-generation has a visible non-economic physical gesture family',()=>{
  let state=reduceScene(createInitialState({mode:'LIVE'}),{id:'connected',seq:1,stream:'transport',at:'2026-10-20T02:10:00Z',kind:EVENT.CONNECTED});
  assert.equal(gestureFamily({animate:true,activity:ACTIVITY.HYPOTHESIS_GENERATION},state),'comparison');
  assert.notEqual(gestureFamily({animate:true,activity:ACTIVITY.HYPOTHESIS_GENERATION},state),'economic');
});
