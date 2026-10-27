from pathlib import Path
from copy import deepcopy
import importlib.util,json,sys
root=Path(sys.argv[1])
sys.path.insert(0,str(root))
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from research.research_os.expansion.v2_core import assert_model_allowed,build_epoch_manifest
fixture=json.loads(Path('/workspace/Quant-Trade/tests/fixtures/oracle_v2_core_fixture.json').read_text())
results={}
def trial(name, mutate):
 b=deepcopy(fixture); mutate(b)
 try: results[name]={'result':'ACCEPTED','status':run_pre_outcome_pipeline(b)['status']}
 except Exception as e: results[name]={'result':'REJECTED','error':str(e),'type':type(e).__name__}
trial('valid_baseline',lambda b:None)
trial('unattributed_proposal',lambda b:b['trial'].update(generated_proposals=[{'id':'UNATTRIBUTED_SYNTHETIC'}]))
trial('outside_model_policy',lambda b:b['trial'].update(model_identity='SYNTHETIC_UNAPPROVED'))
trial('outside_generation_window',lambda b:b['trial'].update(generated_at='2026-10-19T00:00:00Z'))
trial('tuple_hidden_outcome',lambda b:b['export'].update(review_context=({'outcome':'SYNTHETIC_MARKER'},)))
try:
 assert_model_allowed({'allowed_model_set':[None]},None);results['null_model_equality']={'result':'ACCEPTED'}
except Exception as e:results['null_model_equality']={'result':'REJECTED','error':str(e)}
print(json.dumps(results,indent=2))
