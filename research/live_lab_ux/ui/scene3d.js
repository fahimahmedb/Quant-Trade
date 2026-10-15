import {ACTIVITY} from '../core/model.js';
import {deriveSceneVisual,ROLE_STATIONS} from './scene3d-policy.js';

const VERTEX_SHADER=`
attribute vec3 aPosition;
attribute vec3 aNormal;
uniform mat4 uModel;
uniform mat4 uViewProjection;
uniform vec3 uColor;
uniform vec3 uEmissive;
uniform vec3 uLightDirection;
varying vec3 vColor;
varying float vFog;
void main(){
  vec4 world=uModel*vec4(aPosition,1.0);
  vec3 n=normalize(mat3(uModel)*aNormal);
  float diffuse=max(dot(n,normalize(uLightDirection)),0.0);
  float light=0.30+diffuse*0.70;
  vColor=uColor*light+uEmissive;
  vec4 clip=uViewProjection*world;
  gl_Position=clip;
  vFog=clamp((clip.w-7.0)/22.0,0.0,0.72);
}`;

const FRAGMENT_SHADER=`
precision mediump float;
varying vec3 vColor;
varying float vFog;
void main(){
  vec3 fog=vec3(0.025,0.04,0.075);
  gl_FragColor=vec4(mix(vColor,fog,vFog),1.0);
}`;

const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));
const add=(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]];
const mix=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t);

function compile(gl,type,source){
  const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);
  if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS)){const message=gl.getShaderInfoLog(shader);gl.deleteShader(shader);throw new Error(`WebGL shader compile failed: ${message}`);}return shader;
}
function program(gl){
  const p=gl.createProgram(),v=compile(gl,gl.VERTEX_SHADER,VERTEX_SHADER),f=compile(gl,gl.FRAGMENT_SHADER,FRAGMENT_SHADER);
  gl.attachShader(p,v);gl.attachShader(p,f);gl.linkProgram(p);gl.deleteShader(v);gl.deleteShader(f);
  if(!gl.getProgramParameter(p,gl.LINK_STATUS)){const message=gl.getProgramInfoLog(p);gl.deleteProgram(p);throw new Error(`WebGL program link failed: ${message}`);}return p;
}

