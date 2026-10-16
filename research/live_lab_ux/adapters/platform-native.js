import {ACTIVITY,EVENT,PROGRESS,ROLES} from '../core/model.js';

const NATIVE_EVENT_TYPES=new Set(['ACTION_STARTED','ACTION_COMPLETED','WORKER_HEARTBEAT','SESSION_ENDED']);
const ACTIVITY_VALUES=new Set(Object.values(ACTIVITY));

function text(value){return typeof value==='string'&&value.trim()?value.trim():null;}
function integer(value){return Number.isInteger(value)?value:null;}
function nativeStream(event){return `native:${event.worker_id}:${event.session_id}:g${event.generation}`;}
function evidence(event){return [{ref:`worker-event:${event.event_id}`}];}
function explicitActivity(payload={}){
  const candidate=payload.ui_activity??payload.activity;
  return ACTIVITY_VALUES.has(candidate)?candidate:ACTIVITY.NONE;
}
function baseNative(event){
  if(!event||typeof event!=='object')return null;
  if(!text(event.event_id)||!text(event.session_id)||!text(event.worker_id)||!text(event.action_id))return null;
  if(!NATIVE_EVENT_TYPES.has(event.event_type))return null;
  if(integer(event.event_seq)===null||event.event_seq<1)return null;
  if(integer(event.generation)===null||event.generation<1)return null;
  const at=text(event.accepted_at)||text(event.emitted_at);
  if(!at)return null;
  return {
    id:event.event_id,
    seq:event.event_seq,
    stream:nativeStream(event),
    authorityStream:nativeStream(event),
    at,
    workerId:event.worker_id,
    role:'worker',
    evidence:evidence(event),
  };
}

/**
 * Maps only the worker facts proved by the native Site contract.
 * It deliberately does not infer Codex/Owner identity, research role,
 * progress, decisions, Economic Look activity, or economic meaning.
 */
export function mapNativeWorkerEvent(event){
  const base=baseNative(event);if(!base)return null;
  const payload=event.payload&&typeof event.payload==='object'?event.payload:{};
  const label=text(payload.label)||event.action_id;
  const detail=text(payload.detail);
  switch(event.event_type){
    case 'WORKER_HEARTBEAT':
      return {id:base.id,seq:base.seq,stream:base.stream,at:base.at,kind:EVENT.HEARTBEAT};
    case 'ACTION_STARTED':
      return {...base,kind:EVENT.WORK_STARTED,task:label,step:detail,lastAction:detail||label,activity:explicitActivity(payload),progress:{mode:PROGRESS.UNKNOWN}};
    case 'ACTION_COMPLETED':
      return {...base,kind:EVENT.IDLE,task:label,step:detail,lastAction:detail||`Completed: ${label}`,activity:ACTIVITY.NONE};
    case 'SESSION_ENDED':
      return {...base,kind:EVENT.IDLE,task:label,step:detail,lastAction:detail||'Worker session ended',activity:ACTIVITY.NONE};
    default:return null;
  }
}

function validMappedEvents(events=[]){return events.map(event=>({event,mapped:mapNativeWorkerEvent(event)})).filter(item=>item.mapped);}
function newestPerWorker(items=[]){
  const latest=new Map();
  for(const {event,mapped} of items){
    if(!mapped.workerId)continue;
    const key=mapped.workerId,current=latest.get(key);
    const currentGeneration=current?.generation??-1;
    const generation=event.generation;
    if(!current||generation>currentGeneration||(generation===currentGeneration&&event.event_seq>current.event_seq))latest.set(key,{event,event_seq:event.event_seq,generation,mapped});
  }
  return [...latest.values()];
}
function replayGuard(items=[]){
  const lastSeqByStream={};
  for(const {mapped} of items)lastSeqByStream[mapped.stream]=Math.max(lastSeqByStream[mapped.stream]??-1,mapped.seq);
  return {eventIds:items.map(({mapped})=>mapped.id),lastSeqByStream};
}

/** Convert the proven public Site snapshot shape into a non-animating UI snapshot. */
export function mapNativeSnapshot(snapshot){
  if(!snapshot||typeof snapshot!=='object'||!text(snapshot.generated_at))return null;
  const items=validMappedEvents(Array.isArray(snapshot.events)?snapshot.events:[]);
  const agents=newestPerWorker(items).map(({event})=>{
    const payload=event.payload&&typeof event.payload==='object'?event.payload:{};
    const running=event.event_type==='ACTION_STARTED';
    return {
      authorityStream:nativeStream(event),
      workerId:event.worker_id,
      role:'worker',
      stale:(snapshot.sessions||[]).some(s=>s.worker_id===event.worker_id&&s.session_id===event.session_id&&s.generation===event.generation&&['STALE','STALE_RESTART'].includes(s.lease_status)),
      state:running?'WORKING':'IDLE',
      activity:running?explicitActivity(payload):ACTIVITY.NONE,
      task:text(payload.label)||event.action_id,
      step:text(payload.detail),
      lastAction:text(payload.detail)||text(payload.label)||event.event_type,
      progress:{mode:PROGRESS.UNKNOWN},
      evidence:evidence(event),
    };
  });
  const cursor=text(snapshot.cursor)||'none';
  return {
    id:`native-snapshot:${snapshot.generated_at}:${cursor}`,
    seq:1,
    stream:`native-snapshot:${snapshot.generated_at}`,
    at:snapshot.generated_at,
    kind:EVENT.SNAPSHOT,
    agents,
    replayGuard:replayGuard(items),
  };
}

/** Map the named native SSE frames without taking ownership of transport/auth policy. */
export function mapNativeSiteFrame(frame){
  if(!frame||typeof frame!=='object')return null;
  if(frame.channel==='worker_event')return mapNativeWorkerEvent(frame.data);
  if(frame.channel==='worker_stale'){
    const d=frame.data;
    if(!d||!text(d.worker_id)||!text(d.session_id)||!Number.isInteger(d.generation)||d.generation<1||!text(d.at)||!['STALE','STALE_RESTART'].includes(d.reason))return null;
    return {id:`native-lease:${nativeStream(d)}:${d.at}`,seq:1,stream:`native-lease:${nativeStream(d)}:${d.at}`,authorityStream:nativeStream(d),at:d.at,workerId:d.worker_id,kind:EVENT.STALE,reason:d.reason};
  }
  if(frame.channel==='snapshot')return mapNativeSnapshot(frame.data);
  if(frame.channel==='connected'&&text(frame.at))return {id:`transport-connected:${frame.at}`,seq:1,stream:`transport:connected:${frame.at}`,at:frame.at,kind:EVENT.CONNECTED};
  if(frame.channel==='disconnected'&&text(frame.at))return {id:`transport-disconnected:${frame.at}`,seq:1,stream:`transport:disconnected:${frame.at}`,at:frame.at,kind:EVENT.DISCONNECTED,reason:text(frame.reason)||'Native Site event stream disconnected'};
  return null;
}

export const NATIVE_BINDING={
  roles:{worker:ROLES.worker},
  supportedEventTypes:[...NATIVE_EVENT_TYPES],
  inferredFacts:[],
  forbiddenInferences:['codex-owner-identity','research-role','progress','decision','economic-look','economic-result'],
};
