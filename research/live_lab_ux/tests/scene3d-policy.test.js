import test from 'node:test';
import assert from 'node:assert/strict';
import {ACTIVITY,PROGRESS} from '../core/model.js';
import {ARCHITECTURE_NODES,deriveAgentVisual,deriveSceneVisual,escapeSceneText,positionForAgent,sceneBusinessMotionAllowed} from '../ui/scene3d-policy.js';

const agent=(overrides={})=>({id:'worker-a',role:'worker',label:'Worker',state:'WORKING',activity:ACTIVITY.CODING_TESTING,animationRevision:2,animationRunning:true,progress:{mode:PROGRESS.UNKNOWN},stale:false,currentTask:'Task',currentStep:'Step',destination:null,...overrides});

test('stale state freezes visual business animation',()=>{assert.equal(deriveAgentVisual(agent({stale:true})).animate,false);assert.equal(deriveAgentVisual(agent()).animate,true);});
test('scene never invents economic activity',()=>{const base={agents:{a:agent()},transport:{connected:true,stale:false},economicLook:{activeWorkerId:null},invariants:{REAL_CAPITAL_AUTHORIZED:false,LIVE_TRADING_AUTHORIZED:false,paid_usd_total:0}};assert.equal(deriveSceneVisual(base).economicActive,false);assert.equal(deriveSceneVisual({...base,economicLook:{activeWorkerId:'a'}}).economicActive,true);});
test('unknown role placement is stable without becoming a known role',()=>{const a={id:'future-role-17',role:'future'};assert.deepEqual(positionForAgent(a),positionForAgent(a));assert.equal(deriveAgentVisual({...agent(),...a}).role,'future');});
test('architecture nodes are structural labels only',()=>{assert.ok(ARCHITECTURE_NODES.length>=8);assert.ok(ARCHITECTURE_NODES.every(node=>Array.isArray(node.position)&&node.position.length===3));});
test('business motion follows transport truth',()=>{assert.equal(sceneBusinessMotionAllowed({transport:{connected:true,stale:false}}),true);assert.equal(sceneBusinessMotionAllowed({transport:{connected:true,stale:true}}),false);assert.equal(sceneBusinessMotionAllowed({transport:{connected:false,stale:false}}),false);});
test('unknown and completed-count progress never become fabricated ratios',()=>{assert.equal(deriveAgentVisual(agent({progress:{mode:PROGRESS.UNKNOWN}})).progress,null);assert.equal(deriveAgentVisual(agent({progress:{mode:PROGRESS.COMPLETED_COUNT_ONLY,completed:8}})).progress,null);assert.equal(deriveAgentVisual(agent({progress:{mode:PROGRESS.KNOWN_TOTAL,completed:2,total:4}})).progress,0.5);});
test('event-derived display text is escaped before entering 3D overlay markup',()=>{assert.equal(escapeSceneText('<img src=x onerror="boom">'), '&lt;img src=x onerror=&quot;boom&quot;&gt;');assert.equal(deriveAgentVisual(agent({currentTask:'<script>alert(1)</script>'})).task,'&lt;script&gt;alert(1)&lt;/script&gt;');});
