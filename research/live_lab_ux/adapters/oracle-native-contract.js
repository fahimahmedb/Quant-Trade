import {ACTIVITY} from '../core/model.js';

export const ORACLE_NATIVE_SCOPE='ORACLE_RESEARCH_PRE_OUTCOME';
export const ORACLE_UI_ROLE='researcher';
export const ORACLE_UI_LABEL='Oracle';

const TYPES=new Set(['ACTION_STARTED','WORKER_HEARTBEAT','ACTION_COMPLETED','SESSION_ENDED']);
const forbiddenKeys=new Set([
  'progress','progress_percent','economic_result','return','pnl','alpha','position','order','real_capital_authorized','live_trading_authorized',
]);

function requiredText(value,name){
  if(typeof value!=='string'||!value.trim())throw new TypeError(`${name}_REQUIRED`);
  return value.trim();
}
function positiveInteger(value,name){
  if(!Number.isInteger(value)||value<1)throw new TypeError(`${name}_POSITIVE_INTEGER_REQUIRED`);
  return value;
}
function forbidOutcomeLikeFields(value,path='packet'){
  if(!value||typeof value!=='object')return;
  for(const [key,item] of Object.entries(value)){
    if(forbiddenKeys.has(key.toLowerCase()))throw new TypeError(`FORBIDDEN_ORACLE_UI_FIELD:${path}.${key}`);
    if(item&&typeof item==='object')forbidOutcomeLikeFields(item,`${path}.${key}`);
  }
}
function effectProof(value){
  if(!value||typeof value!=='object')throw new TypeError('EFFECT_PROOF_REQUIRED_FOR_COMPLETION');
  const exit=value.exit_code;
  if(!Number.isInteger(exit))throw new TypeError('EFFECT_PROOF_EXIT_CODE_REQUIRED');
  const output=requiredText(value.output_sha256??value.stdout_sha256,'EFFECT_PROOF_OUTPUT_SHA256');
  if(!/^[0-9a-f]{64}$/i.test(output))throw new TypeError('EFFECT_PROOF_OUTPUT_SHA256_INVALID');
  return {exit_code:exit,output_sha256:output.toLowerCase()};
}

/**
 * Build the semantic packet Oracle may submit to a dedicated authenticated Site
 * principal. This function does not know or claim an ingress URL/credential.
 * The Site must authenticate the principal and translate accepted fields into
 * the existing native worker-event contract before public SSE projection.
 */
export function buildOracleIngressPacket({
  workerId='oracle-research-v1',sessionId,leaseId,generation,sequence,eventId,
  type,actionId,label,detail,effectProof:proof,
}){
  if(!TYPES.has(type))throw new TypeError('UNSUPPORTED_ORACLE_EVENT_TYPE');
  const packet={
    worker_id:requiredText(workerId,'WORKER_ID'),
    session_id:requiredText(sessionId,'SESSION_ID'),
    lease_id:requiredText(leaseId,'LEASE_ID'),
    session_generation:positiveInteger(generation,'SESSION_GENERATION'),
    sequence:positiveInteger(sequence,'SEQUENCE'),
    event_id:requiredText(eventId,'EVENT_ID'),
    scope:ORACLE_NATIVE_SCOPE,
    type,
    action_id:requiredText(actionId,'ACTION_ID'),
    label:requiredText(label,'LABEL'),
    detail:requiredText(detail,'DETAIL'),
    ui_activity:type==='ACTION_STARTED'?ACTIVITY.HYPOTHESIS_GENERATION:ACTIVITY.NONE,
    ui_role:ORACLE_UI_ROLE,
    ui_label:ORACLE_UI_LABEL,
  };
  if(type==='ACTION_COMPLETED')packet.effect_proof=effectProof(proof);
  if(proof&&type!=='ACTION_COMPLETED')throw new TypeError('EFFECT_PROOF_ONLY_ALLOWED_ON_COMPLETION');
  forbidOutcomeLikeFields(packet);
  return packet;
}

export function oracleHeartbeat(base){
  return buildOracleIngressPacket({...base,type:'WORKER_HEARTBEAT'});
}

export const ORACLE_NATIVE_CONTRACT=Object.freeze({
  version:'oracle-native-ui.v1',
  scope:ORACLE_NATIVE_SCOPE,
  ingressEndpoint:'UNBOUND_UNTIL_SITE_PRINCIPAL_IS_DEPLOYED',
  authenticatedPrincipalRequired:true,
  siteMustPreserve:['ui_activity','ui_role','ui_label'],
  heartbeatAuthorizesBusinessMotion:false,
  snapshotAuthorizesBusinessMotion:false,
  economicOutcomeFieldsAllowed:false,
});
