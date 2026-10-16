import {chromium} from 'playwright-core';
import {mockNativeSource,emitNative,captureEmptyArchitecture} from './native-review.mjs';
const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const p=await b.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});await mockNativeSource(p);await p.goto(`${process.env.LAB_REVIEW_URL||'http://127.0.0.1:4173'}/live.html`,{waitUntil:'networkidle',timeout:120000});await emitNative(p);await p.waitForFunction(()=>document.querySelector('canvas').dataset.drawCalls,{timeout:120000});
 await captureEmptyArchitecture(p,new URL('../assets/laboratory-idle.png',import.meta.url).pathname);
 await p.setViewportSize({width:393,height:852});await p.locator('[data-camera-reset]').click();await p.waitForTimeout(3500);await captureEmptyArchitecture(p,new URL('../assets/laboratory-idle-mobile.png',import.meta.url).pathname);console.log('Clean architectural backgrounds captured');
}finally{await b.close();}
