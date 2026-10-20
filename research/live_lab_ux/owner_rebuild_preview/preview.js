const canvas=document.getElementById('gl');
const zoneLayer=document.getElementById('zone-layer');
const workerChip=document.getElementById('worker-chip');
const workerPanel=document.getElementById('worker-panel');
const econEl=document.getElementById('economic');
const params=new URLSearchParams(location.search);
const scenario=window.__SCENARIO__||params.get('state')||'idle';
const isMobile=window.__MOBILE__===true||params.get('mobile')==='1'||innerWidth<600;

const state={connected:true,economicActive:scenario==='economic',selected:scenario==='selected',workerActive:['active','selected','economic'].includes(scenario),workerId:'worker-canary',animationRunning:['active','economic'].includes(scenario),activity:'coding-testing'};
if(state.economicActive){state.activity='calculation-economic-look';state.animationRunning=true;econEl.textContent='ACTIVE';}

const gl=canvas.getContext('webgl',{alpha:false,antialias:true,preserveDrawingBuffer:true});
if(!gl){canvas.hidden=true;document.getElementById('fallback').hidden=false;throw new Error('WebGL unavailable');}

const VS=`attribute vec3 p;attribute vec3 n;uniform mat4 m;uniform mat4 vp;varying vec3 N;varying vec3 W;void main(){vec4 w=m*vec4(p,1.0);W=w.xyz;N=mat3(m)*n;gl_Position=vp*w;}`;
const FS=`precision mediump float;varying vec3 N;varying vec3 W;uniform vec3 c;uniform vec3 e;uniform vec3 eye;uniform float alpha;uniform vec3 amberPos;void main(){vec3 nn=normalize(N);vec3 d=normalize(vec3(-.35,.8,.45));float diff=max(dot(nn,d),0.0);vec3 lp=normalize(amberPos-W);float warm=max(dot(nn,lp),0.0)/(1.0+.06*length(amberPos-W)*length(amberPos-W));float rim=pow(1.0-max(dot(nn,normalize(eye-W)),0.0),2.0);vec3 col=c*(.36+.72*diff)+vec3(1.0,.52,.17)*warm*.85+c*rim*.14+e;float fog=clamp((length(eye-W)-14.0)/38.0,0.0,.42);col=mix(col,vec3(.028,.055,.084),fog);col=pow(max(col,vec3(0.0)),vec3(.82));gl_FragColor=vec4(col,alpha);}`;
function shader(t,s){const sh=gl.createShader(t);gl.shaderSource(sh,s);gl.compileShader(sh);if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(sh));return sh}
const prog=gl.createProgram();gl.attachShader(prog,shader(gl.VERTEX_SHADER,VS));gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,FS));gl.linkProgram(prog);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(prog));gl.useProgram(prog);
const loc={p:gl.getAttribLocation(prog,'p'),n:gl.getAttribLocation(prog,'n'),m:gl.getUniformLocation(prog,'m'),vp:gl.getUniformLocation(prog,'vp'),c:gl.getUniformLocation(prog,'c'),e:gl.getUniformLocation(prog,'e'),eye:gl.getUniformLocation(prog,'eye'),alpha:gl.getUniformLocation(prog,'alpha'),amber:gl.getUniformLocation(prog,'amberPos')};

gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);

