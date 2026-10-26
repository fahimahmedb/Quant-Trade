import * as T from './vendor/three.js';
import {ZONES} from './layout.js';
export {ZONES} from './layout.js';
export {buildHumanoid} from './characters.js';

// Fictional architecture and instruments only. No object here represents work,
// progress, an economic conclusion or a live role.
export const mats={};
const geometries=new Map();
const cached=(key,make)=>{if(!geometries.has(key))geometries.set(key,make());return geometries.get(key);};
const material=(color,roughness=.6,metalness=.15,extra={})=>new T.MeshStandardMaterial({color,roughness,metalness,...extra});
function mesh(p,g,m,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;p.add(o);return o;}
export function box(p,w,h,d,m,x=0,y=0,z=0,r=.025){const radius=Math.min(r,w/4,h/4,d/4);return mesh(p,cached(`b${w},${h},${d},${radius}`,()=>radius>0?new T.RoundedBoxGeometry(w,h,d,2,radius):new T.BoxGeometry(w,h,d)),m,x,y,z);}
export function cylinder(p,rt,rb,h,m,x=0,y=0,z=0,n=40){return mesh(p,cached(`c${rt},${rb},${h},${n}`,()=>new T.CylinderGeometry(rt,rb,h,n)),m,x,y,z);}
function sphere(p,rx,ry,rz,m,x,y,z){const o=mesh(p,cached('sphere',()=>new T.SphereGeometry(1,20,14)),m,x,y,z);o.scale.set(rx,ry,rz);return o;}
function ring(p,r,t,m,x,y,z){const o=mesh(p,cached(`r${r},${t}`,()=>new T.TorusGeometry(r,t,8,96)),m,x,y,z);o.rotation.x=Math.PI/2;return o;}
function group(p,x=0,y=0,z=0,angle=0){const g=new T.Group();g.position.set(x,y,z);g.rotation.y=angle;p.add(g);return g;}
function tube(p,points,r,m,segments=24){return mesh(p,new T.TubeGeometry(new T.CatmullRomCurve3(points.map(v=>new T.Vector3(...v))),segments,r,6,false),m);}
function slab(p,outline,y,h,m){const shape=new T.Shape(outline.map(([x,z])=>new T.Vector2(x,-z)));const geo=new T.ExtrudeGeometry(shape,{depth:h,bevelEnabled:true,bevelSize:.035,bevelThickness:.035,bevelSegments:2,curveSegments:32});geo.rotateX(-Math.PI/2);return mesh(p,geo,m,0,y,0);}
function annulus(p,r1,r2,y,h,start,length,m){const pts=[];for(let i=0;i<=64;i++){const a=start+length*i/64;pts.push([Math.sin(a)*r2,Math.cos(a)*r2]);}for(let i=64;i>=0;i--){const a=start+length*i/64;pts.push([Math.sin(a)*r1,Math.cos(a)*r1]);}return slab(p,pts,y,h,m);}
function canvasTexture(draw,w=1024,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;draw(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;return t;}
const textures=new Map();
function illustration(type='system'){if(textures.has(type))return textures.get(type);const t=canvasTexture((c,W,H)=>{
 c.fillStyle='#102331';c.fillRect(0,0,W,H);c.strokeStyle='#456375';c.lineWidth=2;c.fillStyle='#9aafba';c.font='21px monospace';c.fillText('RESEARCH OS / SPATIAL INDEX',36,42);c.fillStyle='#708898';c.font='16px monospace';c.fillText('ARCHITECTURAL SCHEMATIC · NON-DATA',36,H-25);
 c.save();c.translate(W*.53,H*.51);c.scale(1,.65);for(const r of [72,118,172]){c.beginPath();c.arc(0,0,r,0,Math.PI*2);c.stroke();}for(let i=0;i<12;i++){const a=i*Math.PI/6;c.save();c.rotate(a);c.strokeRect(182,-25,55,50);c.beginPath();c.moveTo(118,0);c.lineTo(182,0);c.stroke();c.restore();}c.strokeStyle='#b29365';c.strokeRect(-24,-90,48,180);c.restore();
 },1024,512);textures.set(type,t);return t;}
function sign(p,name,sub,x,y,z,w=3.2,h=.45){const texture=canvasTexture((c,W,H)=>{c.fillStyle='#132b3d';c.fillRect(0,0,W,H);c.fillStyle='#bf9d68';c.fillRect(36,70,4,210);c.fillStyle='#e0d4bc';c.font='500 42px sans-serif';c.fillText(name,65,190);c.fillStyle='#7893a7';c.font='23px monospace';c.fillText(sub,65,278);});box(p,w+.08,h+.08,.08,mats.navy,x,y,z-.05);return mesh(p,new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:texture}),x,y,z);}
function screen(p,x,y,z,w=1.15,h=.66,angle=0){const g=group(p,x,y,z,angle);box(g,w+.055,h+.055,.055,mats.alloy);mesh(g,new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:illustration()}),0,0,.031);return g;}
function lamp(p,x,y,z,length=2.2){box(p,length,.065,.17,mats.brass,x,y,z);box(p,length-.10,.014,.105,mats.warm,x,y-.038,z);for(const s of [-1,1])cylinder(p,.007,.007,1.45,mats.dark,x+s*(length/2-.17),y+.75,z,8);}
function chair(p,x,z,angle=0){const g=group(p,x,0,z,angle);const c=box(g,.57,.12,.56,mats.textile,0,.53,0,.09);box(g,.59,.61,.095,mats.textile,0,.86,.245,.055);box(g,.45,.41,.025,mats.navy,0,.84,.302,.035);cylinder(g,.038,.045,.4,mats.alloy,0,.28,0,16);for(let i=0;i<5;i++){const a=i*Math.PI*.4,b=group(g,0,.08,0,a);box(b,.04,.035,.4,mats.alloy,0,0,.17,.01);sphere(b,.033,.033,.048,mats.dark,0,-.02,.35);}for(const s of [-1,1]){box(g,.023,.30,.023,mats.alloy,s*.29,.68,.02);box(g,.055,.04,.31,mats.textile,s*.29,.85,.025,.018);}return g;}
function notebook(p,x,y,z,angle=0){const g=group(p,x,y,z,angle);box(g,.32,.035,.43,mats.folio,0,0,0,.012);box(g,.29,.022,.40,mats.paper,0,.015,0,.006);box(g,.014,.006,.36,mats.brass,-.13,.029,0);}
function taskLight(p,x,z){const g=group(p,x,1.01,z);cylinder(g,.12,.15,.035,mats.alloy);tube(g,[[0,0,0],[0,.45,-.03],[.12,.63,-.12],[.33,.59,-.12]],.016,mats.alloy);box(g,.31,.045,.12,mats.navy,.30,.60,-.12);box(g,.27,.008,.085,mats.warm,.30,.575,-.12);}
export function workstation(p,kind='research'){
 // A cantilevered cabinet, thin timber worktop, actual armatures and organized cable runs.
 box(p,2.8,.105,1.02,mats.timber,0,.96,.15,.055);box(p,2.72,.035,.93,mats.dark,0,.893,.15,.02);box(p,.55,.78,.81,mats.navy,1,.465,.15,.05);
 for(let j=0;j<3;j++){box(p,.48,.16,.025,mats.mineral,1,.34+j*.2,.57,.018);box(p,.11,.013,.028,mats.brass,1,.34+j*.2,.588);}
 box(p,.08,.86,.66,mats.alloy,-1.12,.47,.15);box(p,.44,.035,.76,mats.dark,-1.12,.055,.15);
 for(const [x,a,w] of [[-.36,.05,1.03],[.66,-.24,.70]]){cylinder(p,.02,.02,.4,mats.alloy,x,1.18,-.12,12);screen(p,x,1.49,-.13,w,w*.59,a);}
 box(p,.58,.018,.22,mats.keypad,-.25,1.023,.47,.014);for(let i=0;i<5;i++)box(p,.52,.004,.013,mats.alloy,-.25,1.035,.38+i*.04,0);
 sphere(p,.045,.016,.07,mats.alloy,.22,1.04,.48);notebook(p,-.99,1.025,.30,-.12);taskLight(p,-1.15,-.18);
 cylinder(p,.066,.058,.13,mats.ceramic,1.18,1.08,.38,20);cylinder(p,.052,.052,.006,mats.dark,1.18,1.148,.38,20);const handle=ring(p,.035,.009,mats.ceramic,1.25,1.083,.38);handle.rotation.x=0;
 tube(p,[[-.36,1.22,-.17],[-.36,.85,-.21],[-.65,.60,-.21],[-1.05,.12,-.08]],.012,mats.dark);
 chair(p,0,1.2);if(kind==='engineering')instrument(p,1.8,.3);
}
function books(p,w=5.5,rows=5,height=3.3){box(p,w+.2,height,.45,mats.timber,0,height/2,-.15,.04);for(let row=0;row<rows;row++){const yy=.18+row*(height-.3)/rows;box(p,w,.045,.57,mats.alloy,0,yy,.02);for(let i=0;i<Math.floor(w/.13)-1;i++){const seed=(i*37+row*17)%101,h=.26+seed/600,ww=.055+(seed%4)*.017;const b=box(p,ww,h,.23,[mats.paper,mats.folio,mats.bookBlue,mats.bookRed,mats.timber][seed%5],-w/2+.1+i*.13,yy+.04+h/2,.05,.006);if(seed%9===0)b.rotation.z=.12;box(p,ww*.6,.012,.004,mats.brass,-w/2+.1+i*.13,yy+h*.7,.169,0);}}}
function instrument(p,x,z){const g=group(p,x,0,z);box(g,.65,.82,.65,mats.navy,0,.42,0,.08);box(g,.52,.045,.53,mats.alloy,0,.85,0);cylinder(g,.17,.22,.19,mats.alloy,0,.96,0);cylinder(g,.155,.155,.54,mats.glass,0,1.30,0);ring(g,.17,.012,mats.warm,0,1.04,0);ring(g,.17,.018,mats.brass,0,1.58,0);for(let i=0;i<3;i++)cylinder(g,.028,.028,.45,mats.steel,(i-1)*.08,1.29,0,12);}
function cart(p,x,z,angle=0){const g=group(p,x,0,z,angle);for(const y of [.2,.67])box(g,.8,.045,.48,mats.alloy,0,y,0,.03);for(const xx of [-.36,.36])for(const zz of [-.19,.19]){cylinder(g,.016,.016,.68,mats.steel,xx,.4,zz,8);sphere(g,.046,.046,.025,mats.dark,xx,.10,zz);}for(let i=0;i<3;i++)box(g,.32,.045,.40,mats.paper,(i%2)*.33-.16,.74+Math.floor(i/2)*.05,0);}
function rail(p,points,y=0){const q=points.map(([x,z])=>[x,y+1.05,z]);tube(p,q,.018,mats.brass);for(const [x,z]of points)cylinder(p,.012,.012,1,mats.alloy,x,y+.55,z,8);}
function steps(p,x,z,w,count,rise,depth,angle=0){const g=group(p,x,0,z,angle);for(let i=0;i<count;i++){box(g,w,(i+1)*rise,depth,mats.mineral,0,(i+1)*rise/2,-i*depth,.015);box(g,w-.14,.008,.018,mats.warm,0,(i+1)*rise+.015,-i*depth+depth/2-.02);}return g;}
function ribs(p,z,high=11){const pts=[];for(let i=0;i<=20;i++){const x=-17+34*i/20;pts.push([x,1+high*Math.sqrt(Math.max(0,1-(x/18.2)**2)),z]);}tube(p,pts,.18,mats.navy,48);tube(p,pts.map(v=>[v[0],v[1]-.19,v[2]+.04]),.027,mats.warm,48);}
function wallPanel(p,x,y,z,w,h,m){return box(p,w,h,.16,m,x,y,z,.035);}
function library(root){
 const g=group(root,-12,.8,-10.6);books(g,6.4,7,5.2);lamp(g,0,5.4,.12,5.6);const b=group(root,-16.25,.8,-6,Math.PI/2);books(b,9.1,7,5.2);
 slab(root,[[-17,-17],[-5,-17],[-5,-10],[-8,-8],[-17,-8]],3.6,.18,mats.timber);
 rail(root,[[-16.8,-8],[-8,-8],[-5,-10],[-5,-16.5]],3.8);box(root,11.9,.035,.06,mats.warm,-11,3.55,-8);
 for(const x of [-16.2,-6]){box(root,.16,3.1,.16,mats.navy,x,2.2,-8.5);box(root,.35,.08,.35,mats.brass,x,.85,-8.5);}
 const upper=group(root,-11,3.8,-16);books(upper,9.5,4,2.4);lamp(upper,0,2.7,.1,8.5);
 steps(root,-5.9,-5.5,1.65,18,.207,.29);rail(root,[[-5,-5.5],[-5,-10.8]],.85);
 sign(root,'RESEARCH LIBRARY','MECHANISMS / SOURCE MEMORY',-12,6.9,-16.2,5,.62);
 // A quiet upper reading alcove with a long table and task lights.
 const table=group(root,-10,3.8,-12.1);box(table,5.4,.10,1.25,mats.timber,0,.94,0,.06);for(const x of [-2,2])box(table,.09,.9,.83,mats.alloy,x,.46,0);for(let i=0;i<4;i++){notebook(table,-1.8+i*1.2,1.02,0,.1);chair(table,-1.8+i*1.2,1,0);}cart(table,-3.2,.2);
}
function archiveZone(g){books(group(g,0,0,-1.8),4.4,4,2.5);for(const x of [-1.6,-.5,.6,1.7]){box(g,.88,.75,.73,mats.mineral,x,.4,.4,.05);for(let j=0;j<5;j++){box(g,.74,.10,.025,mats.folio,x,.20+j*.125,.78,.012);box(g,.22,.035,.01,mats.paper,x,.20+j*.125,.798);}}cart(g,-2.7,.8);sign(g,'EDGE ARCHAEOLOGY','DURABLE MEMORY / DECAY',0,2.87,-1.76,3.7,.43);lamp(g,0,3.3,0,3.8);}
function dataZone(g){const b=group(g,-2,0,-1.1,Math.PI*.15);for(let i=0;i<3;i++){box(b,.66,2.4,.68,mats.navy,i*.76,1.2,0,.045);for(let j=0;j<8;j++){box(b,.55,.17,.03,mats.alloy,i*.76,.26+j*.26,.36);box(b,.018,.018,.012,mats.warm,i*.76+.19,.26+j*.26,.385,0);}}workstation(g);const side=group(g,2.8,0,-.3,-.25);box(side,.8,1.5,.55,mats.steel,0,.75,0);for(let i=0;i<5;i++){box(side,.70,.22,.035,mats.paper,0,.20+i*.28,.30);box(side,.25,.04,.015,mats.folio,0,.20+i*.28,.325);}sign(g,'DATA / EVIDENCE','PROVENANCE / QUALIFICATION',0,3.05,-1.52,3.8,.46);}
function validationZone(g){
 // Curved smoked-glass enclosure with exposed brass cap and solid mineral base.
 annulus(g,3.15,3.22,0,.4,-2.2,2.8,mats.mineral);const pts=[];for(let i=0;i<24;i++){const a=-2.2+2.8*i/23;pts.push([Math.sin(a)*3.18,Math.cos(a)*3.18]);const fin=box(g,.027,2.8,.04,mats.alloy,Math.sin(a)*3.18,1.65,Math.cos(a)*3.18);fin.rotation.y=a;}
 const glass=new T.CylinderGeometry(3.18,3.18,2.65,64,1,true,-2.2,2.8);mesh(g,glass,mats.glass,0,1.73,0);rail(g,pts,2.1);
 workstation(g);const side=group(g,-2.1,0,-1,.38);screen(side,0,1.55,0,1.6,1);cylinder(side,.035,.035,1.4,mats.steel,0,.75,0);box(side,.7,.04,.5,mats.dark,0,.08,0);cart(g,2,.5);
 sign(g,'VALIDATION / RED TEAM','INDEPENDENT CHALLENGE',0,3.3,-2.7,4,.52);lamp(g,0,3.8,-.3,3.5);
}
function infrastructure(g){for(let i=0;i<4;i++){const x=(i-1.5)*.86;box(g,.79,3.0,.95,mats.navy,x,1.52,0,.06);box(g,.67,2.76,.035,mats.rackFace,x,1.53,.51);for(let j=0;j<11;j++){box(g,.60,.16,.025,mats.steel,x,.28+j*.23,.54,.01);for(let k=0;k<4;k++)box(g,.025,.008,.012,k===0?mats.warm:mats.dim,x-.22+k*.12,.28+j*.23,.56,0);}tube(g,[[x,.1,-.48],[x,3.4,-.6],[x,3.7,-.2],[x+1,3.8,.2]],.025,mats.dark);}
 box(g,4.2,.17,1.6,mats.alloy,0,3.47,0);for(let i=0;i<14;i++)box(g,.025,.12,1.4,mats.dark,-1.9+i*.29,3.59,0);lamp(g,0,3.8,.5,3.7);sign(g,'EXPERIMENT SYSTEMS','INSTRUMENT / INFRASTRUCTURE',0,4.15,.05,3.9,.42);
}
function engineering(g){workstation(g,'engineering');const bench=group(g,0,0,-2.6);box(bench,4.8,.18,1,mats.steel,0,.96,0,.05);for(const x of [-1.8,1.8])box(bench,.55,.88,.8,mats.navy,x,.46,0);for(let i=0;i<5;i++){const x=(i-2)*.73;box(bench,.62,.48,.55,mats.mineral,x,1.3,-.13);for(let j=0;j<4;j++)cylinder(bench,.027,.027,.025,mats.brass,x-.18+j*.12,1.36,.17,12);box(bench,.4,.11,.012,mats.dim,x,1.53,.17);}
 const arm=group(g,-2.2,0,-.3);cylinder(arm,.24,.32,.26,mats.steel,0,1.17,0);tube(arm,[[0,1.29,0],[0,1.9,0],[.4,2.2,0],[.73,1.96,.1]],.065,mats.mineral);sphere(arm,.12,.12,.12,mats.brass,0,1.9,0);box(arm,.22,.15,.15,mats.alloy,.75,1.9,.1);cart(g,-2.6,1.5);lamp(g,0,3.65,-.5,4.4);sign(g,'IMPLEMENTABILITY','ENGINEERING / BUILD',0,3.14,-2.9,4.5,.45);
}
function seminar(g){annulus(g,1.7,3.2,0,.18,-1.4,2.8,mats.timber);annulus(g,2.55,3.45,.18,.18,-1.4,2.8,mats.timber);for(let i=0;i<6;i++){const a=-1.1+i*.44,seat=group(g,Math.sin(a)*2.8,.38,Math.cos(a)*2.8,a+Math.PI);box(seat,.72,.1,.48,mats.textile,0,.25,0,.07);box(seat,.72,.45,.07,mats.textile,0,.48,.2,.025);}cylinder(g,1.18,1.18,.10,mats.timber,0,.85,0,64);cylinder(g,.35,.55,.75,mats.navy,0,.45,0);notebook(g,0,.93,0);sign(g,'FUNDAMENTAL','RESEARCH / PRIMARY SOURCES',0,3,-3,3.6,.42);}
function portfolio(g){const t=cylinder(g,2.3,2.3,.14,mats.timber,0,.89,0,96);t.scale.z=.58;const under=cylinder(g,1.9,2,.5,mats.navy,0,.5,0);under.scale.z=.48;const plane=mesh(g,new T.PlaneGeometry(3.4,1.7),new T.MeshBasicMaterial({map:illustration('table')}),0,.97,0);plane.rotation.x=-Math.PI/2;for(let i=0;i<7;i++){const a=i*1.3;cylinder(g,.05,.08,.11,mats.brass,Math.sin(a)*1.4,1.03,Math.cos(a)*.6,16);}for(const x of [-1.4,0,1.4])chair(g,x,1.75);sign(g,'PORTFOLIO / INTEGRATION','SYSTEM ARCHITECTURE · NON-DATA',0,1.55,-1.1,3,.39);}
function identity(g){workstation(g);instrument(g,1.95,-.5);instrument(g,-1.9,-.8);const rack=group(g,0,0,-1.8);box(rack,3.5,.75,.5,mats.navy,0,.4,0);for(let j=0;j<6;j++){cylinder(rack,.055,.055,.42,mats.steel,-1.3+j*.52,.99,0,16);ring(rack,.08,.012,mats.brass,-1.3+j*.52,1.24,0);}sign(g,'ECONOMIC IDENTITY','RESEARCH / INTEGRATION',0,2.30,-1.8,3.6,.44);lamp(g,0,3.6,-.2,3.2);}
function core(root){const g=group(root,0,.3,-.4);cylinder(g,3.25,3.4,.18,mats.mineral,0,.1,0,96);cylinder(g,2.7,3.1,.24,mats.navy,0,.31,0,96);ring(g,2.82,.018,mats.warm,0,.44,0);cylinder(g,1.7,2.25,.42,mats.steel,0,.64,0,64);cylinder(g,1.22,1.5,.22,mats.alloy,0,.93,0);
 const energyMaterial=material('#8a764f',.27,.62,{emissive:'#d49b4d',emissiveIntensity:.14}),cartridge=group(g);
 cylinder(cartridge,.30,.46,5.7,energyMaterial,0,3.9,0);for(let i=0;i<18;i++){const y=1.3+i*.32;cylinder(cartridge,.49,.49,.065,mats.alloy,0,y,0);ring(cartridge,.37,.018,energyMaterial,0,y+.09,0);}
 // Machined containment with six curved fins, inspection windows and cable housings.
 for(let i=0;i<6;i++){const a=i*Math.PI/3,x=Math.sin(a),z=Math.cos(a);tube(g,[[x*1.7,.87,z*1.7],[x*1.87,2,z*1.87],[x*1.7,5.8,z*1.7],[x*1.15,7.2,z*1.15]],.075,mats.brass,32);tube(g,[[x*1.5,1,z*1.5],[x*1.5,5.8,z*1.5],[x*1,7.1,z]],.025,mats.alloy,24);const fin=box(g,.09,4.2,.25,mats.navy,x*1.63,3.6,z*1.63);fin.rotation.y=a;}
 cylinder(g,1.28,1.28,5.7,mats.glass,0,3.9,0,64);for(const y of [1.12,2.9,5.65,6.8]){ring(g,1.44,.10,mats.navy,0,y,0);ring(g,1.46,.018,mats.brass,0,y+.11,0);}
 cylinder(g,1.2,1.65,.35,mats.navy,0,7.02,0,64);cylinder(g,.65,1.20,.34,mats.alloy,0,7.35,0,64);ring(g,1.12,.018,mats.dim,0,7.18,0);const activeRing=ring(g,.91,.015,energyMaterial,0,4.4,0);
 // Overhead toroidal service crown is fixed architecture, never an activity claim.
 annulus(g,3.2,3.8,8.2,.15,0,Math.PI*2,mats.navy);ring(g,3.24,.022,mats.warm,0,8.19,0);for(let i=0;i<8;i++){const a=i*Math.PI/4;tube(g,[[Math.sin(a)*3.5,8.3,Math.cos(a)*3.5],[Math.sin(a)*4.1,10,Math.cos(a)*4.1]],.012,mats.alloy,8);}
 for(let i=0;i<3;i++){const a=i*Math.PI*2/3+.5,k=group(root,Math.sin(a)*4.7,.3,-.4+Math.cos(a)*4.7,a);box(k,.65,.96,.54,mats.navy,0,.48,0,.08);screen(k,0,1.04,.02,.58,.35);box(k,.55,.015,.03,mats.warm,0,.88,.28);}
 const coreLight=new T.PointLight('#ffb05a',0,14,2);coreLight.position.set(0,4,-.4);root.add(coreLight);return{core:g,cartridge,activeRing,energyMaterial,coreLight};}