function mat4Identity(){return new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);}
function mat4Multiply(a,b){
  const out=new Float32Array(16);
  for(let c=0;c<4;c++)for(let r=0;r<4;r++)out[c*4+r]=a[0*4+r]*b[c*4+0]+a[1*4+r]*b[c*4+1]+a[2*4+r]*b[c*4+2]+a[3*4+r]*b[c*4+3];
  return out;
}
function mat4Perspective(fov,aspect,near,far){
  const f=1/Math.tan(fov/2),nf=1/(near-far),out=new Float32Array(16);
  out[0]=f/aspect;out[5]=f;out[10]=(far+near)*nf;out[11]=-1;out[14]=2*far*near*nf;return out;
}
function normalize3(v){const l=Math.hypot(v[0],v[1],v[2])||1;return[v[0]/l,v[1]/l,v[2]/l];}
function cross(a,b){return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function sub(a,b){return[a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function dot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function mat4LookAt(eye,target,up=[0,1,0]){
  const z=normalize3(sub(eye,target)),x=normalize3(cross(up,z)),y=cross(z,x),out=mat4Identity();
  out[0]=x[0];out[1]=y[0];out[2]=z[0];out[4]=x[1];out[5]=y[1];out[6]=z[1];out[8]=x[2];out[9]=y[2];out[10]=z[2];out[12]=-dot(x,eye);out[13]=-dot(y,eye);out[14]=-dot(z,eye);return out;
}
function mat4TRS(position=[0,0,0],scale=[1,1,1],rotationY=0){
  const c=Math.cos(rotationY),s=Math.sin(rotationY),out=mat4Identity();
  out[0]=c*scale[0];out[2]=-s*scale[0];out[5]=scale[1];out[8]=s*scale[2];out[10]=c*scale[2];out[12]=position[0];out[13]=position[1];out[14]=position[2];return out;
}
function transformPoint(matrix,p){
  const x=p[0],y=p[1],z=p[2],w=matrix[3]*x+matrix[7]*y+matrix[11]*z+matrix[15]||1;
  return[(matrix[0]*x+matrix[4]*y+matrix[8]*z+matrix[12])/w,(matrix[1]*x+matrix[5]*y+matrix[9]*z+matrix[13])/w,(matrix[2]*x+matrix[6]*y+matrix[10]*z+matrix[14])/w,w];
}

function boxGeometry(){
  const p=[],n=[],i=[];const faces=[
    [[0,0,1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],[[0,0,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],[1,1,-1]],
    [[1,0,0],[1,-1,1],[1,-1,-1],[1,1,-1],[1,1,1]],[[-1,0,0],[-1,-1,-1],[-1,-1,1],[-1,1,1],[-1,1,-1]],
    [[0,1,0],[-1,1,1],[1,1,1],[1,1,-1],[-1,1,-1]],[[0,-1,0],[-1,-1,-1],[1,-1,-1],[1,-1,1],[-1,-1,1]]];
  for(const face of faces){const base=p.length/3,[normal,...verts]=face;for(const v of verts){p.push(v[0]/2,v[1]/2,v[2]/2);n.push(...normal);}i.push(base,base+1,base+2,base,base+2,base+3);}return{positions:p,normals:n,indices:i};
}
function cylinderGeometry(segments=18){
  const p=[],n=[],i=[];for(let s=0;s<=segments;s++){const a=s/segments*Math.PI*2,x=Math.cos(a)/2,z=Math.sin(a)/2;p.push(x,-.5,z,x,.5,z);n.push(Math.cos(a),0,Math.sin(a),Math.cos(a),0,Math.sin(a));}
  for(let s=0;s<segments;s++){const b=s*2;i.push(b,b+1,b+2,b+1,b+3,b+2);}const bottom=p.length/3;p.push(0,-.5,0);n.push(0,-1,0);const top=p.length/3;p.push(0,.5,0);n.push(0,1,0);for(let s=0;s<segments;s++){const b=s*2,next=((s+1)%segments)*2;i.push(bottom,next,b,top,b+1,next+1);}return{positions:p,normals:n,indices:i};
}
function sphereGeometry(lat=8,lon=12){
  const p=[],n=[],i=[];for(let y=0;y<=lat;y++){const v=y/lat,phi=v*Math.PI;for(let x=0;x<=lon;x++){const u=x/lon,theta=u*Math.PI*2,s=Math.sin(phi),nx=Math.cos(theta)*s,ny=Math.cos(phi),nz=Math.sin(theta)*s;p.push(nx*.5,ny*.5,nz*.5);n.push(nx,ny,nz);}}
  for(let y=0;y<lat;y++)for(let x=0;x<lon;x++){const a=y*(lon+1)+x,b=a+lon+1;i.push(a,b,a+1,b,b+1,a+1);}return{positions:p,normals:n,indices:i};
}

class MiniGL{
  constructor(canvas){
    this.canvas=canvas;this.gl=canvas.getContext('webgl2',{antialias:true,alpha:false,powerPreference:'high-performance'})||canvas.getContext('webgl',{antialias:true,alpha:false,powerPreference:'high-performance'});if(!this.gl)throw new Error('WebGL unavailable');
    const gl=this.gl;this.program=program(gl);this.locations={position:gl.getAttribLocation(this.program,'aPosition'),normal:gl.getAttribLocation(this.program,'aNormal'),model:gl.getUniformLocation(this.program,'uModel'),viewProjection:gl.getUniformLocation(this.program,'uViewProjection'),color:gl.getUniformLocation(this.program,'uColor'),emissive:gl.getUniformLocation(this.program,'uEmissive'),light:gl.getUniformLocation(this.program,'uLightDirection')};
    this.meshes={box:this.makeMesh(boxGeometry()),cylinder:this.makeMesh(cylinderGeometry()),sphere:this.makeMesh(sphereGeometry())};
    gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);gl.clearColor(.025,.04,.075,1);
  }
  makeMesh(geo){const gl=this.gl,position=gl.createBuffer(),normal=gl.createBuffer(),index=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,position);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(geo.positions),gl.STATIC_DRAW);gl.bindBuffer(gl.ARRAY_BUFFER,normal);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(geo.normals),gl.STATIC_DRAW);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,index);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(geo.indices),gl.STATIC_DRAW);return{position,normal,index,count:geo.indices.length};}
  resize(){const ratio=Math.min(window.devicePixelRatio||1,window.innerWidth<800?1.5:2),w=Math.max(1,Math.floor(this.canvas.clientWidth*ratio)),h=Math.max(1,Math.floor(this.canvas.clientHeight*ratio));if(this.canvas.width!==w||this.canvas.height!==h){this.canvas.width=w;this.canvas.height=h;}this.gl.viewport(0,0,w,h);return{w,h,ratio};}
  begin(viewProjection){const gl=this.gl;gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);gl.uniformMatrix4fv(this.locations.viewProjection,false,viewProjection);gl.uniform3f(this.locations.light,-.45,.9,.3);}
  draw(meshName,position,scale,color,emissive=[0,0,0],rotationY=0){const gl=this.gl,mesh=this.meshes[meshName];gl.bindBuffer(gl.ARRAY_BUFFER,mesh.position);gl.enableVertexAttribArray(this.locations.position);gl.vertexAttribPointer(this.locations.position,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,mesh.normal);gl.enableVertexAttribArray(this.locations.normal);gl.vertexAttribPointer(this.locations.normal,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.index);gl.uniformMatrix4fv(this.locations.model,false,mat4TRS(position,scale,rotationY));gl.uniform3fv(this.locations.color,color);gl.uniform3fv(this.locations.emissive,emissive);gl.drawElements(gl.TRIANGLES,mesh.count,gl.UNSIGNED_SHORT,0);}
  destroy(){const gl=this.gl;for(const mesh of Object.values(this.meshes)){gl.deleteBuffer(mesh.position);gl.deleteBuffer(mesh.normal);gl.deleteBuffer(mesh.index);}gl.deleteProgram(this.program);}
}