const M={id:()=>[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],mul:(a,b)=>{const o=new Array(16).fill(0);for(let r=0;r<4;r++)for(let c=0;c<4;c++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o},tr:(x,y,z)=>[1,0,0,0,0,1,0,0,0,0,1,0,x,y,z,1],sc:(x,y,z)=>[x,0,0,0,0,y,0,0,0,0,z,0,0,0,0,1],rx:a=>{let c=Math.cos(a),s=Math.sin(a);return[1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1]},ry:a=>{let c=Math.cos(a),s=Math.sin(a);return[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]},rz:a=>{let c=Math.cos(a),s=Math.sin(a);return[c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1]},persp:(fov,asp,n,f)=>{let q=1/Math.tan(fov/2),nf=1/(n-f);return[q/asp,0,0,0,0,q,0,0,0,0,(f+n)*nf,-1,0,0,2*f*n*nf,0]},look:(eye,t,up=[0,1,0])=>{let zx=eye[0]-t[0],zy=eye[1]-t[1],zz=eye[2]-t[2],zl=Math.hypot(zx,zy,zz);zx/=zl;zy/=zl;zz/=zl;let xx=up[1]*zz-up[2]*zy,xy=up[2]*zx-up[0]*zz,xz=up[0]*zy-up[1]*zx,xl=Math.hypot(xx,xy,xz);xx/=xl;xy/=xl;xz/=xl;let yx=zy*xz-zz*xy,yy=zz*xx-zx*xz,yz=zx*xy-zy*xx;return[xx,yx,zx,0,xy,yy,zy,0,xz,yz,zz,0,-(xx*eye[0]+xy*eye[1]+xz*eye[2]),-(yx*eye[0]+yy*eye[1]+yz*eye[2]),-(zx*eye[0]+zy*eye[1]+zz*eye[2]),1]}};
function rgb(hex){return[(hex>>16&255)/255,(hex>>8&255)/255,(hex&255)/255]}
function makeMesh(P,N,I){const v=gl.createBuffer(),no=gl.createBuffer(),ib=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,v);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(P),gl.STATIC_DRAW);gl.bindBuffer(gl.ARRAY_BUFFER,no);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(N),gl.STATIC_DRAW);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint16Array(I),gl.STATIC_DRAW);return{v,no,ib,count:I.length}}
function cube(){const p=[],n=[],i=[];const F=[[[1,0,0],[1,-1,-1],[1,1,-1],[1,1,1],[1,-1,1]],[[-1,0,0],[-1,-1,1],[-1,1,1],[-1,1,-1],[-1,-1,-1]],[[0,1,0],[-1,1,-1],[-1,1,1],[1,1,1],[1,1,-1]],[[0,-1,0],[-1,-1,1],[-1,-1,-1],[1,-1,-1],[1,-1,1]],[[0,0,1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],[[0,0,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],[1,1,-1]]];for(const f of F){let b=p.length/3;for(let k=1;k<5;k++){p.push(...f[k]);n.push(...f[0])}i.push(b,b+1,b+2,b,b+2,b+3)}return makeMesh(p,n,i)}
function cyl(seg=20){const p=[],n=[],i=[];for(let y of[-1,1])for(let s=0;s<seg;s++){let a=s/seg*Math.PI*2;p.push(Math.cos(a),y,Math.sin(a));n.push(Math.cos(a),0,Math.sin(a))}for(let s=0;s<seg;s++){let q=(s+1)%seg;i.push(s,q,seg+q,s,seg+q,seg+s)}let base=p.length/3;for(let y of[-1,1]){let c=p.length/3;p.push(0,y,0);n.push(0,y,0);for(let s=0;s<seg;s++){let a=s/seg*Math.PI*2;p.push(Math.cos(a),y,Math.sin(a));n.push(0,y,0)}for(let s=0;s<seg;s++){let q=(s+1)%seg;i.push(c,c+1+s,c+1+q)}}return makeMesh(p,n,i)}
function sphere(lat=10,lon=16){const p=[],n=[],i=[];for(let y=0;y<=lat;y++){let v=y/lat,ph=v*Math.PI;for(let x=0;x<=lon;x++){let u=x/lon,th=u*Math.PI*2,s=Math.sin(ph),X=Math.cos(th)*s,Y=Math.cos(ph),Z=Math.sin(th)*s;p.push(X,Y,Z);n.push(X,Y,Z)}}for(let y=0;y<lat;y++)for(let x=0;x<lon;x++){let a=y*(lon+1)+x,b=a+lon+1;i.push(a,b,a+1,b,b+1,a+1)}return makeMesh(p,n,i)}
function torus(seg=32,tube=8,R=1,r=.08){const p=[],n=[],i=[];for(let a=0;a<=seg;a++){let A=a/seg*Math.PI*2;for(let b=0;b<=tube;b++){let B=b/tube*Math.PI*2,cb=Math.cos(B),sb=Math.sin(B),ca=Math.cos(A),sa=Math.sin(A);p.push((R+r*cb)*ca,r*sb,(R+r*cb)*sa);n.push(cb*ca,sb,cb*sa)}}for(let a=0;a<seg;a++)for(let b=0;b<tube;b++){let q=a*(tube+1)+b,w=q+tube+1;i.push(q,w,q+1,w,w+1,q+1)}return makeMesh(p,n,i)}
const meshes={cube:cube(),cyl:cyl(),sphere:sphere(),ring:torus()};
function draw(mesh,model,color,emissive=[0,0,0],alpha=1){gl.bindBuffer(gl.ARRAY_BUFFER,mesh.v);gl.vertexAttribPointer(loc.p,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(loc.p);gl.bindBuffer(gl.ARRAY_BUFFER,mesh.no);gl.vertexAttribPointer(loc.n,3,gl.FLOAT,false,0,0);gl.enableVertexAttribArray(loc.n);gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,mesh.ib);gl.uniformMatrix4fv(loc.m,false,new Float32Array(model));gl.uniform3fv(loc.c,color);gl.uniform3fv(loc.e,emissive);gl.uniform1f(loc.alpha,alpha);gl.drawElements(gl.TRIANGLES,mesh.count,gl.UNSIGNED_SHORT,0)}
const compose=(...m)=>m.reduce((a,b)=>M.mul(a,b),M.id());
const box=(x,y,z,sx,sy,sz,c,e=[0,0,0],a=1,rot=0)=>draw(meshes.cube,compose(M.tr(x,y,z),M.ry(rot),M.sc(sx/2,sy/2,sz/2)),rgb(c),e,a);
const cylinder=(x,y,z,r,h,c,e=[0,0,0],a=1)=>draw(meshes.cyl,compose(M.tr(x,y,z),M.sc(r,h/2,r)),rgb(c),e,a);
const ball=(x,y,z,r,c,e=[0,0,0],a=1)=>draw(meshes.sphere,compose(M.tr(x,y,z),M.sc(r,r,r)),rgb(c),e,a);
const ring=(x,y,z,R,r,c,rx=0,rz=0,e=[0,0,0],a=1)=>draw(meshes.ring,compose(M.tr(x,y,z),M.rx(rx),M.rz(rz),M.sc(R,R,R)),rgb(c),e,a);

const zoneDefs=[['MECHANISMS',-7,0,-4.5],['EVENT / DOCS',7,0,-4.2],['VALIDATION',-7,0,4.4],['EVIDENCE',7,0,4.5],['IMPLEMENTABILITY',0,0,6.6]];
for(const[z]of zoneDefs){let d=document.createElement('div');d.className='zone-label';d.textContent=z;zoneLayer.appendChild(d)}

let yaw=isMobile?-.56:-.66,pitch=isMobile?.17:.22,dist=isMobile?18.2:18.8,target=[0,1.75,.45];let desired={yaw,pitch,dist,target:[...target]};let drag=false,lastPointer=[0,0],pinch=0;
if(state.selected){desired={yaw:-1.05,pitch:.14,dist:isMobile?8.7:8.2,target:[4.15,1.30,3.35]};yaw=desired.yaw;pitch=desired.pitch;dist=desired.dist;target=[...desired.target];workerPanel.hidden=false;workerChip.hidden=true}
canvas.addEventListener('pointerdown',e=>{drag=true;lastPointer=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!drag)return;let dx=e.clientX-lastPointer[0],dy=e.clientY-lastPointer[1];lastPointer=[e.clientX,e.clientY];desired.yaw-=dx*.006;desired.pitch=Math.max(.08,Math.min(.58,desired.pitch-dy*.004))});canvas.addEventListener('pointerup',e=>{drag=false;selectNear(e.clientX,e.clientY)});canvas.addEventListener('wheel',e=>{e.preventDefault();desired.dist=Math.max(10,Math.min(35,desired.dist*(e.deltaY>0?1.06:.94)))},{passive:false});
let touches=new Map();canvas.addEventListener('pointerdown',e=>{touches.set(e.pointerId,[e.clientX,e.clientY]);if(touches.size===2){let[a,b]=[...touches.values()];pinch=Math.hypot(a[0]-b[0],a[1]-b[1])}});canvas.addEventListener('pointermove',e=>{if(touches.has(e.pointerId)){touches.set(e.pointerId,[e.clientX,e.clientY]);if(touches.size===2){let[a,b]=[...touches.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]);if(pinch){desired.dist=Math.max(10,Math.min(35,desired.dist*pinch/d));pinch=d}}}});['pointerup','pointercancel'].forEach(t=>canvas.addEventListener(t,e=>touches.delete(e.pointerId)));
document.getElementById('reset').onclick=()=>{desired={yaw:isMobile?-.56:-.66,pitch:isMobile?.17:.22,dist:isMobile?18.2:18.8,target:[0,1.75,.45]};workerPanel.hidden=true};document.getElementById('zoom-in').onclick=()=>desired.dist=Math.max(10,desired.dist-2);document.getElementById('zoom-out').onclick=()=>desired.dist=Math.min(35,desired.dist+2);document.getElementById('close-panel').onclick=()=>{workerPanel.hidden=true;document.getElementById('reset').click()};workerChip.onclick=()=>focusWorker();
function focusWorker(){desired={yaw:-1.05,pitch:.14,dist:isMobile?8.7:8.2,target:[4.15,1.30,3.35]};workerPanel.hidden=false;workerChip.hidden=true}
let workerScreen=[innerWidth*.5,innerHeight*.5];function selectNear(x,y){if(!state.workerActive)return;if(Math.hypot(x-workerScreen[0],y-workerScreen[1])<65)focusWorker()}

