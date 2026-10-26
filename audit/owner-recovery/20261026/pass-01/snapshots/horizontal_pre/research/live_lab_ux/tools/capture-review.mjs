import {chromium} from 'playwright-core';
import {mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {mockNativeSource,emitNative,nativeEvent,markSynthetic,captureEmptyArchitecture} from './native-review.mjs';
const base=process.env.LAB_REVIEW_URL||'http://127.0.0.1:4173',out=new URL('../artifacts/',import.meta.url).pathname,assets=new URL('../assets/',import.meta.url).pathname;await mkdir(out,{recursive:true});await mkdir(assets,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[],results=[],sourceHead=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
async function snapshot(page,name,entry){
 await page.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:120000});await page.waitForTimeout(900);
 await page.screenshot({path:`${out}${name}.png`,timeout:120000});
 results.push({name,entry,sourceHead,authority:entry==='index.html'?'synthetic explicit reducer Economic Look':'mock EventSource -> native mapper -> real reducer',viewport:page.viewportSize(),workers:await page.locator('.agent-target').count(),contextVisible:await page.locator('[data-agent-context]').isVisible(),economic:await page.locator('[data-economic-status]').innerText(),synthetic:true});console.log(`${name} captured`);
}
async function newPage(mobile=false){const page=await browser.newPage({viewport:mobile?{width:393,height:852}:{width:1440,height:1000},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});page.on('pageerror',e=>errors.push(e.message));return page;}
try{
 // Reuse one native page for idle, work and selection. This also tests a real
 // transition without rebuilding the world or recompiling all shader programs.
 const native=await newPage();await mockNativeSource(native);await native.goto(`${base}/live.html`,{waitUntil:'networkidle',timeout:120000});await emitNative(native);await markSynthetic(native);
 await snapshot(native,'A_IDLE','live.html');await captureEmptyArchitecture(native,`${assets}laboratory-idle.png`);
 await emitNative(native,'worker_event',nativeEvent());await snapshot(native,'B_ACTIVE','live.html');
 await native.locator('.agent-target').click();await native.locator('[data-agent-context]').waitFor({state:'visible',timeout:120000});await snapshot(native,'C_SELECTED','live.html');await native.close();
 const economic=await newPage();await economic.goto(`${base}/index.html?case=economic`,{waitUntil:'networkidle',timeout:120000});await snapshot(economic,'D_ECONOMIC','index.html');await economic.close();
 const phone=await newPage(true);await mockNativeSource(phone);await phone.goto(`${base}/live.html`,{waitUntil:'networkidle',timeout:120000});await emitNative(phone);await markSynthetic(phone);
 await phone.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:120000});await captureEmptyArchitecture(phone,`${assets}laboratory-idle-mobile.png`);
 await emitNative(phone,'worker_event',nativeEvent());await snapshot(phone,'E_IPHONE','live.html');await phone.close();
 await writeFile(`${out}capture-manifest.json`,JSON.stringify({sourceHead,synthetic:true,productionTouched:false,results,errors},null,2));if(errors.length)throw new Error(errors.join('\n'));
}finally{await browser.close();}
