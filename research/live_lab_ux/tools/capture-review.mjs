import {chromium} from 'playwright-core';
import {mkdir,writeFile} from 'node:fs/promises';
const base=process.env.LAB_REVIEW_URL||'http://127.0.0.1:4173';
const out=new URL('../artifacts/',import.meta.url).pathname;await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[];const results=[];
for(const [name,scenario,mobile]of [['A_IDLE','idle',false],['B_ACTIVE','active',false],['C_SELECTED','selected',false],['D_ECONOMIC','economic',false],['E_IPHONE','active',true]]){
 const page=await browser.newPage({viewport:mobile?{width:393,height:852}:{width:1440,height:1000},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});
 page.on('pageerror',e=>errors.push(`${name}: ${e.message}`));
 await page.goto(`${base}/index.html?case=${scenario}`,{waitUntil:'networkidle'});await page.waitForTimeout(scenario==='selected'?3200:1800);
 await page.screenshot({path:`${out}${name}.png`});
 results.push({name,scenario,viewport:page.viewportSize(),workers:await page.locator('.agent-target').count(),contextVisible:await page.locator('[data-agent-context]').isVisible(),economic:await page.locator('[data-economic-status]').innerText(),synthetic:true});
 await page.close();
}
await writeFile(`${out}capture-manifest.json`,JSON.stringify({entry:'index.html',authority:'isolated synthetic events -> existing reduceScene -> shared live renderer',results,errors},null,2));await browser.close();if(errors.length)throw new Error(errors.join('\n'));console.log(JSON.stringify(results));