function short(value,max=34){const s=String(value||'');return s.length>max?`${s.slice(0,max-1)}…`:s;}
function makeLabel(kind){const n=document.createElement(kind==='agent'?'button':'div');n.className=`scene3d-label scene3d-label-${kind}`;if(kind==='agent')n.type='button';return n;}

export function createResearchLab3D({viewport,canvas,labelLayer,onSelectAgent=()=>{}}){
  let mini;
  try{mini=new MiniGL(canvas);}catch(error){console.warn('[live-lab-3d] fallback to DOM renderer:',error);return{ready:false,update(){},reset(){},zoom(){},destroy(){}};}
  viewport.classList.add('has-webgl');
  const reducedMotion=window.matchMedia?.('(prefers-reduced-motion: reduce)').matches??false;
  const camera={yaw:-.72,pitch:.66,distance:19,target:[0,1.0,.7],pointers:new Map(),pinch:null,dragged:false};
  let visual={agents:[],architectureNodes:[],economicActive:false,economicWorkerId:null,connected:false,stale:false};
  let selectedWorkerId=null,destroyed=false,raf=0,visible=!document.hidden;
  const labels=new Map(),pickable=[];

  function ensureLabel(key,kind){if(labels.has(key))return labels.get(key);const n=makeLabel(kind);n.dataset.sceneKey=key;if(kind==='agent')n.addEventListener('click',(e)=>{e.stopPropagation();onSelectAgent(key.slice(6));});labelLayer.append(n);labels.set(key,n);return n;}
  function cameraEye(){const cp=Math.cos(camera.pitch),sp=Math.sin(camera.pitch),sy=Math.sin(camera.yaw),cy=Math.cos(camera.yaw);return[camera.target[0]+camera.distance*cp*sy,camera.target[1]+camera.distance*sp,camera.target[2]+camera.distance*cp*cy];}
  function viewProjection(){const {w,h}=mini.resize(),projection=mat4Perspective(Math.PI/4.1,w/Math.max(1,h),.1,80),view=mat4LookAt(cameraEye(),camera.target);return mat4Multiply(projection,view);}
  function project(vp,p){const q=transformPoint(vp,p),x=(q[0]*.5+.5)*canvas.clientWidth,y=(-q[1]*.5+.5)*canvas.clientHeight;return{x,y,visible:q[3]>0&&q[2]>-1.25&&q[2]<1.25};}
  function box(position,scale,color,emissive=[0,0,0],ry=0){mini.draw('box',position,scale,color,emissive,ry);}
  function cylinder(position,scale,color,emissive=[0,0,0],ry=0){mini.draw('cylinder',position,scale,color,emissive,ry);}
  function sphere(position,scale,color,emissive=[0,0,0]){mini.draw('sphere',position,scale,color,emissive,0);}
  function beam(a,b,color,emissive=color,width=.035){const dx=b[0]-a[0],dz=b[2]-a[2],len=Math.hypot(dx,dz),center=[(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2],angle=Math.atan2(dz,dx);box(center,[len,width,width],color,emissive,-angle);}

  function drawEnvironment(now,vp){
    const floor=visual.stale?[.055,.062,.078]:[.045,.075,.13];box([0,-.16,1.0],[18,.28,15],floor);
    for(let x=-9;x<=9;x+=1.5)box([x,.002,1],[.012,.006,15],[.08,.15,.25]);
    for(let z=-6.5;z<=8.5;z+=1.5)box([0,.003,z],[18,.006,.012],[.08,.15,.25]);
    box([0,1.25,-6.5],[18,2.5,.12],[.035,.055,.095]);box([-9,1.0,1],[.12,2,15],[.03,.05,.09]);box([9,1.0,1],[.12,2,15],[.03,.05,.09]);
    for(const node of visual.architectureNodes){const p=node.position,em=visual.connected&&!visual.stale?[.025,.065,.12]:[0,0,0];cylinder([p[0],.18,p[2]],[1.05,.35,1.05],[.08,.13,.22],em);box([p[0],.56,p[2]],[1.4,.08,.42],[.10,.18,.30],em);}
    const corePulse=visual.economicActive&&!reducedMotion?(Math.sin(now*.004)*.25+.75):visual.economicActive?1:0;
    cylinder([0,.72,.25],[2.05,1.45,2.05],[.17,.10,.31],visual.economicActive?[.24*corePulse,.12*corePulse,.48*corePulse]:[.025,.012,.05]);
    cylinder([0,1.56,.25],[1.25,.10,1.25],[.25,.18,.45],visual.economicActive?[.35,.18,.70]:[.02,.01,.04]);
    cylinder([0,.04,.25],[2.8,.05,2.8],[.10,.08,.20],visual.economicActive?[.18,.08,.40]:[.01,.01,.03]);
    const spine=[[-6.8,.035,-4.2],[0,.035,-4.8],[6.8,.035,-4.2],[7.6,.035,0],[6.5,.035,4.5],[0,.035,5],[-6.5,.035,4.5],[-7.6,.035,0],[-6.8,.035,-4.2]];
    for(let i=1;i<spine.length;i++)beam(spine[i-1],spine[i],[.08,.18,.30],[.015,.04,.08],.018);
    updateArchitectureLabels(vp);
  }

  function drawStation(agent,now,vp){
    const p=agent.position,accent=agent.accent,status=agent.statusColor,active=agent.animate&&!reducedMotion,phase=now*.001+agent.animationRevision*.73,bob=active?Math.sin(phase*4.0)*.08:0,glow=active?.12+.10*(Math.sin(phase*5)*.5+.5):0;
    box([p[0],.34,p[2]],[2.25,.18,1.65],[.075,.105,.18],mix([0,0,0],accent,.06));
    box([p[0],.75,p[2]-.38],[1.7,.72,.10],[.06,.10,.16],mix([0,0,0],accent,active?.35:.08));
    box([p[0],.39,p[2]+.2],[1.5,.12,.72],[.11,.13,.18]);
    cylinder([p[0],.18,p[2]],[2.5,.08,2.5],[.08,.12,.20],agent.selected?mix([0,0,0],accent,.55):[0,0,0]);
    box([p[0]-.45,.78+bob,p[2]+.38],[.42,.72,.30],mix(accent,[.85,.9,1],.18),mix([0,0,0],accent,glow));
    sphere([p[0]-.45,1.30+bob,p[2]+.38],[.34,.34,.34],[.73,.79,.88],active?mix([0,0,0],accent,.05):[0,0,0]);
    cylinder([p[0]+.62,.18,p[2]+.38],[.18,.35,.18],status,mix([0,0,0],status,active?.22:.06));
    drawActivity(agent,p,now,active);
    if(agent.destination){const destinationColor=agent.destination==='PROMOTE'?[.31,.91,.67]:agent.destination==='PARK'?[1,.72,.18]:[1,.35,.45];box([p[0],1.72,p[2]],[1.4,.08,.28],destinationColor,mix([0,0,0],destinationColor,.22));}
    if(visual.economicWorkerId===agent.id)beam([p[0],.9,p[2]],[0,.9,.25],[.45,.28,.85],[.28,.12,.58],.05);
    updateAgentLabel(agent,vp,[p[0],1.9,p[2]]);
  }

  function drawActivity(agent,p,now,active){
    const a=agent.activity,accent=agent.accent,phase=now*.001+agent.animationRevision*.51,pulse=active?(Math.sin(phase*6)*.5+.5):.25;
    if(a===ACTIVITY.SOURCE_RESEARCH){const angle=active?phase*2.2:0,s=[p[0]+.55+Math.cos(angle)*.26,1.22,p[2]-.33+Math.sin(angle)*.26];sphere(s,[.14,.14,.14],accent,mix([0,0,0],accent,.35));beam([p[0]+.55,1.05,p[2]-.33],s,accent,mix([0,0,0],accent,.16),.025);}
    else if(a===ACTIVITY.DOCUMENT_READING){box([p[0]+.56,1.12,p[2]-.32],[.58,.72,.07],[.12,.18,.28],mix([0,0,0],accent,.16));const y=active?1.0+((Math.sin(phase*2.4)+1)/2)*.32:1.12;box([p[0]+.56,y,p[2]-.27],[.5,.025,.02],accent,mix([0,0,0],accent,.40));}
    else if(a===ACTIVITY.DATA_QUALIFICATION){for(let i=0;i<3;i++){const lit=active?Math.max(.12,1-Math.abs(((phase*1.6+i*.55)%3)-1.5)/1.5):.18;box([p[0]+.35+i*.25,1.05,p[2]-.3],[.15,.15,.15],accent,mix([0,0,0],accent,lit*.28));}}
    else if(a===ACTIVITY.CODING_TESTING){for(let i=0;i<3;i++){const width=.18+.24*(active?(.5+.5*Math.sin(phase*5+i)):0.5);box([p[0]+.45+width/2,1.26-i*.17,p[2]-.27],[width,.035,.03],accent,mix([0,0,0],accent,.24));}}
    else if(a===ACTIVITY.CALCULATION){for(let i=0;i<3;i++){const r=.34+i*.14,angle=active?phase*(1.3+i*.22):0;const q=[p[0]+.57+Math.cos(angle)*r,1.16+(i-1)*.08,p[2]-.32+Math.sin(angle)*r];sphere(q,[.09,.09,.09],[.68,.48,1],active?[.20,.08,.40]:[0,0,0]);}}
    else if(a===ACTIVITY.AUDIT){cylinder([p[0]+.58,1.17,p[2]-.31],[.62,.06,.62],[.55,.14,.22],active?[.24*pulse,.03,.05]:[.03,0,0]);}
    else if(a===ACTIVITY.COMMIT){box([p[0]+.56,1.16,p[2]-.31],[.46,.46,.46],[.25,.72,.50],active?[.12*pulse,.28*pulse,.18*pulse]:[0,0,0]);}
    else if(a===ACTIVITY.HANDOFF){const x=active?Math.sin(phase*2.3)*.28:0;box([p[0]+.56+x,1.16,p[2]-.31],[.36,.22,.12],[.36,.66,.95],active?[.08,.18,.32]:[0,0,0]);}
    else if(a===ACTIVITY.RESULT){sphere([p[0]+.56,1.17,p[2]-.31],[.44,.44,.44],[.22,.72,.48],active?[.10*pulse,.34*pulse,.20*pulse]:[0,0,0]);}
    else if(a===ACTIVITY.BLOCKER){box([p[0]+.56,1.17,p[2]-.31],[.56,.14,.56],[.72,.10,.18],active?[.25*pulse,.01,.03]:[0,0,0]);}
  }

  function updateArchitectureLabels(vp){for(const node of visual.architectureNodes){const key=`arch:${node.id}`,n=ensureLabel(key,'architecture'),pt=project(vp,[node.position[0],.92,node.position[2]]);n.innerHTML=`<strong>${node.label}</strong><span>${node.subtitle} · structural node</span>`;n.style.transform=`translate3d(${pt.x}px,${pt.y}px,0) translate(-50%,-100%)`;n.hidden=!pt.visible;}}
  function updateAgentLabel(agent,vp,anchor){const key=`agent:${agent.id}`,n=ensureLabel(key,'agent'),pt=project(vp,anchor),destination=agent.destination?`<em class="dest-${agent.destination.toLowerCase()}">${agent.destination}</em>`:'';n.classList.toggle('is-selected',agent.selected);n.classList.toggle('is-animating',agent.animate);n.classList.toggle('is-stale',agent.state==='STALE');n.innerHTML=`<span class="scene3d-label-role">${agent.label}</span><strong>${agent.state}</strong><small>${short(agent.task)}</small><small>${agent.activityLabel}</small>${destination}`;n.style.transform=`translate3d(${pt.x}px,${pt.y}px,0) translate(-50%,-100%)`;n.hidden=!pt.visible;pickable.push({id:agent.id,x:pt.x,y:pt.y,visible:pt.visible});}
  function pruneLabels(){const valid=new Set([...visual.architectureNodes.map(n=>`arch:${n.id}`),...visual.agents.map(a=>`agent:${a.id}`)]);for(const [key,n] of labels){if(!valid.has(key)){n.remove();labels.delete(key);}}}

  function renderFrame(now){if(destroyed)return;raf=requestAnimationFrame(renderFrame);if(!visible)return;const vp=viewProjection();mini.begin(vp);pickable.length=0;drawEnvironment(now,vp);for(const agent of visual.agents)drawStation(agent,now,vp);pruneLabels();}

  function reset(){camera.yaw=-.72;camera.pitch=.66;camera.distance=19;camera.target=[0,1,.7];}
  function zoom(delta){camera.distance=clamp(camera.distance-delta*12,9.5,30);}
  const pointerDown=e=>{viewport.setPointerCapture?.(e.pointerId);camera.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,lastX:e.clientX,lastY:e.clientY});camera.dragged=false;if(camera.pointers.size===2){const[a,b]=[...camera.pointers.values()];camera.pinch={distance:Math.hypot(a.x-b.x,a.y-b.y),cameraDistance:camera.distance};}};
  const pointerMove=e=>{const p=camera.pointers.get(e.pointerId);if(!p)return;const dx=e.clientX-p.lastX,dy=e.clientY-p.lastY;p.x=e.clientX;p.y=e.clientY;p.lastX=e.clientX;p.lastY=e.clientY;if(Math.hypot(dx,dy)>1.5)camera.dragged=true;if(camera.pointers.size===1){camera.yaw-=dx*.008;camera.pitch=clamp(camera.pitch+dy*.006,.28,1.18);}else if(camera.pointers.size===2){const[a,b]=[...camera.pointers.values()];if(camera.pinch){const d=Math.max(1,Math.hypot(a.x-b.x,a.y-b.y));camera.distance=clamp(camera.pinch.cameraDistance*(camera.pinch.distance/d),9.5,30);}}};
  const pointerUp=e=>{const p=camera.pointers.get(e.pointerId);camera.pointers.delete(e.pointerId);if(camera.pointers.size<2)camera.pinch=null;if(!camera.dragged&&p){const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top;let best=null;for(const item of pickable){if(!item.visible)continue;const d=Math.hypot(item.x-x,item.y-y);if(d<52&&(!best||d<best.d))best={...item,d};}if(best)onSelectAgent(best.id);}};
  const wheel=e=>{e.preventDefault();camera.distance=clamp(camera.distance*(e.deltaY>0?1.08:.92),9.5,30);};
  const visibility=()=>{visible=!document.hidden;};
  viewport.addEventListener('pointerdown',pointerDown);viewport.addEventListener('pointermove',pointerMove);viewport.addEventListener('pointerup',pointerUp);viewport.addEventListener('pointercancel',pointerUp);viewport.addEventListener('wheel',wheel,{passive:false});document.addEventListener('visibilitychange',visibility);
  raf=requestAnimationFrame(renderFrame);

  return{
    ready:true,
    update(state,{selectedWorkerId:nextSelected=null}={}){selectedWorkerId=nextSelected;visual=deriveSceneVisual(state,{selectedWorkerId});},
    reset,
    zoom,
    destroy(){destroyed=true;cancelAnimationFrame(raf);viewport.removeEventListener('pointerdown',pointerDown);viewport.removeEventListener('pointermove',pointerMove);viewport.removeEventListener('pointerup',pointerUp);viewport.removeEventListener('pointercancel',pointerUp);viewport.removeEventListener('wheel',wheel);document.removeEventListener('visibilitychange',visibility);for(const n of labels.values())n.remove();labels.clear();mini.destroy();viewport.classList.remove('has-webgl');},
  };
}

export const SCENE3D_CAPABILITIES=Object.freeze({renderer:'WebGL',externalRuntimeDependencies:0,businessAnimationAuthority:'state.animationRunning',webglFallback:'existing DOM research floor',mobileSafari:true});
