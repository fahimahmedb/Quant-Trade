"""Acceptance tests for the S0 compute infrastructure (determinism across slicings / process counts, resume after a hard kill,
torn-tail repair, merge-verifier negative tests). Writes ACCEPTANCE_REPORT.json. SMOKE-level reps: code correctness only.

  python3 wf_accept.py
"""
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN, REPS = 'p1:m3_astra', 1000
RUN = [sys.executable, os.path.join(HERE, 'wf_run.py'), 'run', PLAN, '--reps', str(REPS)]
MRG = [sys.executable, os.path.join(HERE, 'wf_merge.py'), PLAN, '--reps', str(REPS)]


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, **kw)


def digest(files, out):
    r = sh(MRG + ['--out', out] + files)
    return r.returncode, r.stdout.strip().split()[-1] if r.returncode == 0 else r.stdout


def main():
    tmp = tempfile.mkdtemp()
    res = {}
    # 1 slice, 4 procs
    f1 = os.path.join(tmp, 'one.jsonl')
    sh(RUN + ['--out', f1, '--procs', '4'])
    rc, d_one = digest([f1], os.path.join(tmp, 'm_one.jsonl'))
    # 3 slices, different procs (1, 2, 4), reversed execution order
    fs = []
    for i, procs in ((2, 4), (0, 1), (1, 2)):
        f = os.path.join(tmp, f's{i}.jsonl')
        sh(RUN + ['--slice', f'{i}/3', '--out', f, '--procs', str(procs)])
        fs.append(f)
    rc3, d_three = digest(fs, os.path.join(tmp, 'm_three.jsonl'))
    # 7 slices, 1 proc each
    fs7 = []
    for i in range(7):
        f = os.path.join(tmp, f't{i}.jsonl')
        sh(RUN + ['--slice', f'{i}/7', '--out', f, '--procs', '1'])
        fs7.append(f)
    rc7, d_seven = digest(fs7, os.path.join(tmp, 'm_seven.jsonl'))
    res['determinism'] = dict(one_slice=d_one, three_slices=d_three, seven_slices=d_seven,
                              pass_=bool(rc == rc3 == rc7 == 0 and d_one == d_three == d_seven))
    # resume after SIGKILL
    fk = os.path.join(tmp, 'kill.jsonl')
    p = subprocess.Popen(RUN + ['--out', fk, '--procs', '1'], cwd=HERE, stdout=subprocess.DEVNULL, start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < 60:
        if os.path.exists(fk) and sum(1 for _ in open(fk)) >= 3:
            break
        time.sleep(0.05)
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()
    n_before = sum(1 for _ in open(fk))
    with open(fk, 'ab') as f:                       # simulate a torn last line
        f.write(b'{"plan": "p1:m3_astra", "idx": 9, "torn')
    r = sh(RUN + ['--out', fk, '--procs', '2'])
    rck, d_kill = digest([fk], os.path.join(tmp, 'm_kill.jsonl'))
    r2 = sh(RUN + ['--out', fk, '--procs', '2'])      # second rerun must do nothing
    res['resume'] = dict(cells_before_kill=n_before, resume_log=r.stdout.strip().splitlines()[0],
                         second_rerun_log=r2.stdout.strip().splitlines()[0], digest_after_resume=d_kill,
                         pass_=bool(rck == 0 and d_kill == d_one and 'todo 0' in r2.stdout and n_before < 10))
    # merge-verifier negative tests
    lines = open(f1).read().splitlines()
    neg = {}
    def bad(name, mut, expect):
        f = os.path.join(tmp, f'bad_{name}.jsonl')
        L = [json.loads(x) for x in lines]
        L = mut(L)
        open(f, 'w').write('\n'.join(json.dumps(x) for x in L) + '\n')
        r = sh(MRG + [f])
        neg[name] = bool(r.returncode != 0 and expect in r.stdout)
    bad('duplicate_cell', lambda L: L + [L[0]], 'DUPLICATE')
    bad('missing_cell', lambda L: L[:-1], 'MISSING')
    bad('wrong_seed', lambda L: [dict(x, seed=[1, 2, 3, 4]) if x['idx'] == 4 else x for x in L], 'seed identity')
    bad('wrong_schema', lambda L: [dict(x, schema='old') if x['idx'] == 2 else x for x in L], 'schema')
    bad('wrong_plan_hash', lambda L: [dict(x, plan_hash='0' * 64) if x['idx'] == 1 else x for x in L], 'plan_hash')
    bad('altered_spec', lambda L: [dict(x, g=dict(x['g'], th=0.5)) if x['idx'] == 3 else x for x in L], 'spec differs')
    bad('smoke_marked_evidence', lambda L: [dict(x, evidence_eligible=True) for x in L[:1]] + L[1:], 'evidence_eligible')
    res['merge_negative_tests'] = dict(results=neg, pass_=all(neg.values()))
    res['verdict'] = 'PASS' if all(v['pass_'] for v in res.values() if isinstance(v, dict)) else 'FAIL'
    json.dump(res, open(os.path.join(HERE, 'ACCEPTANCE_REPORT.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))
    return 0 if res['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