function resize(){let d=Math.min(devicePixelRatio||1,1.6),w=Math.floor(innerWidth*d),h=Math.floor(innerHeight*d);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h)}}
function project(p,vp){let x=p[0],y=p[1],z=p[2],w=vp[3]*x+vp[7]*y+vp[11]*z+vp[15];return[(vp[0]*x+vp[4]*y+vp[8]*z+vp[12])/w,(vp[1]*x+vp[5]*y+vp[9]*z+vp[13])/w,(vp[2]*x+vp[6]*y+vp[10]*z+vp[14])/w]}
function setZoneLabels(vp){zoneDefs.forEach((q,i)=>{let p=project([q[1],.45,q[3]],vp),d=zoneLayer.children[i];d.style.left=((p[0]*.5+.5)*innerWidth)+'px';d.style.top=((-p[1]*.5+.5)*innerHeight)+'px';d.style.opacity=p[2]>1?0:.86})}

function floorAndArchitecture(t){
 box(0,-.35,0,22,.6,15.5,0x0b1722);box(0,-.02,0,21.6,.08,15.1,0x152536);
 cylinder(0,.045,0,5.45,.10,0x102536);cylinder(0,.085,0,4.15,.11,0x1a3040);
 for(let a=0;a<8;a++){let q=a*Math.PI/4,px=Math.sin(q)*4.8,pz=Math.cos(q)*4.8;box(px,.13,pz,1.65,.045,.18,0x9b6637,[.018,.008,.002],.72,q);ball(Math.sin(q)*5.28,.16,Math.cos(q)*5.28,.045,0xd09a58,[.04,.018,.004],.82)}
 for(let x=-9;x<=9;x+=3)box(x,.025,0,.025,.018,13.7,0x294158,[0.005,.008,.012],.55);
 for(let z=-6;z<=6;z+=3)box(0,.026,z,19,.018,.025,0x21374c,[.004,.006,.01],.48);
 for(let x=-9;x<=9;x+=3){box(x,2.8,-7.25,.22,5.5,.45,0x162b3c);box(x,5.45,-7.25,.28,.24,.6,0x2b4657)}
 box(0,5.3,-7.35,20,.34,.5,0x132a3b);box(-10,2.3,0,.42,4.7,14,0x102333);box(10,2.3,0,.42,4.7,14,0x102333);
 for(let x of[-5.8,-4.35,-2.9]){box(x,1.7,-6.78,1.05,2.75,.52,0x1c3240);for(let y=.65;y<2.8;y+=.46){box(x,y,-6.48,.82,.19,.03,0x29495b,[.006,.014,.018],.95);for(let j=0;j<3;j++)ball(x-.23+j*.23,y,-6.45,.025,j===1?0xd5a052:0x718c9b,[j===1?.04:.002,.01,.012],.9)}}
 box(0,3.1,-6.95,18,.06,.7,0x314657,[0.01,.02,.025],.55);for(let x=-8;x<=8;x+=2)box(x,3.35,-6.8,.04,.75,.08,0x4b6474,[.01,.015,.02],.45);
 box(-7.9,.34,3.8,4.3,.55,5.2,0x132a39);box(7.9,.34,3.8,4.3,.55,5.2,0x132a39);
 for(let i=0;i<4;i++){box(-5.6+i*.55,.10+i*.08,5.0,.55,.16,1.9,0x1b3344);box(5.6-i*.55,.10+i*.08,5.0,.55,.16,1.9,0x1b3344)}
 for(const [x,z] of [[-7,-4.7],[7,-4.7],[-7,4.2],[7,4.2]]){box(x,.12,z,4.1,.16,3.2,0x172d3b);box(x,1.05,z-1.55,4.2,2.0,.12,0x203848,[.004,.007,.01],.96);for(let dx of[-1.75,1.75])box(x+dx,1.15,z,.11,2.3,3.2,0x27465a,[.01,.014,.018],.72)}
 for(const x of[-8.8,-4.5,4.5,8.8])box(x,2.1,-6.95,.07,3.5,.08,0xb06d32,[.035,.019,.006],.78);
}
function centralColumn(t){
 const active=state.economicActive;let pulse=active?(1+Math.sin(t*2.2)*.08):1;
 cylinder(0,.12,0,2.2,.18,0x1a2b36);cylinder(0,.34,0,1.65,.28,0x263c48);cylinder(0,.62,0,1.15,.34,0x101f2c);
 for(let h of[1.05,1.95,2.85,3.75])ring(0,h,0,1.15,.05,active?0xd49a4f:0x496273,Math.PI/2,0,active?[.10,.045,.01]:[0,0,0],active?.95:.72);
 cylinder(0,2.45,0,.32,3.7,active?0xc37e3c:0x27495f,active?[.16,.07,.012]:[.005,.01,.015],active?.88:.65);
 cylinder(0,2.45,0,.12,3.35,0xe6a959,active?[.65,.22,.035]:[.05,.022,.007],active?.88:.65);
 for(let y=1.1;y<=3.8;y+=.45)ball(0,y,0,.10*pulse,active?0xffc471:0x7897aa,active?[.55,.19,.025]:[.01,.016,.02],.9);
 for(let a=0;a<4;a++){let q=a*Math.PI/2;box(Math.cos(q)*1.45,2.3,Math.sin(q)*1.45,.16,3.5,.16,0x314b5b)}
 ring(0,4.55,0,2.0,.035,0x617887,Math.PI/2,0,[.015,.02,.025],.6);box(0,4.55,0,4.0,.05,.05,0x405767);box(0,4.55,0,.05,.05,4.0,0x405767);
}
function station(x,z,rot,accent=0x31546b){
 box(x,.10,z,3.4,.18,2.6,0x142836,[0,0,0],1,rot);box(x,.72,z,2.35,.12,.95,0x283c47,[0,0,0],1,rot);
 for(let side of[-1,1]){let dx=Math.cos(rot)*side*.95,dz=-Math.sin(rot)*side*.95;box(x+dx,.38,z+dz,.08,.62,.08,0x3b515c)}
 const fwd=[Math.sin(rot),0,Math.cos(rot)],right=[Math.cos(rot),0,-Math.sin(rot)];
 const screen=(offX,offY,offZ,w,h,col)=>{let px=x+right[0]*offX+fwd[0]*offZ,pz=z+right[2]*offX+fwd[2]*offZ;box(px,1.32+offY,pz,w,h,.06,col,[.01,.02,.025],1,rot)};
 screen(0,.08,-.35,1.05,.56,0x275268);screen(-.72,.02,-.30,.45,.4,0x23465a);screen(.72,.02,-.30,.45,.4,0x23465a);box(x+right[0]*0.0+fwd[0]*-.382,1.61,z+right[2]*0.0+fwd[2]*-.382,.72,.018,.025,0x6f98a8,[.018,.03,.035],.8,rot);
 box(x+right[0]*0.0+fwd[0]*.28,.82,z+right[2]*0.0+fwd[2]*.28,.85,.035,.35,0x6b5538,[.015,.009,.003],1,rot);
 box(x-fwd[0]*.65,.52,z-fwd[2]*.65,.52,.11,.48,0x223b4a,[0,0,0],1,rot);box(x-fwd[0]*.83,.81,z-fwd[2]*.83,.52,.66,.10,0x294657,[0,0,0],1,rot);
 box(x+right[0]*1.35,.44,z+right[2]*1.35,.05,.45,.05,accent,[.02,.009,.002],.8,rot);
}
function opsRing(){const pts=[[-5.2,-1.8,.95],[5.2,-1.8,-.95],[-5.6,1.7,1.65],[5.6,1.7,-1.65],[-2.7,4.4,2.8],[2.7,4.4,-2.8],[-2.7,-4.3,.35],[2.7,-4.3,-.35]];pts.forEach((p,i)=>station(p[0],p[1],p[2],i%2?0x355d73:0x885c34))}
function human(x,z,rot,t,active=true){
 const bob=active?Math.sin(t*5)*.018:0;const f=[Math.sin(rot),0,Math.cos(rot)],r=[Math.cos(rot),0,-Math.sin(rot)];
 cylinder(x,1.08+bob,z,.20,.62,0x365f72);box(x,.78+bob,z,.48,.48,.24,0x426e80,[0,0,0],1,rot);
 ball(x,1.56+bob,z,.19,0xb68565);box(x,1.68+bob,z,.29,.11,.23,0x212a2e,[0,0,0],1,rot);
 box(x+f[0]*.185,1.56+bob,z+f[2]*.185,.20,.035,.025,0x8ca8b5,[.018,.026,.03],.9,rot);
 let swing=active?Math.sin(t*6)*.12:0;for(let side of[-1,1]){let sx=x+r[0]*side*.29,sz=z+r[2]*side*.29;box(sx,1.12+bob,sz,.11,.56,.11,0xb68565,[0,0,0],1,rot+swing*side);box(x+r[0]*side*.14-f[0]*.12,.43,z+r[2]*side*.14-f[2]*.12,.16,.62,.18,0x1b3040,[0,0,0],1,rot)}
}
function activeWorker(t){if(!state.workerActive)return;const x=4.15,z=3.35,rot=-2.45;ring(x,.08,z,.42,.045,0xb67a3d,Math.PI/2,0,[.06,.022,.004],.82);human(x,z,rot,t,state.animationRunning);let f=[Math.sin(rot),0,Math.cos(rot)],r=[Math.cos(rot),0,-Math.sin(rot)];if(state.animationRunning){box(x+f[0]*.68,1.45,z+f[2]*.68,.72,.035,.025,0xd9954c,[.14,.052,.008],.95,rot);for(let i=0;i<3;i++){let px=x+f[0]*(.8+i*.18)+r[0]*((i-1)*.14),pz=z+f[2]*(.8+i*.18)+r[2]*((i-1)*.14);ball(px,1.45+i*.08,pz,.045,0xe4a85b,[.08,.03,.004],.9)}}}
function atmosphere(t){for(let i=0;i<7;i++){let x=-8+i*2.6,z=-6.6,y=4.7+Math.sin(t*.2+i)*.05;ball(x,y,z,.035,0xc78947,[.025,.012,.003],.35)}}

