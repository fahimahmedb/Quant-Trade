"""Synthetic direct-ref outcome membrane probe; never uses real protected outcomes."""
from copy import deepcopy
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(root/'src'),str(root)]
from research.research_os.expansion import scientific_adjudication as c0
from research.research_os.scientific_store import sha256_json
from tests.test_wave2_c2_scientific_adjudication import Wave2C2ScientificAdjudicationTests,independence_record
fixture=Wave2C2ScientificAdjudicationTests();fixture.setUp()
ref=c0.bind_independence_ref(fixture.factory,independence_record())
ref['audit']={'nested':[{'return_series':['SYNTHETIC_FORBIDDEN_ALIAS_MARKER_NO_REAL_OUTCOMES']} ]}
ref['ref_hash']=sha256_json({k:v for k,v in ref.items() if k!='ref_hash'})
before=deepcopy(ref)
checks=[]
for name,fn in [
 ('PUBLIC_VALIDATE',lambda:c0.validate_independence_ref(ref,fixture.factory)),
 ('PRESERVED_INNER_VALIDATE',lambda:c0._impl.validate_independence_ref(ref,fixture.factory)),
 ('PUBLIC_COMPOSITION',lambda:fixture.adjudicate(independence_ref=ref)),
 ('PRESERVED_INNER_COMPOSITION',lambda:c0._impl.adjudicate_scientific_candidate(fixture.factory,cross_examination_ref=fixture.cross,validator_ref=fixture.validator,red_team_ref=fixture.red_team,independence_ref=ref)),
]:
 try:
  out=fn()
  checks.append({'ENTRYPOINT':name,'RESULT':'ACCEPTED','VERDICT':out.get('verdict') if isinstance(out,dict) else None,'INDEPENDENT_CONFIRMATION_COUNT':out.get('independent_confirmation_count') if isinstance(out,dict) else None,'RAW_OUTCOMES_CONSUMED_CLAIM':out.get('raw_outcomes_consumed') if isinstance(out,dict) else None})
 except Exception as e:checks.append({'ENTRYPOINT':name,'RESULT':'REJECTED','ERROR':str(e),'TYPE':type(e).__name__})
result={'SYNTHETIC':True,'PRODUCTION_SCIENCE':False,'REAL_PROTECTED_OUTCOMES_ACCESSED':False,'PRODUCTION_STATE_MUTATED':False,'ALIAS_PATH':'$.audit.nested[0].return_series','ALIAS_CLASS':'Existing C0 _FORBIDDEN_OUTCOME_KEYS includes return_series','ORIGINAL_REF_COUNT':ref['independent_confirmation_count'],'REF_UNCHANGED_BY_VALIDATION_COMPOSITION':ref==before,'FACTORY_HASH_BOUND':ref['factory_ref_hash']==fixture.factory['ref_hash'],'CHECKS':checks,'CLASSIFICATION':'CURRENT_INVARIANT_RESIDUAL_OUTCOME_REF_MEMBRANE','SCOPE':'Inherited preexisting direct-ref validation path; separate followup, no product repair in count mission'}
print(json.dumps(result,indent=2))
sys.exit(1 if any(x['RESULT']=='ACCEPTED' for x in checks) else 0)
