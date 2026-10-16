import * as T from './vendor/three.js';
// The fallback projects the same articulated adult geometry. Transform each
// vertex once, cull rear faces, then paint smooth shaded foreground triangles.
export function drawIllustratedActors(ctx,actors,camera,w,h,transform){
 ctx.clearRect(0,0,w,h);const tris=[],light=new T.Vector3(-.4,.8,.6).normalize(),v=new T.Vector3(),normal=new T.Vector3();
 for(const actor of actors.values()){actor.group.updateMatrixWorld(true);actor.group.traverse(o=>{
 if(!o.isMesh||!o.visible)return;const g=o.geometry,p=g.attributes.position,na=g.attributes.normal,indices=g.index?.array,count=indices?.length||p.count,world=new Float32Array(p.count*3),projected=new Float32Array(p.count*3),nm=new T.Matrix3().getNormalMatrix(o.matrixWorld);
 for(let j=0;j<p.count;j++){v.fromBufferAttribute(p,j).applyMatrix4(o.matrixWorld);v.toArray(world,j*3);v.project(camera);projected[j*3]=(v.x+1)*w/2;projected[j*3+1]=(1-v.y)*h/2;projected[j*3+2]=v.z;}
 for(let i=0;i<count;i+=3){const ids=[0,1,2].map(k=>indices?indices[i+k]:i+k),[a,b,c]=ids.map(n=>n*3),ux=world[b]-world[a],uy=world[b+1]-world[a+1],uz=world[b+2]-world[a+2],vx=world[c]-world[a],vy=world[c+1]-world[a+1],vz=world[c+2]-world[a+2],nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
 if(nx*(camera.position.x-world[a])+ny*(camera.position.y-world[a+1])+nz*(camera.position.z-world[a+2])<=0)continue;
 const points=ids.map(n=>({x:projected[n*3],y:projected[n*3+1],z:projected[n*3+2]}));if(points.some(q=>q.z<0||q.z>1))continue;
 if(na){normal.set(na.getX(ids[0])+na.getX(ids[1])+na.getX(ids[2]),na.getY(ids[0])+na.getY(ids[1])+na.getY(ids[2]),na.getZ(ids[0])+na.getZ(ids[1])+na.getZ(ids[2])).applyMatrix3(nm).normalize();}else normal.set(nx,ny,nz).normalize();
 const color=o.material.color.clone().multiplyScalar(.55+.65*Math.max(0,normal.dot(light)));tris.push({points,z:(points[0].z+points[1].z+points[2].z)/3,color:`#${color.getHexString()}`});}
 });}
 tris.sort((a,b)=>b.z-a.z);ctx.save();ctx.translate(transform.x,transform.y);ctx.scale(transform.scale,transform.scale);ctx.lineWidth=.3/transform.scale;
 for(const t of tris){ctx.fillStyle=ctx.strokeStyle=t.color;ctx.beginPath();t.points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fill();ctx.stroke();}ctx.restore();
}
