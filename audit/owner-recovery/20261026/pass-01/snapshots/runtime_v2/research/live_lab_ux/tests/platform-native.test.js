import test from 'node:test';
import assert from 'node:assert/strict';
import {ACTIVITY,EVENT,PROGRESS,SYSTEM_STATE} from '../core/model.js';
import {createInitialState,reduceScene} from '../core/state-machine.js';
import {NATIVE_BINDING,mapNativeSiteFrame,mapNativeSnapshot,mapNativeWorkerEvent} from '../adapters/platform-native.js';
import {subscribeNativeSiteEvents} from '../adapters/platform-native-sse.js';

const native=(overrides={})=>({
  event_id:'platform-probe-event-0422a0b3',
  session_id:'platform-probe-session-0422a0b3',
  worker_id:'platform-probe-worker-0422a0b3',
  action_id:'native-action-stream-0422a0b3',
  event_type:'ACTION_STARTED',
  event_seq:1,
  generation:2,
  emitted_at:'2026-10-14T10:00:00Z',
  accepted_at:'2026-10-14T10:00:01Z',
  payload:{label:'native action stream mapping probe',probe_id:'native-action-stream-0422a0b3',detail:'authenticated worker event accepted and published'},
  ...overrides,
});

test('real probe-shaped ACTION_STARTED maps without invented identity/progress/economics',()=>{
  const mapped=mapNativeWorkerEvent(native());
  assert.equal(mapped.kind,EVENT.WORK_STARTED);
  assert.equal(mapped.workerId,'platform-probe-worker-0422a0b3');
  assert.equal(mapped.role,'worker');
  assert.equal(mapped.stream,'native:platform-probe-worker-0422a0b3:platform-probe-session-0422a0b3:g2');
  assert.equal(mapped.task,'native action stream mapping probe');
  assert.equal(mapped.step,'authenticated worker event accepted and published');
  assert.deepEqual(mapped.progress,{mode:PROGRESS.UNKNOWN});
  assert.equal(mapped.activity,ACTIVITY.NONE);
  assert.equal(mapped.system.state,SYSTEM_STATE.WORKING);
  assert.ok(!JSON.stringify(mapped).toLowerCase().includes('owner'));
  assert.ok(!JSON.stringify(mapped).toLowerCase().includes('codex'));
});

test('explicit supported UI activity is preserved, never guessed',()=>{
  assert.equal(mapNativeWorkerEvent(native()).activity,ACTIVITY.NONE);
  const mapped=mapNativeWorkerEvent(native({payload:{label:'coding',ui_activity:ACTIVITY.CODING_TESTING}}));
  assert.equal(mapped.activity,ACTIVITY.CODING_TESTING);
});

test('heartbeat is presence-only and cannot materialize or animate a worker',()=>{
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  const heartbeat=mapNativeWorkerEvent(native({event_id:'hb',event_type:'WORKER_HEARTBEAT',event_seq:2}));
  state=reduceScene(state,heartbeat);
  assert.deepEqual(state.agents,{});
  assert.equal(state.transport.lastHeartbeatAt,'2026-10-14T10:00:01Z');
});

test('generation-scoped stream permits seq 1 after a prior generation high sequence',()=>{
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,mapNativeWorkerEvent(native({event_id:'g1',generation:1,event_seq:99})));
  state=reduceScene(state,mapNativeWorkerEvent(native({event_id:'g2',generation:2,event_seq:1})));
  assert.equal(state.ignoredEvents,0);
  assert.equal(state.history.length,3);
});

test('duplicate native event never replays state-machine animation',()=>{
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  const event=mapNativeWorkerEvent(native({payload:{label:'coding',ui_activity:ACTIVITY.CODING_TESTING}}));
  state=reduceScene(state,event);
  const revision=state.agents[event.workerId].animationRevision;
  state=reduceScene(state,event);
  assert.equal(state.agents[event.workerId].animationRevision,revision);
  assert.equal(state.ignoredEvents,1);
});

test('unsupported native type is rejected rather than visually invented',()=>{
  assert.equal(mapNativeWorkerEvent(native({event_type:'PROMOTE'})),null);
  assert.equal(mapNativeWorkerEvent(native({event_type:'ECONOMIC_LOOK_STARTED'})),null);
});

test('completed worker with explicit queued result leaves worker idle but system queued',()=>{
  const completed=mapNativeWorkerEvent(native({event_id:'done-queued',event_type:'ACTION_COMPLETED',event_seq:2,payload:{task_id:'FRONTIER-EVENT-001',result:'FROZEN_HYPOTHESIS_QUEUED_FOR_VALIDATION',candidate_id:'EVENT-X'}}));
  assert.equal(completed.kind,EVENT.IDLE);
  assert.equal(completed.system.state,SYSTEM_STATE.QUEUED);
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,completed);
  assert.equal(state.agents[completed.workerId].state,'IDLE');
  assert.equal(state.system.state,SYSTEM_STATE.QUEUED);
});

