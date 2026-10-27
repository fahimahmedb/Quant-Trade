"""Read-only exact-HEAD qualification. Known failures stay failures; outputs external."""
import concurrent.futures,datetime,json,os,pathlib,platform,subprocess,sys,hashlib
root=pathlib.Path(__file__).resolve().parents[2]
out=pathlib.Path(sys.argv[1]).resolve()
if out.is_relative_to(root): raise SystemExit('qualification logs must be outside worktree')
out.mkdir(parents=True,exist_ok=True)
def git(*args): return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
head=git('rev-parse','HEAD'); freeze=json.loads((root/'continuity/one_shot/evidence/PRODUCT_FREEZE.json').read_text())['PRODUCT_FREEZE_SHA']
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
manifest=json.loads((root/'continuity/one_shot/evidence/MANIFEST_SHA256.json').read_text())
assert manifest['SELF_HASHED'] is False
for entry in manifest['FILES']:
 p=root/entry['PATH']; assert p.stat().st_size==entry['SIZE']; assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['SHA256']

assert not git('status','--porcelain'), 'unclean initial worktree'
subprocess.run(['git','merge-base','--is-ancestor','40c590189e1389502d179e63f6e0925df8513d2c',head],cwd=root,check=True)
assert not git('diff',freeze,head,'--','research','src','deploy','scripts'), 'product changed after freeze'
for name in ['test_verified_continuity_admission_identity.py','test_verified_continuation_contract.py','test_verified_continuity_renewal.py']:
 assert (root/'continuity/one_shot/replay_tests'/(name+'.replay')).read_bytes()==subprocess.check_output(['git','show','3be85e3314aa70d2fecfd1b145c3aaa9ab5df199:tests/'+name],cwd=root)
# Production inputs remain identical to resume: code guards are the only research tree modifications.
assert not git('diff','40c5901',head,'--','research/research_os/runtime','research/research_os/tasks','research/research_os/hypotheses','research/research_os/assessments','research/research_os/sources','research/research_os/artifacts')
commands={
 'retained_integrity':['python3','-m','unittest','tests.test_research_os_trial_proposal_export_binding','tests.test_research_os_epoch_model_admission','tests.test_research_os_trial_epoch_window','tests.test_research_os_serializable_outcome_membrane','tests.test_research_os_native_trial_lineage','tests.test_research_os_epoch_blinding_admission','tests.test_research_os_evaluation_membrane_admission','tests.test_research_os_source_pit_clocks','tests.test_wave2_c2_scientific_adjudication'],
 'ordinary_regression':['python3','-m','unittest','discover','-s','tests','-p','test_*.py'],
 'research_os_regression':['python3','-m','unittest','discover','-s','research/research_os/tests','-p','test_*.py'],
 'current_c0_attack':['python3','continuity/one_shot/oneshot_c0_current_attack.py'],
 'source_shadow':['python3','continuity/one_shot/oneshot_e1_probe.py'],
 'historical_replay':['python3','continuity/one_shot/replay_historical_tests.py'],
 'schema_check':['python3','scripts/generate_schemas.py','--check']}
def run(item):
 name,cmd=item;t=datetime.datetime.now(datetime.timezone.utc).isoformat();log=out/(name+'.log')
 with log.open('w') as f:p=subprocess.run(cmd,cwd=root,env={**os.environ,'PYTHONPATH':str(root/'src')+':'+str(root),'PYTHONDONTWRITEBYTECODE':'1'},stdout=f,stderr=subprocess.STDOUT)
 return dict(NAME=name,COMMAND=cmd,ENVIRONMENT=dict(cwd=str(root),python=platform.python_version(),PYTHONPATH='src:.',state='isolated fixtures/read-only source'),HEAD_SHA=head,START_TIME=t,END_TIME=datetime.datetime.now(datetime.timezone.utc).isoformat(),RESULT='PASS' if p.returncode==0 else 'FAIL',EXIT_CODE=p.returncode,FAILURES=[] if p.returncode==0 else ['see log; preserved without waiver'],LOG_REF=str(log))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:runs=list(pool.map(run,commands.items()))
assert git('rev-parse','HEAD')==head
assert not git('status','--porcelain'), 'qualification changed worktree'
result=dict(HEAD_SHA=head,START_TIME=start,END_TIME=datetime.datetime.now(datetime.timezone.utc).isoformat(),WORKTREE_CLEAN=True,PRODUCT_FREEZE_UNCHANGED=True,PRODUCTION_INPUTS_UNCHANGED=True,RUNS=runs,RESULT='PASS' if all(x['RESULT']=='PASS' for x in runs) else 'FAIL',BOUNDED_CONTINUITY_VERDICT='NOT_QUALIFIED')
(out/'QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));sys.exit(0 if result['RESULT']=='PASS' else 1)
