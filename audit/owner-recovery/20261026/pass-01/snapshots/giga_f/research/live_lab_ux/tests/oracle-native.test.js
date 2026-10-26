import test from 'node:test';
import assert from 'node:assert/strict';

import {ACTIVITY,EVENT,PROGRESS} from '../core/model.js';
import {mapNativeSnapshot,mapNativeWorkerEvent,NATIVE_BINDING} from '../adapters/platform-native.js';
import {createInitialState,reduceScene} from '../core/state-machine.js';
import {gestureFamily} from '../ui/motion-authority.js';

const oracle=(overrides={})=>({
  event_id:'oracle-event-1',
  session_id:'oracle-session-1',
  worker_id:'oracle-research-v1',
  action_id:'FRONTIER-FUNDAMENTAL-DISTINCT-THESIS-003-g5',
  event_type:'ACTION_STARTED',
  event_seq:1,
  generation:5,
  emitted_at:'2026-10-20T02:00:00Z',
  accepted_at:'2026-10-20T02:00:01Z',
  payload:{
    label:'Generate bounded candidate hypothesis',
    detail:'Local GPT-OSS pre-outcome reasoning',
    ui_activity:ACTIVITY.HYPOTHESIS_GENERATION,
    ui_role:'researcher',
    ui_label:'Oracle',
  },
  ...overrides,
});

function connected(){
  return reduceScene(createInitialState({mode:'LIVE'}),{
    id:'connected',seq:1,stream:'transport',at:'2026-10-20T02:00:00Z',kind:EVENT.CONNECTED,
  });
}

test('explicit authenticated Oracle metadata maps without inferred economics or progress',()=>{
  const mapped=mapNativeWorkerEvent(oracle());
  assert.equal(mapped.workerId,'oracle-research-v1');
  assert.equal(mapped.role,'researcher');
  assert.equal(mapped.displayName,'Oracle');
  assert.equal(mapped.activity,ACTIVITY.HYPOTHESIS_GENERATION);
  assert.deepEqual(mapped.progress,{mode:PROGRESS.UNKNOWN});
  assert.equal(mapped.kind,EVENT.WORK_STARTED);
  assert.ok(!Object.hasOwn(mapped,'result'));
  assert.ok(!Object.hasOwn(mapped,'destination'));
});

test('Oracle identity is never inferred from worker id when explicit UI metadata is absent',()=>{
  const event=oracle({payload:{label:'work'}});
  const mapped=mapNativeWorkerEvent(event);
  assert.equal(mapped.role,'worker');
  assert.equal(mapped.displayName,undefined);
  assert.equal(mapped.activity,ACTIVITY.NONE);
});

test('invalid explicit role and oversized label fail closed to generic worker identity',()=>{
  const mapped=mapNativeWorkerEvent(oracle({payload:{ui_role:'owner',ui_label:'X'.repeat(65),ui_activity:'future-alpha'}}));
  assert.equal(mapped.role,'worker');
  assert.equal(mapped.displayName,undefined);
  assert.equal(mapped.activity,ACTIVITY.NONE);
});

test('hypothesis generation authorizes only the existing non-economic comparison gesture',()=>{
  let state=connected();
  const mapped=mapNativeWorkerEvent(oracle());
  state=reduceScene(state,mapped);
  const agent=state.agents['oracle-research-v1'];
  assert.equal(agent.label,'Oracle');
  assert.equal(agent.animationRunning,true);
  assert.equal(gestureFamily({animate:true,activity:agent.activity},state),'comparison');
  assert.equal(state.economicLook.activeWorkerId,null);
});

test('snapshot reconstructs Oracle facts but never replays hypothesis-generation motion',()=>{
  const event=oracle();
  const snapshot=mapNativeSnapshot({
    generated_at:'2026-10-20T02:01:00Z',
    cursor:event.event_id,
    events:[event],
    sessions:[{worker_id:event.worker_id,session_id:event.session_id,generation:event.generation,lease_status:'ACTIVE'}],
  });
  let state=connected();
  state=reduceScene(state,snapshot);
  const agent=state.agents[event.worker_id];
  assert.equal(agent.label,'Oracle');
  assert.equal(agent.role,'researcher');
  assert.equal(agent.state,'WORKING');
  assert.equal(agent.activity,ACTIVITY.HYPOTHESIS_GENERATION);
  assert.equal(agent.animationRunning,false);
  assert.equal(state.transport.resumeRequiresBusinessEvent,true);
});

test('heartbeat after snapshot is presence only and cannot resume Oracle animation',()=>{
  const event=oracle();
  let state=connected();
  state=reduceScene(state,mapNativeSnapshot({generated_at:'2026-10-20T02:01:00Z',cursor:event.event_id,events:[event]}));
  const heartbeat=mapNativeWorkerEvent(oracle({event_id:'oracle-hb',event_type:'WORKER_HEARTBEAT',event_seq:2,accepted_at:'2026-10-20T02:01:02Z'}));
  state=reduceScene(state,heartbeat);
  assert.equal(state.agents[event.worker_id].animationRunning,false);
  assert.equal(state.transport.lastHeartbeatAt,'2026-10-20T02:01:02Z');
});

test('a genuinely later semantic Oracle start may resume animation after reconstruction',()=>{
  const event=oracle();
  let state=connected();
  state=reduceScene(state,mapNativeSnapshot({generated_at:'2026-10-20T02:01:00Z',cursor:event.event_id,events:[event]}));
  state=reduceScene(state,mapNativeWorkerEvent(oracle({event_id:'oracle-event-2',event_seq:2,accepted_at:'2026-10-20T02:01:03Z'})));
  assert.equal(state.agents[event.worker_id].animationRunning,true);
  assert.equal(state.transport.resumeRequiresBusinessEvent,false);
});

test('native binding declares explicit Oracle-capable fields and forbids identity inference',()=>{
  for(const key of ['ui_activity','ui_role','ui_label'])assert.ok(NATIVE_BINDING.explicitPayloadFacts.includes(key));
  for(const key of ['role-from-worker-id','identity-from-worker-id','economic-result'])assert.ok(NATIVE_BINDING.forbiddenInferences.includes(key));
});
