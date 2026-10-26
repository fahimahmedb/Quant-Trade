import {FixtureReplayAdapter} from './adapters/fixture-replay.js';
import {createInitialState,reduceScene} from './core/state-machine.js';
import {EVENT,ACTIVITY} from './core/model.js';
import {scenarioNames,scenarios,UX_TOUR} from './fixtures/scenarios.js';
import {renderScene} from './ui/render.js';
import {createResearchLab3D} from './ui/scene3d.js';
import {createInterface} from './ui/interface.js';
// This entry is an isolated, visibly marked SYNTHETIC REVIEW. It never opens SSE,
// sends ingress, writes a store, or imports into the production event authority.
const idle=[{kind:EVENT.CONNECTED}];
const active=[...idle,{kind:EVENT.WORK_STARTED,workerId:'review-worker',role:'worker',activity:ACTIVITY.DOCUMENT_READING,task:'Review source methodology · synthetic fixture',step:'Reading a primary document'}];
const economic=[...active,{kind:EVENT.ECONOMIC_LOOK_STARTED,workerId:'review-worker',role:'worker',task:'Economic Look · synthetic fixture',step:'Explicit review event, no economic evidence'}];
const make=(name,rows)=>rows.map((e,i)=>({...e,id:`review:${name}:${i}`,seq:i+1,stream:`review:${name}`,at:`2026-10-15T21:34:0${i}Z`}));
const review={idle:make('idle',idle),active:make('active',active),selected:make('selected',active),economic:make('economic',economic)};
const options=[...Object.entries(review).map(([key,events])=>({key,label:{idle:'A · Connected / idle',active:'B · One active worker',selected:'C · Worker / camera focus',economic:'D · Economic Look'}[key],events})),...scenarioNames.map(key=>({key,label:key,events:scenarios[key]})),{key:'tour',label:'All original truth scenarios',events:UX_TOUR}];
const q=s=>document.querySelector(s);for(const o of options){const n=document.createElement('option');n.value=o.key;n.textContent=o.label;q('[data-scenario]').append(n);}
let state=createInitialState({mode:'REPLAY'}),scene3d,adapter,unsubscribe;
const ui=createInterface({getState:()=>state,camera:()=>scene3d,onSelection:()=>render()});
function render(){renderScene(state,ui.refs);scene3d?.update(state,{selectedWorkerId:ui.selected});ui.render();q('[data-remaining]').textContent=`${adapter?.remaining||0} events remaining`;}
scene3d=createResearchLab3D({viewport:q('[data-camera]'),canvas:q('[data-scene3d-canvas]'),labelLayer:q('[data-scene3d-labels]'),onSelectAgent:id=>ui.select(id),onFocusComplete:id=>ui.focused(id)});
function bind(key){unsubscribe?.();state=createInitialState({mode:'REPLAY'});adapter=new FixtureReplayAdapter(options.find(o=>o.key===key).events);unsubscribe=adapter.subscribe(event=>{state=reduceScene(state,event);render();});ui.select(null);if(review[key])adapter.playAll();else adapter.next();if(key==='selected')ui.select('review-worker');render();}
q('[data-scenario]').addEventListener('change',e=>bind(e.target.value));q('[data-next-event]').addEventListener('click',()=>adapter.next());q('[data-play-all]').addEventListener('click',()=>adapter.playAll());q('[data-reset]').addEventListener('click',()=>bind(q('[data-scenario]').value));
const key=new URLSearchParams(location.search).get('case')||'idle';q('[data-scenario]').value=options.some(o=>o.key===key)?key:'idle';bind(q('[data-scenario]').value);
window.addEventListener('pagehide',()=>{unsubscribe?.();scene3d.destroy();},{once:true});
