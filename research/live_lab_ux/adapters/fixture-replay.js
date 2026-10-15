export class FixtureReplayAdapter {
  constructor(events=[]){this.events=events;this.cursor=0;this.listeners=new Set();}
  subscribe(listener){this.listeners.add(listener);return()=>this.listeners.delete(listener);}
  reset(events=this.events){this.events=events;this.cursor=0;}
  next(){if(this.cursor>=this.events.length)return null;const event=structuredClone(this.events[this.cursor++]);for(const listener of this.listeners)listener(event);return event;}
  playAll(){const emitted=[];let event;while((event=this.next()))emitted.push(event);return emitted;}
  get remaining(){return this.events.length-this.cursor;}
}
