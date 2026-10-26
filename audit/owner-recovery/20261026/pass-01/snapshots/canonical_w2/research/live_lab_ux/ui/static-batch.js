import * as T from './vendor/three.js';
// Bake static architecture once. Shared material batches keep mobile draw calls
// bounded. Business-authorized cartridge/ring stay independent and mutable.
export function batchArchitecture(scene,world){
 scene.updateMatrixWorld(true);const groups=new Map();
 const excluded=o=>{for(let p=o;p;p=p.parent)if(p===world.cartridge||p===world.activeRing)return true;return false;};
 scene.traverse(o=>{if(!o.isMesh||excluded(o)||Array.isArray(o.material))return;const key=o.material.uuid;let batch=groups.get(key);if(!batch){batch={material:o.material,meshes:[]};groups.set(key,batch);}batch.meshes.push(o);});
 for(const{material,meshes}of groups.values()){
 if(meshes.length<2)continue;const geometries=meshes.map(o=>{const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone();g.applyMatrix4(o.matrixWorld);return g;});
 const geometry=new T.BufferGeometry();for(const name of ['position','normal','uv']){if(!geometries.every(g=>g.getAttribute(name)))continue;const size=geometries[0].getAttribute(name).itemSize,total=geometries.reduce((n,g)=>n+g.getAttribute(name).array.length,0),array=new Float32Array(total);let offset=0;for(const g of geometries){const a=g.getAttribute(name).array;array.set(a,offset);offset+=a.length;}geometry.setAttribute(name,new T.BufferAttribute(array,size));}
 geometry.computeBoundingSphere();const merged=new T.Mesh(geometry,material);merged.castShadow=true;merged.receiveShadow=true;scene.add(merged);for(const m of meshes)m.removeFromParent();for(const g of geometries)g.dispose();
 }
}