test('plain ACTION_COMPLETED never proves global idle',()=>{
  const completed=mapNativeWorkerEvent(native({event_id:'done-unknown',event_type:'ACTION_COMPLETED',event_seq:2,payload:{task_id:'T-1',result:'COMPLETE'}}));
  assert.equal(completed.system.state,SYSTEM_STATE.UNKNOWN);
});

test('snapshot queue summary is the only path that can prove global IDLE',()=>{
  const queued=mapNativeSnapshot({generated_at:'2026-10-14T10:01:00Z',events:[],queue_summary:{ready_count:1,claimed_count:0,next_task_id:'VALIDATE-X',next_lane:'independent_challenge'}});
  assert.equal(queued.system.state,SYSTEM_STATE.QUEUED);
  assert.equal(queued.system.readyCount,1);
  assert.equal(queued.system.nextTaskId,'VALIDATE-X');
  const idle=mapNativeSnapshot({generated_at:'2026-10-14T10:02:00Z',events:[],queue_summary:{ready_count:0,claimed_count:0}});
  assert.equal(idle.system.state,SYSTEM_STATE.IDLE);
});

test('snapshot reconstruction is factual and non-animating until a later business event',()=>{
  const snapshot=mapNativeSnapshot({generated_at:'2026-10-14T10:01:00Z',cursor:'platform-probe-event-0422a0b3',events:[native()]});
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,snapshot);
  const worker=state.agents['platform-probe-worker-0422a0b3'];
  assert.equal(worker.state,'WORKING');
  assert.equal(worker.animationRunning,false);
  assert.deepEqual(worker.progress,{mode:PROGRESS.UNKNOWN});
  assert.equal(state.system.state,SYSTEM_STATE.WORKING);
  assert.equal(state.transport.resumeRequiresBusinessEvent,true);
});

test('snapshot replay frames are ignored; only a truly later accepted event can animate',()=>{
  const historical=native({payload:{label:'coding',ui_activity:ACTIVITY.CODING_TESTING}});
  const snapshot=mapNativeSnapshot({generated_at:'2026-10-14T10:01:00Z',cursor:historical.event_id,events:[historical]});
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,snapshot);
  const workerId=historical.worker_id;
  assert.equal(state.agents[workerId].animationRunning,false);
  const historyAfterSnapshot=state.history.length;
  state=reduceScene(state,mapNativeWorkerEvent(historical));
  assert.equal(state.history.length,historyAfterSnapshot);
  assert.equal(state.agents[workerId].animationRunning,false);
  const later=native({event_id:'platform-probe-event-next',event_seq:2,accepted_at:'2026-10-14T10:01:02Z',payload:{label:'coding next',ui_activity:ACTIVITY.CODING_TESTING}});
  state=reduceScene(state,mapNativeWorkerEvent(later));
  assert.equal(state.agents[workerId].animationRunning,true);
  assert.equal(state.transport.resumeRequiresBusinessEvent,false);
});

test('native Site named frames route through one canonical mapper',()=>{
  assert.equal(mapNativeSiteFrame({channel:'worker_event',data:native()}).kind,EVENT.WORK_STARTED);
  assert.equal(mapNativeSiteFrame({channel:'snapshot',data:{generated_at:'2026-10-14T10:01:00Z',events:[]}}).kind,EVENT.SNAPSHOT);
  assert.equal(mapNativeSiteFrame({channel:'unknown',data:{}}),null);
});

test('binding contract documents the forbidden inferences',()=>{
  for(const key of ['codex-owner-identity','progress','decision','economic-look','economic-result','global-idle-from-worker-completion'])assert.ok(NATIVE_BINDING.forbiddenInferences.includes(key));
  assert.equal(NATIVE_BINDING.idleRequiresGlobalQueueProof,true);
});

test('SSE subscription forwards only real open/named-frame/error observations and closes cleanly',()=>{
  class FakeEventSource{
    constructor(url){this.url=url;this.handlers={};this.closed=false;FakeEventSource.instance=this;}
    addEventListener(name,fn){(this.handlers[name]??=[]).push(fn);}
    removeEventListener(){}
    emit(name,value={}){for(const fn of this.handlers[name]??[])fn(value);}
    close(){this.closed=true;}
  }
  const frames=[];
  const stop=subscribeNativeSiteEvents(frame=>frames.push(frame),{EventSourceImpl:FakeEventSource,now:()=> '2026-10-15T00:00:00Z'});
  FakeEventSource.instance.emit('open');
  FakeEventSource.instance.emit('worker_event',{data:JSON.stringify(native())});
  FakeEventSource.instance.emit('error');
  assert.equal(FakeEventSource.instance.url,'/api/work/events');
  assert.equal(frames[0].channel,'connected');
  assert.equal(frames[1].channel,'worker_event');
  assert.equal(frames[2].channel,'disconnected');
  stop();
  assert.equal(FakeEventSource.instance.closed,true);
});
