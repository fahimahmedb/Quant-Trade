import {ACTIVITY,PROGRESS,ROLES,progressRatio} from '../core/model.js';

/**
 * Structural floor nodes are architecture, not runtime claims.
 * They never become "active" unless explicit event-backed state references them.
 */
import {ZONES,ROLE_STATIONS} from './layout.js';
export {ROLE_STATIONS} from './layout.js';
export const ARCHITECTURE_NODES=Object.freeze(ZONES.map(z=>({id:z.id,label:z.name,position:[z.x,z.y,z.z]})));

const STATUS_COLOR=Object.freeze({IDLE:[0.45,0.52,0.66],WORKING:[0.31,0.91,0.67],BLOCKED:[1.0,0.39,0.50]});
const ACTIVITY_LABELS=Object.freeze({
  [ACTIVITY.NONE]:'Resting',[ACTIVITY.SOURCE_RESEARCH]:'Source research',[ACTIVITY.DOCUMENT_READING]:'Document reading',[ACTIVITY.DATA_QUALIFICATION]:'Data qualification',[ACTIVITY.CODING_TESTING]:'Coding / testing',[ACTIVITY.CALCULATION]:'Economic Look',[ACTIVITY.AUDIT]:'Audit / red-team',[ACTIVITY.COMMIT]:'Commit / persistence',[ACTIVITY.HANDOFF]:'Handoff',[ACTIVITY.RESULT]:'Result',[ACTIVITY.BLOCKER]:'Blocked',
});
const HTML_ESCAPE=Object.freeze({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'});
export function escapeSceneText(value=''){return String(value).replace(/[&<>"']/g,char=>HTML_ESCAPE[char]);}

function hashString(value=''){let hash=2166136261;for(let i=0;i<value.length;i++){hash^=value.charCodeAt(i);hash=Math.imul(hash,16777619);}return hash>>>0;}
function fallbackPosition(id){const h=hashString(id),angle=((h%360)/180)*Math.PI,radius=3.4+((h>>>9)%170)/100;return[Math.cos(angle)*radius,0.55,Math.sin(angle)*radius];}
export function positionForAgent(agent){const base=ROLE_STATIONS[agent?.role]?.position||fallbackPosition(agent?.id||'unknown');return[...base];}

export function deriveAgentVisual(agent){
  const station=ROLE_STATIONS[agent.role],stale=Boolean(agent.stale),animate=Boolean(agent.animationRunning)&&!stale,progress=progressRatio(agent.progress);
  return {
    id:agent.id,
    role:agent.role,
    label:escapeSceneText(agent.label||ROLES[agent.role]||agent.role||'Worker'),
    position:positionForAgent(agent),
    angle:station?.angle||0,
    accent:station?.accent||[0.66,0.72,0.86],
    statusColor:stale?[0.49,0.42,0.48]:(STATUS_COLOR[agent.state]||STATUS_COLOR.IDLE),
    state:stale?'STALE':agent.state,
    activity:agent.activity||ACTIVITY.NONE,
    activityLabel:escapeSceneText(ACTIVITY_LABELS[agent.activity]||agent.activity||'Unknown activity'),
    animate,
    animationRevision:Number.isInteger(agent.animationRevision)?agent.animationRevision:0,
    progress,
    progressMode:agent.progress?.mode||PROGRESS.UNKNOWN,
    task:escapeSceneText(agent.currentTask||'No task object'),
    step:escapeSceneText(agent.currentStep||'No current step'),
    destination:agent.destination||null,
    selected:false,
  };
}

export function deriveSceneVisual(state,{selectedWorkerId=null}={}){
  const agents=Object.values(state.agents||{}).map(agent=>{const visual=deriveAgentVisual(agent);visual.selected=visual.id===selectedWorkerId;return visual;});
  const economicWorkerId=state.economicLook?.activeWorkerId||null;
  return {connected:Boolean(state.transport?.connected),stale:Boolean(state.transport?.stale),economicWorkerId,economicActive:Boolean(economicWorkerId),agents,architectureNodes:ARCHITECTURE_NODES,invariants:{realCapitalAuthorized:Boolean(state.invariants?.REAL_CAPITAL_AUTHORIZED),liveTradingAuthorized:Boolean(state.invariants?.LIVE_TRADING_AUTHORIZED),paidUsdTotal:Number(state.invariants?.paid_usd_total||0)}};
}
export function sceneBusinessMotionAllowed(state){return Boolean(state.transport?.connected)&&!state.transport?.stale&&!state.transport?.resumeRequiresBusinessEvent;}
