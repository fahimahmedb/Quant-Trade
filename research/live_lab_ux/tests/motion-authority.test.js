import test from 'node:test';
import assert from 'node:assert/strict';
import {ACTIVITY,EVENT} from '../core/model.js';
import {createInitialState,reduceScene} from '../core/state-machine.js';
import {deriveSceneVisual} from '../ui/scene3d-policy.js';
import {gestureFamily,coreMotionAllowed} from '../ui/motion-authority.js';
const e=(n,kind,rest={})=>({id:`motion:${n}`,seq:n,stream:'motion',at:'2026-10-15T21:34:00Z',kind,...rest});
const worker={workerId:'a',role:'worker'};
function activeEconomic(){return [e(1,EVENT.CONNECTED),e(2,EVENT.ECONOMIC_LOOK_STARTED,worker)].reduce(reduceScene,createInitialState());}
test('core requires explicit slot AND authorized worker AND current transport',()=>{
 const active=activeEconomic();assert.equal(coreMotionAllowed(deriveSceneVisual(active),active),true);
 for(const state of [reduceScene(active,e(3,EVENT.STALE)),reduceScene(active,e(3,EVENT.DISCONNECTED)),reduceScene(active,e(3,EVENT.CONNECTED)),reduceScene(active,e(3,EVENT.SNAPSHOT)),reduceScene(active,e(3,EVENT.ECONOMIC_LOOK_FINISHED,worker))])assert.equal(coreMotionAllowed(deriveSceneVisual(state),state),false);
 const missing={...active,agents:{}};assert.equal(coreMotionAllowed(deriveSceneVisual(missing),missing),false);
});
test('unsupported activities and progress-only presence never imply a research gesture',()=>{
 const state=activeEconomic();
 for(const activity of [ACTIVITY.NONE,ACTIVITY.COMMIT,ACTIVITY.HANDOFF,ACTIVITY.RESULT,ACTIVITY.BLOCKER])assert.equal(gestureFamily({animate:true,activity},state),null);
 assert.equal(gestureFamily({animate:true,activity:ACTIVITY.CODING_TESTING},state),'typing');
 assert.equal(gestureFamily({animate:true,activity:ACTIVITY.AUDIT},state),'comparison');
 assert.equal(gestureFamily({animate:true,activity:ACTIVITY.DOCUMENT_READING},state),'reading');
 assert.equal(gestureFamily({animate:false,activity:ACTIVITY.CALCULATION},state),null);
});
test('heartbeat and duplicated events cannot authorize core after reconnect',()=>{
 let state=activeEconomic();state=reduceScene(state,e(3,EVENT.DISCONNECTED));state=reduceScene(state,e(4,EVENT.CONNECTED));state=reduceScene(state,e(5,EVENT.HEARTBEAT));state=reduceScene(state,e(2,EVENT.ECONOMIC_LOOK_STARTED,worker));assert.equal(coreMotionAllowed(deriveSceneVisual(state),state),false);
 state=reduceScene(state,e(6,EVENT.ECONOMIC_LOOK_STARTED,worker));assert.equal(coreMotionAllowed(deriveSceneVisual(state),state),true);
});

test('empty snapshot freezes omitted workers and later work on another worker cannot revive them',()=>{
 let state=activeEconomic();state=reduceScene(state,e(3,EVENT.SNAPSHOT,{agents:[]}));assert.equal(state.agents.a.animationRunning,false);
 state=reduceScene(state,e(4,EVENT.WORK_STARTED,{workerId:'b',role:'worker',activity:ACTIVITY.CODING_TESTING}));assert.equal(state.agents.a.animationRunning,false);assert.equal(state.agents.b.animationRunning,true);assert.equal(coreMotionAllowed(deriveSceneVisual(state),state),false);
});
