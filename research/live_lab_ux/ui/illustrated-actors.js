import * as T from './vendor/three.js';
// Fallback characters use the exact articulated adult geometry and factual pose,
// projected and shaded on CPU. No toy replacement, worker prepainting or fake work.
export function drawIllustratedActors(ctx,actors,camera,w,h,transform){
 ctx.clearRect(0,0,w,h);const tris=[];const light=new T.Vector3(-.4,.8,.6).normalize();
 for(const actor of actors.values()){actor.group.updateMatrixWorld(true);actor.group.traverse(o=>{if(!o.isMesh||!o.visible)return;const p=o.geometry.attributes.position,index=o.geometry.index,indices=index?.array;const count=indices?.length||p.count;
 for(let i=0;i<count;i+=3){const vertices=[0,1,2].map(k=>new T.Vector3().fromBufferAttribute(p,indices?indices[i+k]:i+k).applyMatrix4(o.matrixWorld));const n=vertices[1].clone().sub(vertices[0]).cross(vertices[2].clone().sub(vertices[0])).normalize();const color=o.material.color.clone().multiplyScalar(.55+.7*Math.max(0,n.dot(light)));const points=vertices.map(v=>{v.project(camera);return{x:(v.x+1)*w/2,y:(1-v.y)*h/2,z:v.z};});if(points.some(p=>p.z<0||p.z>1))continue;tris.push({points,z:points.reduce((a,p)=>a+p.z,0)/3,color:`#${color.getHexString()}`});}
 });}
 tris.sort((a,b)=>b.z-a.z);ctx.save();ctx.translate(transform.x,transform.y);ctx.scale(transform.scale,transform.scale);for(const t of tris){ctx.fillStyle=t.color;ctx.beginPath();t.points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fill();}ctx.restore();
}