export function buildArchitecture(scene){
 Object.assign(mats,{navy:material('#13283d',.47,.5),dark:material('#17222d',.68,.25),steel:material('#465969',.40,.8),alloy:material('#9aa8ac',.29,.73),brass:material('#9d7446',.33,.7),mineral:material('#536976',.84,.05),floor:material('#606e76',.8,.05),timber:material('#6b6158',.72,.05),textile:material('#536b79',.97,0),folio:material('#5c5142',.9,0),paper:material('#c9c2ad',.92,0),bookBlue:material('#39516a',.86,.05),bookRed:material('#77534a',.9,0),ceramic:material('#d0c6b2',.45,.02),keypad:material('#293c4b',.95,0),rackFace:material('#24313b',.8,.2),glass:material('#6e9cab',.14,.1,{transparent:true,opacity:.15,depthWrite:false,side:T.DoubleSide}),warm:material('#cb964d',.5,.2,{emissive:'#ffb459',emissiveIntensity:1.65}),dim:material('#748d9c',.5,.35,{emissive:'#8ba8bb',emissiveIntensity:.25})});
 const load=new T.TextureLoader(),tex=(name,color=false,repeat=1)=>{const t=load.load(new URL(`../assets/materials/${name}`,import.meta.url).href,()=>scene.userData.materialsChanged=true);t.colorSpace=color?T.SRGBColorSpace:T.NoColorSpace;t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(repeat,repeat);t.anisotropy=4;return t;};
 mats.timber.map=tex('oak-color.jpg',true,1);mats.timber.bumpMap=tex('oak-bump.jpg');mats.timber.bumpScale=.013;mats.timber.roughnessMap=tex('oak-roughness.jpg');
 mats.floor.map=tex('mineral-color.jpg',true,.5);mats.floor.normalMap=tex('mineral-normal.jpg',false,.5);mats.floor.normalScale.set(.09,.09);mats.floor.roughness=.82;
 const root=group(scene);const outline=[[-16,-19],[15,-19],[18,-15],[18,8],[12,14],[-11,14],[-18,8],[-18,-15]];slab(root,outline,-.55,.65,mats.navy);slab(root,outline,.10,.18,mats.floor);
 // Cutaway edge: mineral-over-metal reveals an actual building thickness.
 for(const x of [-14,-9,-4,1,6,11])box(root,2.3,.012,.026,mats.brass,x,.305,12.5);
 slab(root,[[-17.2,-18],[-3,-18],[-3,-10],[-6,-6],[-6,4.7],[-17.2,4.7]],.3,.5,mats.floor);
 slab(root,[[5,-18],[16.8,-18],[17,-3],[6.5,-3],[6.5,-9],[5,-11]],.3,.5,mats.floor);
 annulus(root,5.8,7.1,.29,.035,0,Math.PI*2,mats.dark);ring(root,5.78,.013,mats.brass,0,.34,-.4);ring(root,7.13,.013,mats.brass,0,.34,-.4);
 for(let i=0;i<24;i++){const a=i*Math.PI/12,g=group(root,Math.sin(a)*6.44,.34,-.4+Math.cos(a)*6.44,a);box(g,.018,.008,1.1,mats.alloy);}
 steps(root,-6.8,5.4,3.4,3,.17,.38);steps(root,7.7,-2.5,3.1,3,.17,.38,Math.PI);
 // Back elevation: double-height glazing, massive piers, warm reveals and a distant campus.
 for(let i=0;i<10;i++){const x=-16+i*3.55;box(root,.25,10.3,.32,mats.navy,x,5.7,-18.15);box(root,.038,9.3,.03,mats.brass,x+.16,5.8,-17.95);wallPanel(root,x+1.7,6.0,-18.25,3.1,8.3,mats.glass);}
 box(root,34.5,.32,.55,mats.navy,0,10.9,-18.1);box(root,34,.025,.06,mats.warm,0,10.69,-17.82);box(root,34,.12,.2,mats.alloy,0,3.8,-18);
 // Architectural background has no screens or activity: fixed night-campus silhouettes.
 const campus=group(root,0,-.5,-32);for(let i=0;i<10;i++){const x=(i-4.5)*5,h=5+(i*17%9);box(campus,3.2,h,4,mats.navy,x,h/2,-(i%3)*4,.12);for(let j=0;j<3;j++)box(campus,.018,Math.min(h-1,5),.025,mats.dim,x-1+j*1.1,h/2,2.03);}
 for(const side of [-1,1]){for(const z of [-14,-6,2]){box(root,.54,8.1,.66,mats.mineral,side*17.2,4.8,z,.08);box(root,.12,6.8,.7,mats.navy,side*17.2,4.9,z);box(root,.025,5.5,.035,mats.warm,side*17.2-side*.3,4.9,z+.3);}tube(root,[[side*17.3,1,-17],[side*17.3,10.2,-17],[side*16,11.8,-10],[side*14,11.9,-2],[side*14,10,5]],.2,mats.navy,40);}
 ribs(root,-14,10.4);ribs(root,-6,10.1);ribs(root,2,9.5);
 // A continuous mineral back wall grounds the glazing and frames technical niches.
 for(const x of [-13,-5,3,11]){box(root,7.5,2.3,.48,mats.navy,x,1.95,-18.1,.08);box(root,7.3,.07,.12,mats.alloy,x,3.14,-17.78);}
 // The cutaway roof retains two broad curved ribbons and visible soffits.
 for(const z of [-14,-6]){const outline=[];for(let j=0;j<=40;j++){const x=-17+34*j/40;outline.push([x,1+10.25*Math.sqrt(Math.max(0,1-(x/18.2)**2)),z]);}
 const pos=[],ind=[];for(let j=0;j<outline.length;j++){const[x,y,zz]=outline[j];pos.push(x,y,zz-.44,x,y,zz+.44);if(j){const n=j*2;ind.push(n-2,n-1,n+1,n-2,n+1,n);}}const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setIndex(ind);geo.computeVertexNormals();const roofMat=mats.navy.clone();roofMat.side=T.DoubleSide;mesh(root,geo,roofMat);
 }
 // Left archive niche: a curved, substantial back with shelves and inset light.
 const archiveBack=group(root,-13,.3,7.9,.6);annulus(archiveBack,3.0,3.3,0,3.05,-2.15,2.0,mats.navy);annulus(archiveBack,2.98,3.35,3.05,.16,-2.15,2.0,mats.timber);annulus(archiveBack,2.98,3.04,2.95,.025,-2.15,2.0,mats.warm);
 // Engineering alcove has a cantilevered equipment canopy and louvered wall.
 const engineeringRoom=group(root,11.5,.3,6,-.75);box(engineeringRoom,5.8,.28,4.7,mats.navy,0,3.78,-.9,.17);box(engineeringRoom,5.4,.035,4.3,mats.mineral,0,3.61,-.9,.08);for(let j=0;j<12;j++)box(engineeringRoom,.025,.035,3.7,mats.alloy,-2.5+j*.45,3.94,-.9);for(const x of [-2.1,2.1])box(engineeringRoom,.09,3.6,.16,mats.alloy,x,1.88,-2.9);for(let j=0;j<10;j++)box(engineeringRoom,.065,2.9,.42,mats.navy,2.9,.3+1.45,-2.75+j*.39);lamp(engineeringRoom,0,3.49,-.4,4.8);
 // Evidence stations sit in an integrated mineral pod, with a timber acoustic canopy.
 const evidenceRoom=group(root,-10,.8,1.5,.65);box(evidenceRoom,.23,2.8,4.1,mats.navy,-3.0,1.4,-.2,.08);box(evidenceRoom,5.9,.20,1.4,mats.timber,-.1,3.12,-1.2,.10);for(let j=0;j<16;j++)box(evidenceRoom,.035,.20,1.35,mats.brass,-2.8+j*.36,3.27,-1.2);lamp(evidenceRoom,0,3,-.3,3.8);
 // Rear suspended bridge with readable landings and glass balustrade.
 box(root,18,.22,1.85,mats.navy,4.4,4.15,-16.2,.06);box(root,17.8,.025,.035,mats.warm,4.4,4.01,-15.26);box(root,17.7,.9,.035,mats.glass,4.4,4.73,-15.35);rail(root,[[-4.4,-15.35],[4.4,-15.35],[13.2,-15.35]],4.3);
 steps(root,14.8,-5,1.5,17,.205,.4);for(let i=0;i<8;i++)box(root,.025,1,.025,mats.alloy,15.5,1.2+i*.41,-5-i*.8);
 library(root);
 // Differentiated operational zones are integrated into this single floor.
 for(const zone of ZONES){if(zone.id==='documents')continue;const g=group(root,zone.x,zone.y,zone.z,zone.angle);
 if(zone.type==='library'){workstation(g);const annex=group(g,2.8,0,-1.6,-.3);box(annex,1.8,.08,.8,mats.timber,0,.9,0);notebook(annex,0,.97,0);lamp(g,0,3.3,-.3,3);}
 if(zone.type==='archive')archiveZone(g);
 if(zone.type==='evidence')dataZone(g);
 if(zone.type==='validation')validationZone(g);
 if(zone.type==='racks')infrastructure(g);
 if(zone.type==='engineering')engineering(g);
 if(zone.type==='seminar')seminar(g);
 if(zone.type==='identity')identity(g);
 if(zone.type==='portfolio')portfolio(g);
 if(zone.type==='maps'){box(g,4.5,.10,.8,mats.timber,0,.94,0);for(const x of [-1.1,1.1]){box(g,.09,.9,.6,mats.alloy,x,.46,0);screen(g,x,1.7,-.1,1.8,1.1,x*-.1);}sign(g,'FLOWS / REGULATORY','CONTEXT / SYSTEM INDEX',0,3,-1,4,.46);lamp(g,0,3.6,-.2,3.5);}
 }
 // Service niches, quiet circulation, technical ceiling and physical greenery.
 for(const side of [-1,1])for(let i=0;i<5;i++){const z=1+i*2.3,x=side*16;box(root,.4,.04,1.6,mats.dark,x,.33,z);for(let j=0;j<11;j++)box(root,.32,.012,.018,mats.alloy,x,.36,z-.65+j*.13,0);}
 for(const [x,z]of [[-15.5,5.5],[15.2,1.5],[-4,-16],[2,10.9]]){cylinder(root,.33,.27,.6,mats.mineral,x,.59,z);for(let i=0;i<7;i++){const a=i*2.4,leaf=sphere(root,.07,.44,.15,material('#334c48',.97,0),x+Math.sin(a)*.16,1.15+(i%3)*.13,z+Math.cos(a)*.16);leaf.rotation.z=Math.sin(a)*.4;}}
 for(let j=0;j<3;j++){const z=-13+j*3.6;for(let i=0;i<7;i++)box(root,.1,.12,2.9,mats.timber,-15+i*.35,7.7,z);}
 const center=core(root);
 // Fewer, larger practical light pools create hierarchy instead of flat global light.
 for(const [x,y,z,intensity]of [[-11,4.2,-5,115],[-11,5.9,-13,90],[10,4.5,-5,105],[11,3.4,6,90],[4,3.3,7,75],[-4,3.7,10,65],[4,5,-14,90]]){const light=new T.PointLight('#ffcb8d',intensity,11,2);light.position.set(x,y,z);root.add(light);}
 const key=new T.DirectionalLight('#a9c7df',2.1);key.position.set(-8,22,10);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-26,right:26,top:26,bottom:-26,near:1,far:85});key.shadow.normalBias=.035;key.shadow.bias=-.00015;key.shadow.radius=3;scene.add(key);
 scene.add(new T.HemisphereLight('#9ab5d0','#26363d',.65));const fill=new T.DirectionalLight('#e5c69d',.45);fill.position.set(14,10,5);scene.add(fill);const rim=new T.DirectionalLight('#7fa6c7',1.1);rim.position.set(0,10,-25);scene.add(rim);
 return{root,...center};
}
