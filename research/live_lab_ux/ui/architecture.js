import * as T from './vendor/three.js';

// All architectural objects and screen textures are decorative, never research data.
export const ZONES = [
 {id:'research',name:'MECHANISMS',sub:'01 / RESEARCH',x:-10,z:-7,y:1.05,angle:.35,type:'library'},
 {id:'documents',name:'DOCUMENTS',sub:'02 / EVENTS',x:-4,z:-12,y:1.05,angle:.10,type:'archive'},
 {id:'fundamental',name:'FUNDAMENTAL',sub:'03 / RESEARCH',x:4,z:-12,y:1.05,angle:-.12,type:'library'},
 {id:'flows',name:'FLOWS / REGULATORY',sub:'04 / CONTEXT',x:11,z:-8,y:1.05,angle:-.65,type:'panels'},
 {id:'data',name:'DATA / EVIDENCE',sub:'05 / PROVENANCE',x:-13,z:.5,y:.4,angle:.95,type:'racks'},
 {id:'validation',name:'VALIDATION',sub:'06 / RED TEAM',x:11,z:-1,y:.4,angle:-.9,type:'compare'},
 {id:'decay',name:'EDGE ARCHAEOLOGY',sub:'07 / DECAY',x:-12,z:7,y:.4,angle:1.15,type:'archive'},
 {id:'implement',name:'IMPLEMENTABILITY',sub:'08 / BUILD',x:9,z:6,y:.4,angle:-1.15,type:'instrument'},
 {id:'experiment',name:'EXPERIMENT SYSTEMS',sub:'09 / INFRASTRUCTURE',x:3,z:11,y:.4,angle:Math.PI,type:'racks'},
 {id:'identity',name:'ECONOMIC IDENTITY',sub:'10 / INTEGRATION',x:-6,z:8,y:.4,angle:1.7,type:'instrument'},
 {id:'portfolio',name:'PORTFOLIO',sub:'11 / INTEGRATION',x:-3,z:13,y:.4,angle:Math.PI,type:'table'},
];
export const mats={};
const gcache=new Map();
function geo(key,make){if(!gcache.has(key))gcache.set(key,make());return gcache.get(key);}
function mat(color,roughness=.55,metalness=.2,other={}){return new T.MeshStandardMaterial({color,roughness,metalness,...other});}
function mesh(parent,geometry,material,x=0,y=0,z=0){const m=new T.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
export function box(p,w,h,d,m,x=0,y=0,z=0,r=.035){
 let geometry;
 if(r&&Math.min(w,h,d)>.08){const s=new T.Shape(),a=w/2,b=d/2,rr=Math.min(r,w/3,d/3);s.moveTo(-a+rr,-b);s.lineTo(a-rr,-b);s.quadraticCurveTo(a,-b,a,-b+rr);s.lineTo(a,b-rr);s.quadraticCurveTo(a,b,a-rr,b);s.lineTo(-a+rr,b);s.quadraticCurveTo(-a,b,-a,b-rr);s.lineTo(-a,-b+rr);s.quadraticCurveTo(-a,-b,-a+rr,-b);geometry=geo(`round:${w}:${h}:${d}:${rr}`,()=>{const g=new T.ExtrudeGeometry(s,{depth:h,bevelEnabled:false,curveSegments:3});g.rotateX(-Math.PI/2);g.translate(0,-h/2,0);return g;});}
 else geometry=geo(`box:${w}:${h}:${d}`,()=>new T.BoxGeometry(w,h,d));
 return mesh(p,geometry,m,x,y,z);
}
export function cylinder(p,rt,rb,h,m,x=0,y=0,z=0,n=48){return mesh(p,geo(`c:${rt}:${rb}:${h}:${n}`,()=>new T.CylinderGeometry(rt,rb,h,n)),m,x,y,z);}
function ring(p,r,t,m,x,y,z){const o=mesh(p,geo(`ring:${r}:${t}`,()=>new T.TorusGeometry(r,t,8,96)),m,x,y,z);o.rotation.x=Math.PI/2;return o;}
function arc(p,inner,outer,height,start,length,m,y=0){const o=mesh(p,new T.CylinderGeometry(outer,outer,height,96,1,true,start,length),m,0,y+height/2,0);o.material.side=T.DoubleSide;const floor=mesh(p,new T.RingGeometry(inner,outer,96,1,start,length),m,0,y,0);floor.rotation.x=-Math.PI/2;return o;}
function makeTexture(draw,w=1024,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;return t;}
function textPanel(parent,text,sub,w,h,x,y,z){const texture=makeTexture((c,W,H)=>{c.fillStyle='#152d40';c.fillRect(0,0,W,H);c.fillStyle='#c6b691';c.fillRect(44,H*.28,32,3);c.font='500 39px sans-serif';c.fillText(text,44,H*.51);c.fillStyle='#8295a2';c.font='22px monospace';c.fillText(sub,44,H*.76);});const m=new T.MeshBasicMaterial({map:texture});const panel=mesh(parent,new T.PlaneGeometry(w,h),m,x,y,z);panel.castShadow=false;return panel;}
function neutralScreen(parent,x,y,z,w=1.12,h=.69,angle=0){const g=new T.Group();g.position.set(x,y,z);g.rotation.y=angle;parent.add(g);box(g,w+.075,h+.065,.055,mats.steel,0,0,0,.025);const t=geo('screen',()=>makeTexture((c,W,H)=>{c.fillStyle='#0b1c2a';c.fillRect(0,0,W,H);c.strokeStyle='#405769';c.lineWidth=2;for(let i=0;i<5;i++){c.strokeRect(48+i*130,100+i%2*40,100,225);}c.strokeStyle='#a08961';c.beginPath();c.arc(W*.75,H*.47,72,0,Math.PI*2);c.stroke();c.font='23px monospace';c.fillStyle='#b0bbc0';c.fillText('STATION / AVAILABLE',42,48);c.font='18px monospace';c.fillStyle='#708a98';c.fillText('SYSTEM GEOMETRY · NON-DATA',42,H-34);}));const s=mesh(g,new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:t}),0,0,.031);s.castShadow=false;return g;}
function book(parent,x,y,z,i){const colors=[mats.paper,mats.wood,mats.fabric,mats.blue,mats.steel];box(parent,.085+.025*(i%3),.32+.05*(i%4),.29,colors[i%5],x,y,z,.008);}
function archive(parent){box(parent,3.7,2.45,.5,mats.blue,0,1.23,-1.4);for(let row=0;row<4;row++){box(parent,3.65,.055,.55,mats.steel,0,.28+row*.57,-1.38);for(let i=0;i<18;i++)book(parent,-1.65+i*.18,.50+row*.57,-1.36,i+row*3);}box(parent,3.7,.035,.035,mats.light,0,2.48,-1.06);}
function equipment(parent,type){if(type==='library'||type==='archive'){archive(parent);if(type==='archive'){box(parent,1,.65,.8,mats.stone,2, .33,-.7);for(let j=0;j<4;j++)box(parent,.81,.09,.64,mats.paper,2,.72+j*.1,-.7);}}
 if(type==='racks'){for(let j=0;j<3;j++){box(parent,.76,2.3,.7,mats.blue,-1.1+j*.95,1.15,-1.3);for(let k=0;k<8;k++){box(parent,.66,.19,.025,mats.steel,-1.1+j*.95,.25+k*.25,-.93);box(parent,.025,.023,.035,k%3===0?mats.light:mats.dim,-.85+j*.95,.25+k*.25,-.90);}}}
 if(type==='panels'||type==='compare'){for(let j=0;j<3;j++){const p=new T.Group();p.position.set((j-1)*1.26,1.7,-1.3);p.rotation.y=(1-j)*.12;parent.add(p);neutralScreen(p,0,0,0,1.14,1.2);cylinder(p,.035,.035,1.1,mats.steel,0,-1,0);}}
 if(type==='instrument'){box(parent,1.05,.9,.8,mats.stone,1.75,.45,-.8);cylinder(parent,.3,.39,.35,mats.steel,1.75,1.05,-.8);cylinder(parent,.23,.23,.62,mats.glass,1.75,1.5,-.8);ring(parent,.3,.025,mats.light,1.75,1.25,-.8);box(parent,.8,.06,.65,mats.paper,-1.3,1.02,.1);}
 if(type==='table'){const t=cylinder(parent,1.45,1.45,.14,mats.wood,0,1.03,-.5);t.scale.z=.7;cylinder(parent,.52,.65,.85,mats.blue,0,.5,-.5);ring(parent,1.12,.012,mats.dim,0,1.11,-.5);}
}
export function workstation(parent){
 box(parent,3.4,.13,1.22,mats.wood,0,.94,.38,.15);box(parent,3.34,.025,.04,mats.steel,0,.91,1);
 for(const x of [-1.32,1.32]){box(parent,.13,.87,.78,mats.steel,x,.47,.38);box(parent,.38,.045,.95,mats.blue,x,.055,.4);}
 box(parent,.62,.64,.65,mats.blue,1.05,.47,.4);for(let i=0;i<3;i++)box(parent,.49,.018,.035,mats.steel,1.05,.35+i*.16,.735);
 cylinder(parent,.034,.034,.36,mats.steel,0,1.18,.12);box(parent,.6,.025,.3,mats.steel,0,1.03,.14);neutralScreen(parent,-.32,1.56,.08);neutralScreen(parent,.73,1.52,.16,.72,.58,-.18);
 box(parent,.65,.025,.25,mats.fabric,-.3,1.025,.73);box(parent,.21,.018,.27,mats.paper,-1.18,1.025,.66);box(parent,.24,.018,.29,mats.paper,-1.13,1.05,.64);
 cylinder(parent,.075,.065,.13,mats.paper,1.38,1.08,.68,16);cylinder(parent,.06,.06,.008,mats.wood,1.38,1.15,.68,16);
 // Technical textile chair, polished frame, adult scale.
 cylinder(parent,.055,.055,.43,mats.steel,0,.3,1.56);const seat=box(parent,.62,.15,.56,mats.fabric,0,.56,1.54,.12);box(parent,.61,.64,.12,mats.fabric,0,.91,1.83,.1);
 for(let i=0;i<5;i++){const foot=box(parent,.05,.04,.52,mats.steel,0,.08,1.56);foot.rotation.y=i*Math.PI*.4;}
 for(let i=0;i<2;i++)box(parent,.035,.35,.035,mats.steel,i? .29:-.29,.68,1.62);
}
export function buildArchitecture(scene){
 Object.assign(mats,{blue:mat('#263c50',.5,.45),steel:mat('#687d89',.3,.78),stone:mat('#394650',.94,.06),floor:mat('#58636a',.79,.14),wood:mat('#615146',.82,.06),fabric:mat('#596775',.98,0),paper:mat('#c2bdb0',.9,0),glass:mat('#74939d',.19,.38,{transparent:true,opacity:.19,depthWrite:false,side:T.DoubleSide}),light:mat('#e8b875',.4,.3,{emissive:'#ffc27c',emissiveIntensity:2.1}),dim:mat('#879da6',.4,.3,{emissive:'#58798a',emissiveIntensity:.6})});
 const root=new T.Group();scene.add(root);
 const floor=cylinder(root,18.8,19,.65,mats.blue,0,-.35,0,128);cylinder(root,18.5,18.5,.13,mats.floor,0,.025,0,128);ring(root,18.5,.035,mats.steel,0,.1,0);ring(root,18.78,.026,mats.light,0,-.17,0);
 // Quiet mineral circulation ring, inset brass guidance and radial expansion joints.
 cylinder(root,7.9,7.9,.13,mats.stone,0,.12,0,128);ring(root,7.87,.018,mats.light,0,.2,0);ring(root,5.3,.018,mats.steel,0,.201,0);
 for(let i=0;i<40;i++){const angle=i*Math.PI/20;const line=box(root,.016,.008,2.1,mats.steel,Math.sin(angle)*6.55,.204,Math.cos(angle)*6.55,0);line.rotation.y=angle;}
 // Raised horseshoe terrace and layered curved facade. The front is an open cutaway.
 const shape=new T.Shape();shape.absarc(0,0,17.9,0,Math.PI,false);shape.absarc(0,0,9.7,Math.PI,0,true);const slab=new T.ExtrudeGeometry(shape,{depth:.85,bevelEnabled:false,curveSegments:96});slab.rotateX(-Math.PI/2);mesh(root,slab,mats.stone,0,.15,0);
 for(let i=0;i<30;i++){const a=Math.PI*.5+i*Math.PI/29,rr=17.7,x=Math.sin(a)*rr,z=Math.cos(a)*rr;const bay=new T.Group();bay.position.set(x,0,z);bay.rotation.y=a;root.add(bay);box(bay,1.65,5.3,.3,mats.blue,0,3.3,0);box(bay,1.45,3.6,.09,mats.glass,0,3.6,.18);box(bay,.055,5.2,.09,mats.steel,-.81,3.3,.22);if(i%3===0)box(bay,.035,3.3,.035,mats.light,-.72,3.6,.28);}
 arc(root,17.15,18.2,.32,Math.PI/2,Math.PI,mats.blue,5.95);arc(root,17.14,17.3,.035,Math.PI/2,Math.PI,mats.light,5.93);
 // Architectural buttresses and overhead bridges draw sightlines to the atrium.
 for(const sign of [-1,1]){for(const z of [-9,0]){box(root,.38,5.9,.48,mats.steel,sign*15.5,3,z);const beam=box(root,7,.3,.5,mats.blue,sign*12.2,5.8,z);beam.rotation.z=sign*.055;box(root,6.8,.035,.08,mats.light,sign*12.2,5.65,z+.24);}
 for(let i=0;i<6;i++){box(root,3.6,.14,.4,mats.stone,sign*8.5,.21+i*.14,-6.7-i*.43);box(root,3.6,.023,.035,mats.light,sign*8.5,.29+i*.14,-6.51-i*.43);}}
 // Rear mezzanine, transparent rail and slender access stair.
 box(root,14,.26,2,mats.blue,0,3.85,-14.5,.15);box(root,13.8,.035,.04,mats.light,0,3.72,-13.51);box(root,13.9,.85,.045,mats.glass,0,4.38,-13.55);box(root,14,.04,.045,mats.steel,0,4.83,-13.55);
 for(let i=0;i<15;i++){box(root,1.4,.16,.35,mats.steel,-8.3,1.07+i*.19,-10.5-i*.3);}
 for(const x of [-6,0,6])box(root,.18,3.8,.18,mats.steel,x,2,-15.2);
 // Roof blades imply a building without obscuring the diorama.
 for(let i=0;i<7;i++){const x=(i-3)*2.1;box(root,1.6,.15,3,mats.blue,x,6.45,-15.1);box(root,.025,.025,2.9,mats.dim,x-.65,6.36,-15.1);}
 for(const zone of ZONES){const g=new T.Group();g.position.set(zone.x,zone.y,zone.z);g.rotation.y=zone.angle;root.add(g);box(g,4.75,.18,4.3,zone.type==='library'?mats.wood:mats.blue,0,-.14,0,.38);box(g,4.1,.025,.035,mats.light,0,-.035,2.08);equipment(g,zone.type);if(zone.type!=='table')workstation(g);
 const sign=textPanel(g,zone.name,zone.sub,3.6,.84,0,2.98,-1.65);box(g,3.72,.96,.075,mats.steel,0,2.98,-1.7,.04);
 // Low side partition in translucent smoked glass.
 box(g,.045,1.1,2.4,mats.glass,-2.22,.55,-.25);box(g,.04,.035,2.4,mats.steel,-2.22,1.12,-.25);
 }
 // Central containment column: mineral podium, six load-bearing fins, glass chamber,
 // stacked experimental cartridge and secondary containment rings.
 const core=new T.Group();root.add(core);cylinder(core,2.45,2.7,.28,mats.stone,0,.3,0,96);cylinder(core,2.05,2.3,.32,mats.blue,0,.6,0,96);ring(core,2.07,.025,mats.light,0,.77,0);
 cylinder(core,1.3,1.65,.42,mats.steel,0,.95,0);cylinder(core,1.25,1.25,4.55,mats.glass,0,3.35,0,64);
 const energyMaterial=mat('#bd9b6e',.4,.6,{emissive:'#c78a3e',emissiveIntensity:.13});const cartridge=new T.Group();core.add(cartridge);
 cylinder(cartridge,.42,.55,3.7,energyMaterial,0,3.25,0);for(let i=0;i<12;i++){cylinder(cartridge,.63,.63,.09,mats.steel,0,1.55+i*.3,0);ring(cartridge,.48,.014,energyMaterial,0,1.7+i*.3,0);}
 for(let i=0;i<6;i++){const a=i*Math.PI/3,x=Math.sin(a)*1.52,z=Math.cos(a)*1.52;const fin=box(core,.15,4.8,.32,mats.steel,x,3.24,z);fin.rotation.y=a;box(core,.025,4.05,.025,mats.dim,x*1.02,3.24,z*1.02);}
 for(const y of [1.15,2.25,4.45,5.65]){ring(core,1.54,.11,mats.blue,0,y,0);ring(core,1.56,.025,mats.steel,0,y+.12,0);}
 cylinder(core,1.66,1.34,.3,mats.blue,0,5.73,0);cylinder(core,.78,1.6,.23,mats.steel,0,5.98,0);const activeRing=ring(core,1.2,.025,energyMaterial,0,3.5,0);
 const coreLight=new T.PointLight('#ffb95f',0,11,2);coreLight.position.set(0,3,0);root.add(coreLight);
 // Physical practical lights illuminate stations and circulation; never state indicators.
 for(const [x,z] of [[-10,-6],[9,-7],[-11,4],[10,5],[-3,10]]){const light=new T.PointLight('#ffd6a0',24,10,2);light.position.set(x,4.6,z);scene.add(light);}
 const overhead=new T.DirectionalLight('#d3e2f2',3.4);overhead.position.set(-10,24,15);overhead.castShadow=true;overhead.shadow.mapSize.set(2048,2048);Object.assign(overhead.shadow.camera,{left:-23,right:23,top:23,bottom:-23,near:1,far:65});overhead.shadow.normalBias=.04;overhead.shadow.bias=-.0003;scene.add(overhead);
 scene.add(new T.HemisphereLight('#adcbeb','#303543',2));const rim=new T.DirectionalLight('#9ab4c9',2.6);rim.position.set(8,12,-20);scene.add(rim);
 // Grounding plane is outside the cutaway, with a soft studio-night background.
 mesh(scene,new T.PlaneGeometry(400,400),mat('#0f1d2c',1,0),0,-.8,0).rotation.x=-Math.PI/2;
 return {root,core,cartridge,energyMaterial,coreLight,activeRing};
}

