import * as T from './vendor/three.js';
import {buildArchitecture,buildHumanoid} from './architecture.js';
import {deriveSceneVisual,sceneBusinessMotionAllowed} from './scene3d-policy.js';
import {ACTIVITY} from '../core/model.js';

const clamp=T.MathUtils.clamp;
export function createResearchLab3D({viewport,canvas,labelLayer,onSelectAgent=()=>{},onFocusComplete=()=>{}}){
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const mobile=()=>viewport.clientWidth<700;
 const scene=new T.Scene();scene.background=new T.Color('#0f1d2c');scene.fog=new T.FogExp2('#182a3b',.009);
 const camera=new T.PerspectiveCamera(40,1,.1,180);
 const view={yaw:.44,pitch:.48,distance:mobile()?48:48,target:new T.Vector3(0,1.6,0)};
 const goal={...view,target:view.target.clone()};
 let renderer,ready=false,destroyed=false,frame=0,last=0,state=null,visual={agents:[]},selected=null,focusPending=null,focusStarted=0,economicLevel=0;
 const actors=new Map(),targets=new Map(),pointers=new Map();let dragged=false,pinch=null;
 let fallback=false,illustration;
 try{renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,mobile()?1.65:1.75));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;ready=true;}catch{fallback=true;}
 const world=buildArchitecture(scene);
 if(fallback){illustration=document.createElement('img');illustration.src=new URL('../assets/laboratory-idle.webp',import.meta.url).href;illustration.alt='Illustrated night-blue research laboratory with amber containment column, curved terrace and specialized research stations';illustration.className='lab-illustration';viewport.prepend(illustration);viewport.classList.add('has-illustration');}
 viewport.classList.add('has-webgl');
 const v=new T.Vector3();
 function resize(){const w=viewport.clientWidth,h=viewport.clientHeight;camera.aspect=w/h;camera.fov=mobile()?48:40;camera.updateProjectionMatrix();renderer?.setSize(w,h,false);}
 const observer=new ResizeObserver(resize);observer.observe(viewport);resize();
 function point(position){v.set(...position).project(camera);return{x:(v.x+1)*viewport.clientWidth/2,y:(1-v.y)*viewport.clientHeight/2,visible:v.z<1&&v.z>0};}
 function applyCamera(){const c=Math.cos(view.pitch);camera.position.set(view.target.x+Math.sin(view.yaw)*c*view.distance,view.target.y+Math.sin(view.pitch)*view.distance,view.target.z+Math.cos(view.yaw)*c*view.distance);camera.lookAt(view.target);camera.updateMatrixWorld();}
 applyCamera();
 function focus(id){const a=visual.agents.find(a=>a.id===id);if(!a)return;goal.target.set(a.position[0],a.position[1]+1.1,a.position[2]);goal.distance=mobile()?8.6:7.2;goal.pitch=.25;goal.yaw=a.angle+.48;focusPending=id;focusStarted=performance.now();if(reduced){view.target.copy(goal.target);Object.assign(view,{distance:goal.distance,pitch:goal.pitch,yaw:goal.yaw});}}
 function reset(){goal.target.set(0,1.6,0);goal.yaw=.44;goal.pitch=.48;goal.distance=48;focusPending=null;}
 function zoom(delta){goal.distance=clamp(goal.distance-delta*18,5.5,63);}
 function syncActors(){const ids=new Set(visual.agents.map(a=>a.id));for(const[id,actor]of actors)if(!ids.has(id)){scene.remove(actor.group);targets.get(id)?.remove();targets.delete(id);actors.delete(id);}
 const used=new Map();for(const a of visual.agents){let actor=actors.get(a.id);if(!actor){actor=buildHumanoid(scene,actors.size);actors.set(a.id,actor);const b=document.createElement('button');b.type='button';b.className='agent-target';b.setAttribute('aria-label',`Focus ${a.id}`);const dot=document.createElement('i');b.append(dot);b.addEventListener('click',e=>{e.stopPropagation();onSelectAgent(a.id);});labelLayer.append(b);targets.set(a.id,b);}
 const slot=used.get(a.role)||0;used.set(a.role,slot+1);actor.group.position.set(a.position[0]+Math.cos(a.angle)*slot*.85,a.position[1],a.position[2]-Math.sin(a.angle)*slot*.85);actor.group.rotation.y=a.angle+Math.PI;actor.visual=a;
 const b=targets.get(a.id);b.classList.toggle('is-active',a.animate);b.classList.toggle('is-selected',a.selected);b.classList.toggle('is-stale',a.state==='STALE');b.title=`${a.id} · ${a.state}`;
 }}
 function pose(actor,dt){const a=actor.visual,allowed=a.animate&&sceneBusinessMotionAllowed(state); // reducer state.animationRunning is the only business gesture authority.
 if(allowed&&!reduced)actor.phase+=dt;
 const t=actor.phase;
 const reading=[ACTIVITY.DOCUMENT_READING,ACTIVITY.SOURCE_RESEARCH].includes(a.activity),typing=a.activity===ACTIVITY.CODING_TESTING,comparison=[ACTIVITY.AUDIT,ACTIVITY.DATA_QUALIFICATION].includes(a.activity),economic=a.activity===ACTIVITY.CALCULATION;
 if(!allowed)return; // freeze exactly at last pose on disconnect; no idle work.
 actor.document.visible=reading;
 actor.arms.forEach((arm,i)=>{const phase=t*(typing?8:1.6)+i*1.7;
 arm.shoulder.rotation.x=reading?-1.05:typing?-.58:comparison?-.7+Math.sin(phase)*.22:economic?-.72:-.3;
 arm.shoulder.rotation.z=(i?-.1:.1)+(comparison?Math.sin(phase*.7)*.16:0);
 arm.forearm.rotation.x=reading?-.7:typing?-.9+Math.sin(phase)*.11:comparison?-.5+Math.sin(phase)*.26:-.3;
 });
 }
 function animate(now){if(destroyed)return;frame=requestAnimationFrame(animate);if(document.hidden){last=now;return;}const dt=Math.min((now-(last||now))/1000,.06);last=now;
 const k=reduced?1:1-Math.exp(-dt*5.5);view.target.lerp(goal.target,k);for(const key of ['yaw','pitch','distance'])view[key]+= (goal[key]-view[key])*k;
 applyCamera();
 // Core activation requires both the explicit Economic Look slot and a currently
 // authorized factual worker. Historical snapshots, stale and reconnect stay dim.
 const economicAgent=visual.agents.find(a=>a.id===visual.economicWorkerId);
 const coreAllowed=visual.economicActive&&economicAgent?.animate&&sceneBusinessMotionAllowed(state);
 economicLevel+=(Number(coreAllowed)-economicLevel)*(reduced?1:1-Math.exp(-dt*3));
 world.energyMaterial.emissiveIntensity=.13+economicLevel*3.3;world.coreLight.intensity=economicLevel*38;
 if(coreAllowed&&!reduced){world.cartridge.rotation.y+=dt*.33;world.activeRing.rotation.z+=dt*.22;}
 for(const[id,actor]of actors){pose(actor,dt);const pos=actor.group.position;const p=point([pos.x,pos.y+1.9,pos.z]);const b=targets.get(id);b.style.transform=`translate(${p.x}px,${p.y}px) translate(-50%,-50%)`;b.hidden=!p.visible;}
 if(focusPending&&now-focusStarted>(reduced?0:1000)){const id=focusPending;focusPending=null;onFocusComplete(id);}
 if(renderer)renderer.render(scene,camera);
 }
 const down=e=>{if(e.target.closest('button'))return;viewport.setPointerCapture?.(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,sx:e.clientX,sy:e.clientY});dragged=false;if(pointers.size===2){const[a,b]=[...pointers.values()];pinch={d:Math.hypot(a.x-b.x,a.y-b.y),camera:goal.distance};}};
 const move=e=>{const p=pointers.get(e.pointerId);if(!p)return;const dx=e.clientX-p.x,dy=e.clientY-p.y;p.x=e.clientX;p.y=e.clientY;dragged ||= Math.hypot(p.x-p.sx,p.y-p.sy)>7;if(!dragged)return;focusPending=null;
 if(pointers.size===2){const[a,b]=[...pointers.values()];if(pinch)goal.distance=clamp(pinch.camera*pinch.d/Math.max(1,Math.hypot(a.x-b.x,a.y-b.y)),5.5,63);}
 else if(e.shiftKey||e.buttons===2){goal.target.x=clamp(goal.target.x-dx*.025,-10,10);goal.target.z=clamp(goal.target.z-dy*.025,-10,10);}
 else{goal.yaw-=dx*.005;goal.pitch=clamp(goal.pitch+dy*.004,.14,.83);}};
 const up=e=>{pointers.delete(e.pointerId);pinch=null;};
 const wheel=e=>{e.preventDefault();goal.distance=clamp(goal.distance*Math.exp(e.deltaY*.001),5.5,63);};
 const context=e=>e.preventDefault();
 viewport.addEventListener('pointerdown',down);viewport.addEventListener('pointermove',move);viewport.addEventListener('pointerup',up);viewport.addEventListener('pointercancel',up);viewport.addEventListener('wheel',wheel,{passive:false});viewport.addEventListener('contextmenu',context);
 canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();viewport.dataset.contextLost='true';if(!illustration){illustration=document.createElement('img');illustration.src=new URL('../assets/laboratory-idle.webp',import.meta.url).href;illustration.className='lab-illustration';viewport.prepend(illustration);}viewport.classList.add('has-illustration');});
 frame=requestAnimationFrame(animate);
 return{ready:true,renderer:ready?'WebGL':'illustrated',
 update(next,{selectedWorkerId=null}={}){state=next;visual=deriveSceneVisual(state,{selectedWorkerId});syncActors();if(selectedWorkerId!==selected){selected=selectedWorkerId;if(selected)focus(selected);else reset();}},
 focus,reset,zoom,
 destroy(){destroyed=true;cancelAnimationFrame(frame);observer.disconnect();for(const[name,fn]of[['pointerdown',down],['pointermove',move],['pointerup',up],['pointercancel',up],['wheel',wheel],['contextmenu',context]])viewport.removeEventListener(name,fn);for(const b of targets.values())b.remove();scene.traverse(o=>{o.geometry?.dispose();if(o.material)for(const m of [].concat(o.material)){m.map?.dispose();m.dispose();}});renderer?.dispose();illustration?.remove();},
 };
}
export const SCENE3D_CAPABILITIES=Object.freeze({renderer:'Three.js / WebGL2',businessAnimationAuthority:'state.animationRunning',webglFallback:'same-world architectural illustration',mobileSafari:true});
