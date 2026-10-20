// Opt-in operational check only. Credentials arrive on hidden stdin and are
// never persisted. Uses real HTTPS, ingress, D1, EventSource and integrated UI.
import {chromium} from 'playwright-core';
import {createHash,randomUUID} from 'node:crypto';
import {spawn} from 'node:child_process';
import {writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
let input='';for await(const part of process.stdin)input+=part;
const cfg=JSON.parse(input);input='';
const base='https://quant-trade-lab.sassylime.chatgpt.site';
const dir=new URL('../review/production/',import.meta.url);await mkdir(dir,{recursive:true});
const trace='PROD-CANARY-'+randomUUID().slice(0,12),checks=[],errors=[];
const report={trace_id:trace,scope:'WRAPPED_BENIGN_OPERATIONAL_CANARY_ONLY',base,checks,errors,real_capital_authorized:false,live_trading_authorized:false,paid_usd_total:0,identity_claim:'No Codex/Owner/research identity claim',started_at:new Date().toISOString()};
const sha=s=>createHash('sha256').update(s).digest('hex');
const check=(name,details={})=>{checks.push({name,...details});console.log('PASS '+name);};
async function call(path,payload,{auth=true,origin}={}){const res=await fetch(base+'/__platform_probe/'+path,{method:payload===undefined?'GET':'POST',headers:{...(auth?{authorization:'Bearer '+cfg.worker_key}:{}),...(payload?{'content-type':'application/json'}:{}),...(origin?{origin}:{})},...(payload?{body:JSON.stringify(payload)}:{}),signal:AbortSignal.timeout(20000)});return {status:res.status,body:await res.json()};}
let browser,page,session,sequence=0,heartbeat,child,finishPromise;
const packet=type=>({worker_id:session.worker_id,session_id:session.session_id,lease_id:session.lease_id,session_generation:session.generation,sequence:++sequence,event_id:trace+'-'+sequence,trace_id:trace,scope:'PLATFORM_PROBE_ONLY',type,action_id:trace+'-sha256',label:'Production connectivity canary · benign SHA256',detail:'Actual wrapped Python subprocess; no research or economic action',ui_activity:'coding-testing'});
async function event(type,extra={}){const body={...packet(type),...extra};const r=await call('event',body);assert.equal(r.status,200,JSON.stringify(r));return {packet:body,receipt:r.body};}
try{
 const provenance=await(await fetch(base+'/live-lab-source.json')).json();assert.equal(provenance.release_id,'owner-ux-20261016-r1');report.ux_commit_sha=provenance.ux_commit_sha;check('production serves rebuilt release',{release:provenance.release_id,ux_commit_sha:provenance.ux_commit_sha});
 const anonymous=await call('session',{worker_id:cfg.worker_id},{auth:false});assert.equal(anonymous.status,401);check('anonymous ingress remains rejected');
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',proxy:{server:process.env.HTTPS_PROXY},args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 page=await browser.newPage({viewport:{width:1200,height:850}});page.on('pageerror',e=>errors.push(e.message));
 const cdp=await page.context().newCDPSession(page);await cdp.send('Network.enable');const frames=[];cdp.on('Network.eventSourceMessageReceived',e=>{if(['snapshot','worker_event','worker_stale'].includes(e.eventName))frames.push({channel:e.eventName,data:JSON.parse(e.data),received_at:Date.now()});});
 await page.goto(base,{waitUntil:'domcontentloaded'});await page.locator('[data-connectivity]').filter({hasText:/^LIVE$/}).waitFor({timeout:60000});await page.waitForFunction(()=>Number(document.querySelector('canvas[data-scene3d-canvas]').dataset.drawCalls)>0,{},{timeout:90000});assert.equal(await page.locator('.agent-target.is-active').count(),0);await page.screenshot({timeout:120000,path:new URL('A_IDLE.png',dir).pathname});check('public integrated WebGL and native stream connected idle');
 const cursor=(await(await fetch(base+'/api/work/snapshot')).json()).cursor;
 await page.evaluate(cursor=>{window.__canaryDeliveries={};window.__canaryDeliverySource=new EventSource('/__platform_probe/stream?cursor='+cursor);window.__canaryDeliverySource.addEventListener('worker_event',e=>{const d=JSON.parse(e.data);window.__canaryDeliveries[d.event_id]=d;});},cursor);
 const created=await call('session',{worker_id:cfg.worker_id,native_session_id:randomUUID(),trace_id:trace});assert.equal(created.status,200,JSON.stringify(created));session=created.body;report.binding={worker_id:session.worker_id,session_id:session.session_id,generation:session.generation};
 const countBeforeHeartbeat=await page.locator('.agent-target').count();const hb=await event('HEARTBEAT',{label:'Production transport presence check',detail:'Authenticated canary launcher; no command started',ui_activity:'none'});const heartbeatDeadline=Date.now()+20000;while(!frames.some(x=>x.data.event_id===hb.packet.event_id)){assert.ok(Date.now()<heartbeatDeadline,'heartbeat delivered over native SSE');await new Promise(r=>setTimeout(r,100));}assert.equal(await page.locator('.agent-target').count(),countBeforeHeartbeat);assert.equal(await page.locator('.agent-target.is-active').count(),0);check('real heartbeat creates no business animation',{event_id:hb.packet.event_id});
 const code='import hashlib,time\nd=b"QUANT_OPERATIONAL_CONNECTIVITY_ONLY";end=time.monotonic()+120;n=0\nwhile time.monotonic()<end:\n for _ in range(10000):d=hashlib.sha256(d).digest();n+=1\n time.sleep(.05)\nprint(d.hex());print(n)';
 child=spawn('python3',['-c',code]);let out='',err='';child.stdout.on('data',d=>out+=d);child.stderr.on('data',d=>err+=d);const completed=new Promise(resolve=>child.on('close',exit_code=>resolve({exit_code:exit_code??-1,stdout_sha256:sha(out),stderr_sha256:sha(err),command_sha256:sha(code)})));
 const start=await event('ACTION_STARTED');report.start=start;
 let sending=false;heartbeat=setInterval(async()=>{if(sending)return;sending=true;try{await event('HEARTBEAT');}catch(e){errors.push('heartbeat: '+e.message);}finally{sending=false;}},session.heartbeat_interval_ms);
 finishPromise=completed.then(async proof=>{clearInterval(heartbeat);while(sending)await new Promise(r=>setTimeout(r,25));const done=await event('ACTION_COMPLETED',{effect_proof:proof});report.effect_proof=proof;report.completion=done;return done;});
 const target=page.locator(`.agent-target[title^="${cfg.worker_id} ·"]`);await page.locator(`.agent-target.is-active[title^="${cfg.worker_id} ·"]`).waitFor({state:'attached',timeout:60000});
 assert.ok(frames.some(x=>x.data.event_id===start.packet.event_id),'main native stream received accepted action');
 await page.waitForFunction(id=>Boolean(window.__canaryDeliveries[id]),start.packet.event_id,{timeout:20000});
 const ack=await page.evaluate(async({event_id,trace_id})=>{const d=window.__canaryDeliveries[event_id],at=performance.now();await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);if(document.visibilityState!=='visible'||!document.querySelector('.agent-target.is-active'))throw Error('Main scene not visibly active');const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(event_id+'|'+d.type)))).map(n=>n.toString(16).padStart(2,'0')).join('');const r=await fetch('/__platform_probe/ack',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({delivery_token:d.delivery_token,trace_id,last_applied_event_id:event_id,render_state_hash:hash,frame_cycles:2,visibility:document.visibilityState,render_after_receive_ms:performance.now()-at})});return {status:r.status,body:await r.json()};},{event_id:start.packet.event_id,trace_id:trace});
 assert.equal(ack.status,200);report.render_ack=ack.body;check('authenticated ingress → D1 → public SSE → real reducer → visible active worker → post-frame ACK',{event_id:start.packet.event_id});
 await page.screenshot({timeout:120000,path:new URL('B_ACTIVE.png',dir).pathname});
 const duplicate=await call('event',start.packet);assert.equal(duplicate.body.status,'DUPLICATE_IGNORED');assert.equal(duplicate.body.cursor,start.receipt.cursor);check('native duplicate does not create another transition');
 await target.click();assert.equal(await page.locator('[data-agent-context]').isVisible(),false);await page.locator('[data-agent-context]').waitFor({state:'visible',timeout:90000});await page.screenshot({timeout:120000,path:new URL('C_SELECTED.png',dir).pathname});await page.locator('[data-open-details]').click();assert.equal(await page.locator('[data-detail-progress]').innerText(),'Progress unknown');await page.locator('[data-sheet-close]').click();check('production focus precedes context and progress remains unknown');
 const done=await finishPromise;await page.locator(`.agent-target:not(.is-active)[title^="${cfg.worker_id} ·"]`).waitFor({state:'attached',timeout:60000});check('actual subprocess completion stops gesture',{event_id:done.packet.event_id,exit_code:report.effect_proof.exit_code});
 report.end=await event('SESSION_ENDED');
 await page.reload({waitUntil:'domcontentloaded'});await page.locator('[data-connectivity]').filter({hasText:/^LIVE$/}).waitFor({timeout:60000});assert.equal(await page.locator('.agent-target.is-active').count(),0);check('real reload snapshot does not replay work');
 const phone=await browser.newPage({viewport:{width:393,height:852},isMobile:true,hasTouch:true});phone.on('pageerror',e=>errors.push(e.message));await phone.goto(base,{waitUntil:'domcontentloaded'});await phone.locator('[data-connectivity]').filter({hasText:/^LIVE$/}).waitFor({timeout:90000});await phone.waitForFunction(()=>Number(document.querySelector('canvas[data-scene3d-canvas]').dataset.drawCalls)>0,{},{timeout:90000});await phone.screenshot({timeout:120000,path:new URL('E_IPHONE.png',dir).pathname});check('production iPhone portrait viewport renders');await phone.close();
 assert.equal(await page.locator('[data-economic-status]').innerText(),'FREE');assert.deepEqual(errors,[]);report.status='PASS';
}catch(e){report.status='FAIL';report.failure=e.message;console.error(e.message);process.exitCode=1;}
finally{
 clearInterval(heartbeat);if(child&&child.exitCode===null)child.kill();
 try{await finishPromise;}catch(e){report.cleanup_error=e.message;}
 if(session&&!report.end){try{report.end=await event('SESSION_ENDED');}catch(e){report.cleanup_error=e.message;}}
 await browser?.close();report.finished_at=new Date().toISOString();await writeFile(new URL('canary.json',dir),JSON.stringify(report,null,2)+'\n');console.log('CANARY '+report.status);
}
