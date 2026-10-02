"""Weather V3 / S0 - merge verifier.

  python3 wf_merge.py PLAN --reps N [--streams 1|5] [--cells 0,1,..] [--K consts.json] --out MERGED.jsonl  slice1.jsonl slice2.jsonl ...

Verifies, and exits non-zero (listing every violation) unless all hold:
  - expected cell count (all cells of the plan, or the --cells subset) present exactly once;
  - no duplicate cell id (across all input files);
  - exact deterministic seed identity: seed == [base_seed, plan_code, cell_id, stream] (CONFIRM: five seeds, streams 1..5);
  - schema version and engine version equal the current ones;
  - plan_hash equals the hash recomputed from the plan definition (+ K), cell spec `g` equals the plan's cell spec,
    reps / streams / rep_block as declared;
  - no SMOKE record is marked evidence_eligible.
Writes the merged file sorted by cell id and prints a content digest (sha256 of the sorted canonical lines), which is the
object compared across slicings.
"""
import hashlib
import json
import sys

import wf_engine as E
import wf_plans as P


def verify(plan, reps, streams, cells, K, files):
    errs = []
    d = P.PLAN_DEFS[plan]
    specs = P.plan_cells(plan)
    ph = P.plan_hash(plan, K)
    expect = set(range(len(specs))) if cells is None else set(cells)
    seen = {}
    for fn in files:
        for ln, line in enumerate(open(fn), 1):
            line = line.strip()
            if not line:
                continue
            try:
                x = json.loads(line)
            except ValueError:
                errs.append(f'{fn}:{ln} unparseable'); continue
            if x.get('reps') != reps or x.get('streams') != streams:
                continue                              # other run level in a shared file: not part of this merge
            i = x.get('idx')
            where = f'{fn}:{ln} cell {i}'
            if i in seen:
                errs.append(f'{where} DUPLICATE cell id (first in {seen[i][0]})'); continue
            seen[i] = (fn, x)
            if x.get('schema') != E.SCHEMA_VERSION:
                errs.append(f'{where} schema {x.get("schema")} != {E.SCHEMA_VERSION}')
            if x.get('engine') != E.ENGINE_VERSION:
                errs.append(f'{where} engine {x.get("engine")} != {E.ENGINE_VERSION}')
            if x.get('plan') != plan or x.get('plan_hash') != ph:
                errs.append(f'{where} plan/plan_hash mismatch')
            if i is None or not (0 <= i < len(specs)):
                errs.append(f'{where} cell id out of range'); continue
            if x.get('g') != specs[i]:
                errs.append(f'{where} cell spec differs from plan')
            if x.get('rep_block') != (E.GO_BLOCK if d['kind'] == 'go' else E.rep_block(specs[i])):
                errs.append(f'{where} rep_block differs')
            want = [[d['base_seed'], d['plan_code'], i, 0]] if streams == 1 else \
                [[d['base_seed'], d['plan_code'], i, s] for s in range(1, streams + 1)]
            got = [x['seed']] if streams == 1 else x['seed']
            if got != want:
                errs.append(f'{where} seed identity {got} != {want}')
            if x.get('run_level') == 'SMOKE' and x.get('evidence_eligible'):
                errs.append(f'{where} SMOKE record marked evidence_eligible')
    missing = sorted(expect - set(seen))
    extra = sorted(set(seen) - expect)
    if missing:
        errs.append(f'MISSING {len(missing)} cells: {missing[:20]}')
    if extra:
        errs.append(f'UNEXPECTED {len(extra)} cells: {extra[:20]}')
    return errs, seen


def main(argv):
    plan = argv[0]
    opt = lambda k, dflt=None: argv[argv.index(k) + 1] if k in argv else dflt
    reps = int(opt('--reps'))
    streams = int(opt('--streams', 1))
    cells = [int(c) for c in opt('--cells').split(',')] if opt('--cells') else None
    K = json.load(open(opt('--K'))) if opt('--K') else None
    out = opt('--out')
    skip = {'--reps', '--streams', '--cells', '--K', '--out'}
    files = [a for i, a in enumerate(argv[1:], 1) if a not in skip and argv[i - 1] not in skip]
    errs, seen = verify(plan, reps, streams, cells, K, files)
    if errs:
        print('MERGE VERIFY FAIL'); [print(' ', e) for e in errs]
        return 1
    lines = [json.dumps(seen[i][1], sort_keys=True) for i in sorted(seen)]
    if out:
        open(out, 'w').write('\n'.join(lines) + '\n')
    print('MERGE VERIFY PASS cells', len(lines), 'digest', hashlib.sha256('\n'.join(lines).encode()).hexdigest())
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
