import {LiveEventAdapter} from './adapters/live-event.js';
import {mapNativeSiteFrame} from './adapters/platform-native.js';
import {subscribeNativeSiteEvents} from './adapters/platform-native-sse.js';
import {createInitialState,reduceScene} from './core/state-machine.js';
import {renderScene} from './ui/render.js';
import {createResearchLab3D} from './ui/scene3d.js';
import {createInterface} from './ui/interface.js';
let state=createInitialState({mode:'LIVE'}),scene3d;
const ui=createInterface({getState:()=>state,camera:()=>scene3d,onSelection:()=>render()});
function render(){renderScene(state,ui.refs);scene3d?.update(state,{selectedWorkerId:ui.selected});ui.render();}
scene3d=createResearchLab3D({viewport:document.querySelector('[data-camera]'),canvas:document.querySelector('[data-scene3d-canvas]'),labelLayer:document.querySelector('[data-scene3d-labels]'),onSelectAgent:id=>ui.select(id),onFocusComplete:id=>ui.focused(id)});
const adapter=new LiveEventAdapter({subscribeLive:emit=>subscribeNativeSiteEvents(emit),mapCanonicalEvent:mapNativeSiteFrame});
adapter.start(event=>{state=reduceScene(state,event);render();});
window.addEventListener('pagehide',()=>{adapter.stop();scene3d.destroy();},{once:true});render();

// Safari may restore this destroyed scene from the back-forward cache. Rebind
// through a fresh snapshot, which cannot authorize replayed work.
window.addEventListener('pageshow',event=>{if(event.persisted)window.location.reload();});
