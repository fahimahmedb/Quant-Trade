#!/usr/bin/env python3
"""Qualify an exact committed GIGA F HEAD; write the non-circular receipt outside Git."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE='ebc72b9fd14f91420c37e0b7607f9bfb584a289a'
BRANCH='builder/giga-f-idea-federation-autonomous-feed-20261023'


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--remote-check',action='store_true')
    args=parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT): raise ValueError('RECEIPT_MUST_BE_OUTSIDE_QUALIFIED_TREE')
    head=git('rev-parse','HEAD')
    assert git('branch','--show-current')==BRANCH
    assert not git('status','--porcelain'), 'EXACT_HEAD_REQUIRES_CLEAN_WORKTREE'
    # Exactly one initial parent is the immutable owner-supplied Wave2 SHA.
    commits=git('rev-list','--reverse',BASE+'..HEAD').splitlines()
    assert commits and git('rev-parse',commits[0]+'^')==BASE
    assert all(len(git('rev-list','--parents','-n','1',c).split())==2 for c in commits)
    preserved=['QUANT_NORTH_STAR.md','research/research_os/multi_source_ideation.py',
        'research/research_os/multi_source_ideation_hardening.py','research/research_os/ideation_cycle.py',
        'research/research_os/multi_source_ideation_bindings.py','research/research_os/policy_c_safe.py',
        'research/research_os/discovery_chain.py','research/research_os/discovery_engine.py',
        'research/research_os/research_intelligence.py']
    assert not git('diff','--name-only',BASE,head,'--',*preserved), 'CANONICAL_COMPONENT_REPLACEMENT'
    env=dict(os.environ,PYTHONPATH=os.pathsep.join(map(str,(ROOT/'src',ROOT,ROOT/'tests'))))
    commands=[
        [sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],
        [sys.executable,'-m','unittest','discover','-s','research/research_os/tests','-p','test_*.py','-v'],
        [sys.executable,'-m','pytest','--import-mode=importlib','-q','tests','research/research_os/tests'],
        ['bash','-c','node --test research/live_lab_ux/tests/*.test.js'],
        [sys.executable,'scripts/generate_schemas.py','--check'],
        [sys.executable,'scripts/status_artifacts.py','--check'],
        [sys.executable,'scripts/demo_quant_system.py'],
    ]
    logs=args.output.parent/'giga-f-qualification-logs'; logs.mkdir(parents=True,exist_ok=True)
    results=[]
    for i,command in enumerate(commands):
        print('CHECK '+str(i+1)+': '+' '.join(command),flush=True)
        log=logs/f'{i+1:02d}.log'
        with log.open('w') as out:
            completed=subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
        if completed.returncode:
            print(log.read_text()[-6000:],flush=True)
            raise RuntimeError('QUALIFICATION_FAILED:'+str(log))
        results.append({'command':command,'status':'PASS','log':str(log)})
    with tempfile.TemporaryDirectory(prefix='giga-f-exact-demo-') as tmp:
        demo=Path(tmp)/'demo.json'
        subprocess.run([sys.executable,'scripts/demo_giga_f_idea_feed.py','--output',str(demo)],
            cwd=ROOT,env=env,stdout=subprocess.DEVNULL,check=True)
        observed=json.loads(demo.read_text())
        expected=json.loads((ROOT/'research/research_os/idea_feed/evidence/deterministic_demo.json').read_text())
        assert observed==expected, 'DETERMINISTIC_DEMO_RECEIPT_DRIFT'
    assert len(observed['origins'])==7 and observed['restart_denominator_preserved']
    assert observed['backpressure']=='BACKPRESSURE' and observed['autonomous_replenishment']
    assert not any(observed['authority'].values()) and observed['source_adapter_candidates_created']==0
    assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
    remote_match=False
    if args.remote_check:
        remote=git('ls-remote','--exit-code','origin','refs/heads/'+BRANCH).split()[0]
        assert remote==head, 'REMOTE_HEAD_MISMATCH'
        remote_match=True
    receipt={'mission':'GIGA_F','qualified_head':head,'base_sha':BASE,'branch':BRANCH,
        'full_regression':'PASS','exact_head_qualification':'PASS','worktree_clean':True,
        'remote_head_match':remote_match,'checks':results,'demo_reproduced':True,
        'safe_for_post_wave2_convergence':remote_match,'authority':observed['authority']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