function ellipsoid(p,rx,ry,rz,m,x,y,z){const o=mesh(p,geo('bodySphere',()=>new T.SphereGeometry(1,16,12)),m,x,y,z);o.scale.set(rx,ry,rz);return o;}
function limb(p,a,b,r1,r2,m){const v1=new T.Vector3(...a),v2=new T.Vector3(...b),d=v2.clone().sub(v1);const o=cylinder(p,r1,r2,d.length(),m,...v1.clone().add(v2).multiplyScalar(.5).toArray(),12);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return o;}
export function buildHumanoid(parent,index=0){
 const g=new T.Group();parent.add(g);const skin=mat(['#b7957b','#8f6954','#c9ad93'][index%3],.83,0),suit=mat(['#94a0a5','#657c91','#8a8173'][index%3],.9,.03),trousers=mat('#263543',.91,0),hair=mat('#33312e',.98,0);
 // Adult: 7.5 head heights, narrow neck and articulated limbs, tailored jacket.
 ellipsoid(g,.215,.31,.135,suit,0,1.15,0);ellipsoid(g,.19,.13,.13,trousers,0,.9,0);
 cylinder(g,.066,.075,.12,skin,0,1.48,0,16);ellipsoid(g,.112,.145,.105,skin,0,1.64,0);ellipsoid(g,.116,.08,.11,hair,0,1.73,-.015);
 ellipsoid(g,.026,.043,.028,skin,-.116,1.64,0);ellipsoid(g,.026,.043,.028,skin,.116,1.64,0);
 box(g,.016,.012,.008,trousers,-.038,1.655,.096,0);box(g,.016,.012,.008,trousers,.038,1.655,.096,0);
 box(g,.025,.21,.012,mats.steel,0,1.22,.128,0);box(g,.055,.035,.016,mats.dim,.12,1.29,.127,0);
 for(const side of [-1,1]){limb(g,[side*.12,.88,0],[side*.13,.5,.015],.085,.065,trousers);limb(g,[side*.13,.5,.015],[side*.14,.13,.025],.065,.045,trousers);ellipsoid(g,.07,.065,.14,hair,side*.14,.075,.085);}
 const arms=[];for(const side of [-1,1]){const shoulder=new T.Group();shoulder.position.set(side*.23,1.36,0);g.add(shoulder);limb(shoulder,[0,0,0],[side*.045,-.27,0],.073,.055,suit);const forearm=new T.Group();forearm.position.set(side*.045,-.27,0);shoulder.add(forearm);limb(forearm,[0,0,0],[0,-.26,.025],.052,.034,suit);ellipsoid(forearm,.04,.07,.028,skin,0,-.31,.03);arms.push({shoulder,forearm});}
 const document=box(g,.27,.015,.36,mats.paper,0,1.02,.4);document.visible=false;
 return {group:g,arms,document,phase:0};
}
