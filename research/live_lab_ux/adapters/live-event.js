/** Presentation boundary for the proven worker-event protocol.
 * Transport/auth/lease/retry/cursor semantics remain owned by the injected native transport.
 */
export class LiveEventAdapter {
  constructor({mapCanonicalEvent,subscribeLive=null}={}){
    if(typeof mapCanonicalEvent!=='function')throw new TypeError('LiveEventAdapter requires a canonical-event mapper');
    if(subscribeLive!==null&&typeof subscribeLive!=='function')throw new TypeError('subscribeLive must be a function');
    this.mapCanonicalEvent=mapCanonicalEvent;
    this.subscribeLive=subscribeLive;
    this.listeners=new Set();
    this.stopLive=null;
  }
  subscribe(listener){if(typeof listener!=='function')throw new TypeError('listener must be a function');this.listeners.add(listener);return()=>this.listeners.delete(listener);}
  acceptCanonicalEvent(canonicalEvent){const normalized=this.mapCanonicalEvent(canonicalEvent);if(!normalized)return null;for(const listener of this.listeners)listener(normalized);return normalized;}
  start(listener){
    if(typeof this.subscribeLive!=='function')throw new TypeError('LiveEventAdapter requires an injected live transport to start');
    if(this.stopLive)throw new Error('LiveEventAdapter already started');
    const unsubscribe=listener?this.subscribe(listener):()=>{};
    const stopTransport=this.subscribeLive((canonicalEvent)=>this.acceptCanonicalEvent(canonicalEvent));
    if(typeof stopTransport!=='function'){unsubscribe();throw new TypeError('live transport must return a stop function');}
    this.stopLive=()=>{stopTransport();unsubscribe();};
    return()=>this.stop();
  }
  stop(){const stop=this.stopLive;this.stopLive=null;if(stop)stop();}
}