let lastFrame=performance.now();function frame(now){resize();let dt=Math.min((now-lastFrame)/1000,.05);lastFrame=now;let k=1-Math.pow(.002,dt);yaw+=(desired.yaw-yaw)*k;pitch+=(desired.pitch-pitch)*k;dist+=(desired.dist-dist)*k;for(let i=0;i<3;i++)target[i]+=(desired.target[i]-target[i])*k;
 const cp=Math.cos(pitch),sp=Math.sin(pitch),eye=[target[0]+Math.sin(yaw)*cp*dist,target[1]+sp*dist,target[2]+Math.cos(yaw)*cp*dist];let vp=M.mul(M.persp(isMobile?52*Math.PI/180:46*Math.PI/180,canvas.width/canvas.height,.1,80),M.look(eye,target));gl.uniformMatrix4fv(loc.vp,false,new Float32Array(vp));gl.uniform3fv(loc.eye,eye);gl.uniform3fv(loc.amber,[0,3.0,0]);gl.clearColor(.024,.045,.071,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
 const t=now/1000;floorAndArchitecture(t);opsRing();centralColumn(t);atmosphere(t);activeWorker(t);setZoneLabels(vp);
 if(state.workerActive){let p=project([4.15,1.92,3.35],vp);workerScreen=[(p[0]*.5+.5)*innerWidth,(-p[1]*.5+.5)*innerHeight];if(workerPanel.hidden){workerChip.hidden=false;workerChip.style.left=Math.max(92,Math.min(innerWidth-92,workerScreen[0]))+'px';workerChip.style.top=Math.max(90,Math.min(innerHeight-100,workerScreen[1]))+'px'}}
 requestAnimationFrame(frame)}requestAnimationFrame(frame);
window.__QT_PREVIEW__={state,focusWorker,setState(next){Object.assign(state,next)}};
