function parseFrame(channel,event,listener){
  try{listener({channel,data:JSON.parse(event.data)});}catch(error){
    listener({channel:'disconnected',at:new Date().toISOString(),reason:`Invalid ${channel} frame: ${error.message}`});
  }
}

/**
 * Thin browser binding for the already-proved Site SSE endpoint.
 * EventSource owns reconnect/cursor behavior; this layer adds no polling,
 * heartbeat timer, lease timer, retry scheduler, or fabricated progress.
 */
export function subscribeNativeSiteEvents(listener,{url='/api/work/events',EventSourceImpl=globalThis.EventSource,now=()=>new Date().toISOString()}={}){
  if(typeof listener!=='function')throw new TypeError('listener must be a function');
  if(typeof EventSourceImpl!=='function')throw new TypeError('EventSource is unavailable');
  const source=new EventSourceImpl(url);
  const onOpen=()=>listener({channel:'connected',at:now()});
  const onSnapshot=(event)=>parseFrame('snapshot',event,listener);
  const onWorkerEvent=(event)=>parseFrame('worker_event',event,listener);
  const onStale=event=>parseFrame('worker_stale',event,listener);
  const onStoreError=()=>listener({channel:'disconnected',at:now(),reason:'Native worker store unavailable'});
  const onError=()=>listener({channel:'disconnected',at:now(),reason:'Native Site event stream disconnected'});
  source.addEventListener('open',onOpen);
  source.addEventListener('snapshot',onSnapshot);
  source.addEventListener('worker_event',onWorkerEvent);
  source.addEventListener('worker_stale',onStale);
  source.addEventListener('stream_error',onStoreError);
  source.addEventListener('error',onError);
  return ()=>{
    source.removeEventListener?.('open',onOpen);
    source.removeEventListener?.('snapshot',onSnapshot);
    source.removeEventListener?.('worker_event',onWorkerEvent);
    source.removeEventListener?.('worker_stale',onStale);
    source.removeEventListener?.('stream_error',onStoreError);
    source.removeEventListener?.('error',onError);
    source.close();
  };
}
