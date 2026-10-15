import {LiveEventAdapter} from './adapters/live-event.js';
import {mapNativeSiteFrame} from './adapters/platform-native.js';
import {subscribeNativeSiteEvents} from './adapters/platform-native-sse.js';
import {createInitialState,reduceScene} from './core/state-machine.js';
import {createMobileCamera} from './ui/camera.js';
import {renderScene} from './ui/render.js';
import {createResearchLab3D} from './ui/scene3d.js';

const refs={worldAgents:document.querySelector('[data-world-agents]'),economicStatus:document.querySelector('[data-economic-status]'),connectivity:document.querySelector('[data-connectivity]'),warning:document.querySelector('[data-warning]'),resumeGuard:document.querySelector('[data-resume-guard]'),clock:document.querySelector('[data-clock]'),roleCount:document.querySelector('[data-role-count]'),resultWall:document.querySelector('[data-result-wall]'),detailSheet:document.querySelector('[data-detail-sheet]')};
let state=createInitialState({mode:'LIVE'}),selectedWorkerId=null,scene3d=null;
function render(){renderScene(state,refs,{selectedWorkerId,onSelectAgent(id){selectedWorkerId=id;render();}});scene3d?.update(state,{selectedWorkerId});}

const viewport=document.querySelector('[data-camera]');
scene3d=createResearchLab3D({viewport,canvas:document.querySelector('[data-scene3d-canvas]'),labelLayer:document.querySelector('[data-scene3d-labels]'),onSelectAgent(id){selectedWorkerId=id;render();}});
const fallbackCamera=scene3d.ready?null:createMobileCamera(viewport,document.querySelector('[data-world]'));
const camera=scene3d.ready?scene3d:fallbackCamera;

const adapter=new LiveEventAdapter({subscribeLive:(emit)=>subscribeNativeSiteEvents(emit),mapCanonicalEvent:mapNativeSiteFrame});
adapter.start((event)=>{state=reduceScene(state,event);render();});
document.querySelector('[data-detail-close]').addEventListener('click',()=>{selectedWorkerId=null;render();});
document.querySelector('[data-zoom-in]').addEventListener('click',()=>camera?.zoom(.12));
document.querySelector('[data-zoom-out]').addEventListener('click',()=>camera?.zoom(-.12));
document.querySelector('[data-camera-reset]').addEventListener('click',()=>camera?.reset());
window.addEventListener('pagehide',()=>{adapter.stop();scene3d?.destroy();fallbackCamera?.destroy();},{once:true});
render();
