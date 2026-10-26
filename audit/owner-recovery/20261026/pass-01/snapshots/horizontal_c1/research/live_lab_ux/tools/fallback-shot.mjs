import {chromium} from 'playwright-core';
const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
try{
 const p=await b.newPage({viewport:{width:393,height:852},isMobile:true,hasTouch:true});const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type==='webgl'||type==='webgl2'?null:original.call(this,type,...args);};});
 await p.goto(`${process.env.LAB_REVIEW_URL||'http://127.0.0.1:4173'}/index.html?case=active`,{waitUntil:'networkidle'});await p.locator('.has-illustration').waitFor();
 if(!await p.locator('.lab-illustration').evaluate(i=>i.complete&&i.naturalWidth>0))throw new Error('Missing fallback illustration');
 await p.locator('.agent-target').click();await p.locator('[data-agent-context]').waitFor({state:'visible',timeout:30000});await p.screenshot({path:new URL('../artifacts/F_FALLBACK.png',import.meta.url).pathname,timeout:60000});if(errors.length)throw new Error(errors.join('\n'));console.log('Current forced fallback captured');
}finally{await b.close();}
