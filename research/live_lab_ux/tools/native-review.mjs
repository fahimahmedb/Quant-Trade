// Browser-only mock of EventSource, scoped to QA pages. No production ingress,
// store, SSE server or runtime credentials are touched.
export async function mockNativeSource(page){
 await page.addInitScript(()=>{window.__reviewSources=[];window.EventSource=class extends EventTarget{constructor(url){super();this.url=url;window.__reviewSources.push(this);}close(){this.closed=true;}};});
}
export async function emitNative(page,type='open',data){
 await page.evaluate(({type,data})=>{const source=window.__reviewSources[0];if(!source)throw new Error('No native source');source.dispatchEvent(type==='open'||type==='error'?new Event(type):new MessageEvent(type,{data:JSON.stringify(data)}));},{type,data});
}
export const nativeEvent=(overrides={})=>({event_id:'synthetic-review-action-1',session_id:'synthetic-review-session',worker_id:'review-worker',action_id:'synthetic-review-action',event_type:'ACTION_STARTED',event_seq:1,generation:1,emitted_at:'2026-10-15T21:34:00Z',accepted_at:'2026-10-15T21:34:01Z',payload:{label:'Review source methodology · synthetic fixture',detail:'Reading a primary document',ui_activity:'document-reading'},...overrides});
export async function markSynthetic(page){await page.evaluate(()=>{const badge=document.createElement('span');badge.className='replay-badge';badge.textContent='SYNTHETIC REVIEW';document.querySelector('.stream').append(badge);});}
