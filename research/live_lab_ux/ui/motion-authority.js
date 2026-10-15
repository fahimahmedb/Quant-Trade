import {ACTIVITY} from '../core/model.js';
import {sceneBusinessMotionAllowed} from './scene3d-policy.js';
// Only factual business states may enter a gesture family. BLOCKED, HANDOFF,
// COMMIT and RESULT are facts, never implicit reading/typing/calculation.
export function gestureFamily(agent,state){
 if(!agent?.animate||!sceneBusinessMotionAllowed(state))return null;
 if([ACTIVITY.SOURCE_RESEARCH,ACTIVITY.DOCUMENT_READING].includes(agent.activity))return 'reading';
 if(agent.activity===ACTIVITY.CODING_TESTING)return 'typing';
 if([ACTIVITY.AUDIT,ACTIVITY.DATA_QUALIFICATION].includes(agent.activity))return 'comparison';
 if(agent.activity===ACTIVITY.CALCULATION)return 'economic';
 return null;
}
export function coreMotionAllowed(visual,state){
 return Boolean(visual.economicActive&&sceneBusinessMotionAllowed(state)&&visual.agents.some(a=>a.id===visual.economicWorkerId&&a.animate));
}
