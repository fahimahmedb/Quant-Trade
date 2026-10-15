import {renderDetailSheet} from './render.js';
export function createInterface({getState,onSelection,camera}){
 const q=s=>document.querySelector(s),context=q('[data-agent-context]'),sheet=q('[data-detail-sheet]');
 let selected=null,focused=null;
 const refs=Object.fromEntries(['worldAgents','economicStatus','connectivity','warning','resumeGuard','clock','roleCount','resultWall','detailSheet'].map(key=>[key,q(`[data-${key.replace(/[A-Z]/g,c=>'-'+c.toLowerCase())}]`)]));
 function showContext(){const a=getState().agents[focused];if(!a){context.hidden=true;return;}context.hidden=false;q('[data-context-role]').textContent=a.label;q('[data-context-state]').textContent=`${a.id} · ${a.stale?'STALE':a.state}`;q('[data-context-task]').textContent=a.currentTask||'No task received';}
 function select(id){selected=id;focused=null;context.hidden=true;sheet.close();onSelection(id);}
 q('[data-detail-close]').addEventListener('click',()=>select(null));
 q('[data-open-details]').addEventListener('click',()=>{if(!selected)return;renderDetailSheet(getState(),selected,sheet);sheet.showModal();});
 q('[data-sheet-close]').addEventListener('click',()=>sheet.close());
 sheet.addEventListener('click',e=>{if(e.target===sheet&&e.clientY<sheet.getBoundingClientRect().top)sheet.close();});
 q('[data-zoom-in]').addEventListener('click',()=>camera().zoom(.12));q('[data-zoom-out]').addEventListener('click',()=>camera().zoom(-.12));q('[data-camera-reset]').addEventListener('click',()=>{select(null);camera().reset();});
 return{refs,select,focused(id){if(selected===id){focused=id;showContext();}},render(){showContext();if(sheet.open&&selected)renderDetailSheet(getState(),selected,sheet);},get selected(){return selected;}};
}
