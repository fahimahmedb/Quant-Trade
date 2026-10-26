import {LiveEventAdapter} from './adapters/live-event.js';
import {mapNativeSiteFrame} from './adapters/platform-native.js';
import {subscribeNativeSiteEvents} from './adapters/platform-native-sse.js';
import {createInitialState,reduceScene} from './core/state-machine.js';
import {createMobileCamera} from './ui/camera.js';
import {renderScene} from './ui/render.js';

const refs={
  worldAgents:document.querySelector('[data-world-agents]'),
  economicStatus:document.querySelector('[data-economic-status]'),
  connectivity:document.querySelector('[data-connectivity]'),
  warning:document.querySelector('[data-warning]'),
  resumeGuard:document.querySelector('[data-resume-guard]'),
  clock:document.querySelector('[data-clock]'),
  roleCount:document.querySelector('[data-role-count]'),
  resultWall:document.querySelector('[data-result-wall]'),
  detailSheet:document.querySelector('[data-detail-sheet]'),
};

let state=createInitialState({mode:'LIVE'}),selectedWorkerId=null;
function render(){renderScene(state,refs,{selectedWorkerId,onSelectAgent(id){selectedWorkerId=id;render();}});}

const adapter=new LiveEventAdapter({
  subscribeLive:(emit)=>subscribeNativeSiteEvents(emit),
  mapCanonicalEvent:mapNativeSiteFrame,
});
adapter.start((event)=>{state=reduceScene(state,event);render();});

document.querySelector('[data-detail-close]').addEventListener('click',()=>{selectedWorkerId=null;render();});
const camera=createMobileCamera(document.querySelector('[data-camera]'),document.querySelector('[data-world]'));
document.querySelector('[data-zoom-in]').addEventListener('click',()=>camera.zoom(.12));
document.querySelector('[data-zoom-out]').addEventListener('click',()=>camera.zoom(-.12));
document.querySelector('[data-camera-reset]').addEventListener('click',()=>camera.reset());
window.addEventListener('pagehide',()=>adapter.stop(),{once:true});
render();
