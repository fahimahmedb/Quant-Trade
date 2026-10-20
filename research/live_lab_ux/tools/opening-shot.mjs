import {chromium} from 'playwright-core';
import {mkdir} from 'node:fs/promises';
const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
page.on('pageerror',e=>console.log('PAGE ERROR',e.message));page.on('console',e=>{if(e.type()==='error')console.log('CONSOLE',e.text().slice(0,500));});
await page.goto('http://127.0.0.1:4173/index.html?case=idle',{waitUntil:'networkidle',timeout:120000});await page.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:120000});await page.waitForTimeout(900);await mkdir('artifacts',{recursive:true});await page.screenshot({path:'artifacts/REBUILD_OPENING.png',timeout:120000});console.log('Opening ready');await b.close();
