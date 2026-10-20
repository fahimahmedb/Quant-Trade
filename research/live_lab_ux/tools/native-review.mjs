// Browser-only mock of EventSource, scoped to QA pages. No production ingress,
// store, SSE server or runtime credentials are touched.
export async function mockNativeSource(page){
 await page.addInitScript(()=>{window.__reviewSources=[];window.EventSource=class extends EventTarget{constructor(url){super();this.url=url;window.__reviewSources.push(this);}close(){this.closed=true;}};});
}
export async function emitNative(page,type='open',data){
 await page.evaluate(({type,data})=>{const source=window.__reviewSources[0];if(!source)throw new Error('No native source');source.dispatchEvent(type==='open'||type==='error'?new Event(type):new MessageEvent(type,{data:JSON.stringify(data)}));},{type,data});
}
export const nativeEvent=(overrides={})=>({event_id:'synthetic-review-action-1',session_id:'synthetic-review-session',worker_id:'review-worker',action_id:'synthetic-review-action',event_type:'ACTION_STARTED',event_seq:1,generation:1,emitted_at:'2026-10-15T21:34:00Z',accepted_at:'2026-10-15T21:34:01Z',payload:{label:'Review source methodology · synthetic fixture',detail:'Reading a primary document',ui_activity:'document-reading'},...overrides});
export const oracleNativeEvent=(overrides={})=>({event_id:'synthetic-oracle-action-1',session_id:'synthetic-oracle-session',worker_id:'oracle-research-v1',action_id:'FRONTIER-SYNTHETIC-REVIEW',event_type:'ACTION_STARTED',event_seq:1,generation:1,emitted_at:'2026-10-20T02:00:00Z',accepted_at:'2026-10-20T02:00:01Z',payload:{label:'Generate bounded candidate hypothesis · synthetic fixture',detail:'Local GPT-OSS pre-outcome reasoning · synthetic fixture',ui_activity:'hypothesis-generation',ui_role:'researcher',ui_label:'Oracle'},...overrides});
export async function markSynthetic(page){await page.evaluate(()=>{const badge=document.createElement('span');badge.className='replay-badge';badge.textContent='SYNTHETIC REVIEW';document.querySelector('.stream').append(badge);});}
export async function captureEmptyArchitecture(page,path){
 // Element screenshots include overlapping DOM. Hide factual overlays while
 // capturing the empty world; never bake LIVE, clocks, workers or HUD into it.
 const style=await page.addStyleTag({content:'.app-shell > :not(.camera), [data-scene3d-labels]{visibility:hidden!important}'});
 try{await page.locator('[data-scene3d-canvas]').screenshot({path,timeout:120000});}finally{await style.evaluate(node=>node.remove());}
}
