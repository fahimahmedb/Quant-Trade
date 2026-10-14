/** Presentation-only boundary for the future proven worker-event protocol.
 * Owns NO transport, polling, authentication, lease, retry, cursor or reconnect semantics.
 */
export class LiveEventAdapter {
  constructor({mapCanonicalEvent}){if(typeof mapCanonicalEvent!=='function')throw new TypeError('LiveEventAdapter requires a canonical-event mapper');this.mapCanonicalEvent=mapCanonicalEvent;this.listeners=new Set();}
  subscribe(listener){this.listeners.add(listener);return()=>this.listeners.delete(listener);}
  acceptCanonicalEvent(canonicalEvent){const normalized=this.mapCanonicalEvent(canonicalEvent);if(!normalized)return null;for(const listener of this.listeners)listener(normalized);return normalized;}
}
