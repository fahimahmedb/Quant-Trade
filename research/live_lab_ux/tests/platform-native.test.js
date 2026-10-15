import test from 'node:test';
import assert from 'node:assert/strict';
import {ACTIVITY,EVENT,PROGRESS} from '../core/model.js';
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

test('snapshot reconstruction is factual and non-animating until a later business event',()=>{
  const snapshot=mapNativeSnapshot({generated_at:'2026-10-14T10:01:00Z',cursor:'platform-probe-event-0422a0b3',events:[native()]});
  let state=reduceScene(createInitialState(),{id:'c',seq:1,stream:'transport',at:'2026-10-14T09:59:59Z',kind:EVENT.CONNECTED});
  state=reduceScene(state,snapshot);
  const worker=state.agents['platform-probe-worker-0422a0b3'];
  assert.equal(worker.state,'WORKING');
  assert.equal(worker.animationRunning,false);
  assert.deepEqual(worker.progress,{mode:PROGRESS.UNKNOWN});
  assert.equal(state.transport.resumeRequiresBusinessEvent,true);
});

test('native Site named frames route through one canonical mapper',()=>{
  assert.equal(mapNativeSiteFrame({channel:'worker_event',data:native()}).kind,EVENT.WORK_STARTED);
  assert.equal(mapNativeSiteFrame({channel:'snapshot',data:{generated_at:'2026-10-14T10:01:00Z',events:[]}}).kind,EVENT.SNAPSHOT);
  assert.equal(mapNativeSiteFrame({channel:'unknown',data:{}}),null);
});

test('binding contract documents the forbidden inferences',()=>{
  for(const key of ['codex-owner-identity','progress','decision','economic-look','economic-result'])assert.ok(NATIVE_BINDING.forbiddenInferences.includes(key));
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
