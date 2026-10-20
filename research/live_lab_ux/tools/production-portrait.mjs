// Read-only public verification. No mocked transport or synthetic business facts.
import {chromium} from 'playwright-core';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const root='https://quant-trade-lab.sassylime.chatgpt.site',dir=new URL('../review/production/',import.meta.url),errors=[],checks=[];
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',proxy:{server:process.env.HTTPS_PROXY},args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 for(const fallback of [false,true]){
  const page=await browser.newPage({viewport:{width:393,height:852},isMobile:true,hasTouch:true});page.on('pageerror',e=>errors.push(e.message));
  if(fallback)await page.addInitScript(()=>{const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return ['webgl','webgl2'].includes(type)?null:get.call(this,type,...args);};});
  await page.goto(root,{waitUntil:'domcontentloaded'});
  await page.locator('[data-connectivity]').filter({hasText:/^LIVE$/}).waitFor({timeout:90000});
  if(fallback){await page.locator('.lab-illustration').waitFor();await page.waitForFunction(()=>{const i=document.querySelector('.lab-illustration');return i.complete&&i.naturalWidth>0;});}
  else await page.waitForFunction(()=>Number(document.querySelector('canvas[data-scene3d-canvas]').dataset.drawCalls)>0,{},{timeout:90000});
  assert.equal(await page.locator('.agent-target.is-active').count(),0);
  const rect=await page.locator('[data-camera]').boundingBox();assert.ok(rect.height>=850&&rect.width>=390);
  await page.screenshot({path:new URL(fallback?'F_FALLBACK.png':'E_IPHONE.png',dir).pathname,timeout:120000});
  checks.push({name:fallback?'public connected same-world fallback':'public connected iPhone portrait WebGL',status:'PASS',connectivity:await page.locator('[data-connectivity]').innerText(),viewport:rect});
  console.log('PASS '+checks.at(-1).name);await page.close();
 }
 assert.deepEqual(errors,[]);
}finally{await browser.close();await writeFile(new URL('portrait-fallback.json',dir),JSON.stringify({checked_at:new Date().toISOString(),checks,errors,real_iPhone_hardware_verified:false},null,2)+'\n');}
