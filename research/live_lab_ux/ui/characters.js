import * as T from './vendor/three.js';
import {HEAD_DATA} from './adult-head.js';
const headGeometry=new T.BufferGeometry();
function typed(s,Type){const b=Uint8Array.from(atob(s),c=>c.charCodeAt(0));return new Type(b.buffer);}
headGeometry.setAttribute('position',new T.BufferAttribute(typed(HEAD_DATA.position,Float32Array),3));headGeometry.setAttribute('normal',new T.BufferAttribute(typed(HEAD_DATA.normal,Float32Array),3));headGeometry.setIndex(new T.BufferAttribute(typed(HEAD_DATA.index,Uint16Array),1));
const sphere=new T.SphereGeometry(1,20,14);
const mat=(color,roughness=.8,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness});
function mesh(p,g,m,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;p.add(o);return o;}
function ell(p,x,y,z,rx,ry,rz,m){const o=mesh(p,sphere,m,x,y,z);o.scale.set(rx,ry,rz);return o;}
function limb(p,a,b,r1,r2,m){const aa=new T.Vector3(...a),bb=new T.Vector3(...b),d=bb.clone().sub(aa),o=mesh(p,new T.CylinderGeometry(r2,r1,d.length(),16),m);o.position.copy(aa.add(bb).multiplyScalar(.5));o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return o;}
function torso(p,m){const positions=[],uv=[],indices=[],rings=[[.74,.17,.115],[.86,.18,.12],[1.10,.21,.125],[1.20,.23,.11],[1.25,.09,.085]];for(let j=0;j<rings.length;j++){const[y,w,d]=rings[j];for(let i=0;i<=20;i++){const a=i*Math.PI/10;positions.push(Math.sin(a)*w,y,Math.cos(a)*d);uv.push(i/20,j/(rings.length-1));if(j&&i){const n=j*21+i;indices.push(n-22,n-21,n,n-22,n,n-1);}}}const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(indices);g.computeVertexNormals();return mesh(p,g,m);}
export function buildHumanoid(parent,index=0){
 const g=new T.Group();parent.add(g);const skin=mat(['#a9866c','#87644f','#bda38b'][index%3],.8),suit=mat(['#354d61','#52616b','#6f675b'][index%3],.9),trousers=mat('#253441',.95),shoe=mat('#292b2c',.63),trim=mat('#a7987d',.45,.5),shirt=mat('#aaa79a',.92);
 torso(g,suit);ell(g,0,.71,0,.175,.115,.13,trousers);limb(g,[0,1.2,0],[0,1.33,0],.055,.055,skin);
 const head=new T.Group();g.add(head);const h=mesh(head,headGeometry,skin,0,1.3458,.005);h.scale.setScalar(.047);
 // Tailored jacket: shirt inset, lapels, shoulder seams and restrained agent pin.
 const inset=mesh(g,new T.PlaneGeometry(.115,.25),shirt,0,1.1,.128);inset.rotation.x=.05;
 for(const s of [-1,1]){const lapel=mesh(g,new T.BoxGeometry(.048,.23,.012),suit,s*.067,1.11,.13);lapel.rotation.z=s*-.28;limb(g,[s*.1,1.21,.02],[s*.21,1.18,.05],.008,.008,trim);}
 mesh(g,new T.BoxGeometry(.026,.014,.012),trim,.13,1.12,.124);
 for(const s of [-1,1]){limb(g,[s*.11,.70,.02],[s*.13,.49,.35],.09,.075,trousers);ell(g,s*.13,.49,.35,.076,.078,.076,trousers);limb(g,[s*.13,.49,.35],[s*.14,.14,.39],.07,.046,trousers);ell(g,s*.14,.08,.45,.065,.06,.13,shoe);}
 const arms=[];for(const s of [-1,1]){const shoulder=new T.Group();shoulder.position.set(s*.225,1.18,0);g.add(shoulder);ell(shoulder,0,-.025,0,.075,.085,.08,suit);limb(shoulder,[0,-.025,0],[s*.035,-.265,.015],.071,.053,suit);const forearm=new T.Group();forearm.position.set(s*.035,-.265,.015);shoulder.add(forearm);limb(forearm,[0,0,0],[0,-.245,.015],.052,.034,suit);limb(forearm,[0,-.235,.015],[0,-.26,.017],.036,.036,shirt);ell(forearm,0,-.292,.02,.037,.046,.024,skin);for(let f=0;f<4;f++)limb(forearm,[(f-1.5)*.015,-.31,.022],[(f-1.5)*.015,-.355+(f%2)*.006,.03],.007,.005,skin);limb(forearm,[s*.03,-.28,.025],[s*.05,-.31,.045],.011,.007,skin);arms.push({shoulder,forearm});}
 const document=mesh(g,new T.BoxGeometry(.28,.012,.36),mat('#c8c1ad'),0,.9,.41);document.visible=false;
 return{group:g,head,arms,document,phase:0};
}
