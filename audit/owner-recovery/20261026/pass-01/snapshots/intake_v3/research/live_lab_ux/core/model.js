export const ROLES = Object.freeze({
  worker: 'Worker', researcher: 'Researcher / Scout', builder: 'Builder',
  data: 'Data', auditor: 'Auditor / Red Team', manager: 'Manager / Orchestrator',
});

export const EVENT = Object.freeze({
  CONNECTED:'CONNECTED', DISCONNECTED:'DISCONNECTED', HEARTBEAT:'HEARTBEAT', STALE:'STALE', SNAPSHOT:'SNAPSHOT',
  TASK_ASSIGNED:'TASK_ASSIGNED', WORK_STARTED:'WORK_STARTED', ACTIVITY_CHANGED:'ACTIVITY_CHANGED', PROGRESS:'PROGRESS',
  BLOCKED:'BLOCKED', IDLE:'IDLE', COMMIT:'COMMIT', HANDOFF:'HANDOFF', RESULT:'RESULT', DECISION:'DECISION',
  ECONOMIC_LOOK_STARTED:'ECONOMIC_LOOK_STARTED', ECONOMIC_LOOK_FINISHED:'ECONOMIC_LOOK_FINISHED',
});

export const ACTIVITY = Object.freeze({
  NONE:'none', SOURCE_RESEARCH:'source-research', DOCUMENT_READING:'document-reading', DATA_QUALIFICATION:'data-qualification',
  HYPOTHESIS_GENERATION:'hypothesis-generation', CODING_TESTING:'coding-testing', CALCULATION:'calculation-economic-look',
  AUDIT:'audit-red-team', COMMIT:'commit-persistence', HANDOFF:'handoff', RESULT:'result', BLOCKER:'blocker',
});

export const PROGRESS = Object.freeze({ KNOWN_TOTAL:'KNOWN_TOTAL', COMPLETED_COUNT_ONLY:'COMPLETED_COUNT_ONLY', UNKNOWN:'UNKNOWN' });
export const DESTINATIONS = Object.freeze(['KILL','PARK','PROMOTE']);
export const ANIMATION_EVENTS = new Set([EVENT.WORK_STARTED,EVENT.ACTIVITY_CHANGED,EVENT.BLOCKED,EVENT.COMMIT,EVENT.HANDOFF,EVENT.RESULT,EVENT.DECISION,EVENT.ECONOMIC_LOOK_STARTED,EVENT.ECONOMIC_LOOK_FINISHED,EVENT.IDLE]);

export function normalizeProgress(value={mode:PROGRESS.UNKNOWN}) {
  if (!value || !Object.values(PROGRESS).includes(value.mode)) return {mode:PROGRESS.UNKNOWN};
  if (value.mode===PROGRESS.KNOWN_TOTAL) {
    const completed=Number(value.completed), total=Number(value.total);
    if (!Number.isFinite(completed)||!Number.isFinite(total)||total<=0) return {mode:PROGRESS.UNKNOWN};
    return {mode:PROGRESS.KNOWN_TOTAL,completed:Math.max(0,completed),total};
  }
  if (value.mode===PROGRESS.COMPLETED_COUNT_ONLY) {
    const completed=Number(value.completed);
    return Number.isFinite(completed)?{mode:PROGRESS.COMPLETED_COUNT_ONLY,completed:Math.max(0,completed)}:{mode:PROGRESS.UNKNOWN};
  }
  return {mode:PROGRESS.UNKNOWN};
}
export function formatProgress(progress) {
  const p=normalizeProgress(progress);
  if (p.mode===PROGRESS.KNOWN_TOTAL) return `${p.completed} / ${p.total}`;
  if (p.mode===PROGRESS.COMPLETED_COUNT_ONLY) return `${p.completed} completed`;
  return 'Progress unknown';
}
export function progressRatio(progress) {
  const p=normalizeProgress(progress);
  return p.mode===PROGRESS.KNOWN_TOTAL?Math.max(0,Math.min(1,p.completed/p.total)):null;
}
export function normalizeEvent(input) {
  if (!input||typeof input!=='object') throw new TypeError('event must be an object');
  if (!input.id||!Number.isInteger(input.seq)||!input.kind||!input.at) throw new TypeError('event requires id, integer seq, kind and at');
  if (!Object.values(EVENT).includes(input.kind)) throw new TypeError(`unknown event kind: ${input.kind}`);
  if (input.destination&&!DESTINATIONS.includes(input.destination)) throw new TypeError(`invalid result destination: ${input.destination}`);
  return {...input,stream:input.stream||'default',progress:input.progress?normalizeProgress(input.progress):undefined,evidence:Array.isArray(input.evidence)?input.evidence:[]};
}
