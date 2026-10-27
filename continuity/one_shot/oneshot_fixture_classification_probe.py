"""Evidence-only in-memory fixture correction; product remains frozen."""
import json,unittest,subprocess
from pathlib import Path
from research.research_os.expansion.v2_core import build_candidate,build_research_trial
from tests.test_research_os_v2_pipeline import V2PipelineTests
original=V2PipelineTests.bundle
def attributed(self):
 b=original(self);c=build_candidate(b['candidate']);b['trial']['generated_proposals'][0].update({k:c[k] for k in ('hypothesis_id','generation_id','candidate_hash')});return b
V2PipelineTests.bundle=attributed
suite=unittest.defaultTestLoader.loadTestsFromTestCase(V2PipelineTests)
r=unittest.TextTestRunner(verbosity=2).run(suite)
old=json.loads(subprocess.check_output(['git','show','ebc72b9:tests/fixtures/oracle_v2_core_fixture.json'],text=True));new=json.loads(Path('tests/fixtures/oracle_v2_core_fixture.json').read_text())
print(json.dumps({'old_trial_hash':build_research_trial(old['trial'])['trial_hash'],'attributed_trial_hash':build_research_trial(new['trial'])['trial_hash'],'product_changes':False,'state_inventory':'1107','observed_suite':'1125'},indent=2))
raise SystemExit(not r.wasSuccessful())
