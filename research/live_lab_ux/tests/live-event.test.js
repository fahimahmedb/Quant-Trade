import test from 'node:test';
import assert from 'node:assert/strict';
import {LiveEventAdapter} from '../adapters/live-event.js';

test('live adapter starts injected transport, maps frames, and stops exactly once',()=>{
  const emitted=[];
  let transportEmit=null,stopCount=0;
  const adapter=new LiveEventAdapter({
    mapCanonicalEvent:(frame)=>frame.kind==='accepted'?{id:frame.id}:null,
    subscribeLive:(emit)=>{transportEmit=emit;return()=>{stopCount+=1;};},
  });
  adapter.start((event)=>emitted.push(event));
  transportEmit({kind:'accepted',id:'e1'});
  transportEmit({kind:'ignored',id:'e2'});
  assert.deepEqual(emitted,[{id:'e1'}]);
  adapter.stop();
  adapter.stop();
  assert.equal(stopCount,1);
});

test('live adapter rejects duplicate starts and transport without stop handle',()=>{
  const adapter=new LiveEventAdapter({mapCanonicalEvent:(x)=>x,subscribeLive:()=>()=>{}});
  adapter.start(()=>{});
  assert.throws(()=>adapter.start(()=>{}),/already started/);
  adapter.stop();
  const broken=new LiveEventAdapter({mapCanonicalEvent:(x)=>x,subscribeLive:()=>null});
  assert.throws(()=>broken.start(()=>{}),/stop function/);
});
