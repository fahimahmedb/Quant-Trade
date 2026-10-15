import {chromium} from 'playwright-core';
import {mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {mockNativeSource,emitNative,nativeEvent,markSynthetic} from './native-review.mjs';
const base=process.env.LAB_REVIEW_URL||'http://127.0.0.1:4173',out=new URL('../artifacts/',import.meta.url).pathname,assets=new URL('../assets/',import.meta.url).pathname;await mkdir(out,{recursive:true});await mkdir(assets,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[],results=[];
for(const [name,scenario,mobile]of [['A_IDLE','idle',false],['B_ACTIVE','active',false],['C_SELECTED','selected',false],['D_ECONOMIC','economic',false],['E_IPHONE','active',true]]){
 const page=await browser.newPage({viewport:mobile?{width:393,height:852}:{width:1440,height:1000},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});page.on('pageerror',e=>errors.push(`${name}: ${e.message}`));
 if(scenario==='economic')await page.goto(`${base}/index.html?case=economic`,{waitUntil:'networkidle'});
 else{await mockNativeSource(page);await page.goto(`${base}/live.html`,{waitUntil:'networkidle'});await emitNative(page);await markSynthetic(page);if(scenario!=='idle')await emitNative(page,'worker_event',nativeEvent());}
 await page.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:90000});
 if(scenario==='selected'){await page.locator('.agent-target').click();await page.locator('[data-agent-context]').waitFor({state:'visible',timeout:90000});}
 await page.waitForTimeout(1200);await page.screenshot({path:`${out}${name}.png`,timeout:120000});
 results.push({name,entry:scenario==='economic'?'index.html':'live.html',authority:scenario==='economic'?'synthetic explicit reducer Economic Look':'mock EventSource -> native mapper -> real reducer',viewport:page.viewportSize(),workers:await page.locator('.agent-target').count(),contextVisible:await page.locator('[data-agent-context]').isVisible(),economic:await page.locator('[data-economic-status]').innerText(),synthetic:true});
 if(name==='A_IDLE')await page.locator('[data-scene3d-canvas]').screenshot({path:`${assets}laboratory-idle.png`,timeout:120000});
 if(name==='E_IPHONE'){await page.reload({waitUntil:'networkidle'});await emitNative(page);await page.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:90000});await page.locator('[data-scene3d-canvas]').screenshot({path:`${assets}laboratory-idle-mobile.png`,timeout:120000});}
 await page.close();console.log(`${name} captured`);
}
await writeFile(`${out}capture-manifest.json`,JSON.stringify({sourceHead:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),synthetic:true,productionTouched:false,results,errors},null,2));await browser.close();if(errors.length)throw new Error(errors.join('\n'));
