"""Weather V3 / S0 - slice driver.

  python3 wf_run.py run PLAN --reps N --out FILE [--streams 1|5] [--slice i/n] [--cells 3,7,9] [--procs P] [--K consts.json]
                          [--timing FILE]

* One self-contained JSONL record per cell; deterministic content only (no wall-clock, host or process fields) so records are
  bit-identical across slicings, process counts and completion order. Timing goes to the optional --timing sidecar.
* --slice i/n  : this process handles cells with cell_id % n == i (i in 0..n-1).
* Resume-safe  : cells already present in --out (same plan_hash, reps, streams) are skipped; a torn last line left by a killed
  run is truncated away first and recomputed. Each record is flushed + fsynced as it completes.
* --streams 1  : stream id 0, `reps` replications (RESEARCH). --streams 5: independent streams 1..5 of reps//5 each, combined
  (CONFIRM, same arithmetic as V2 `cell`).
* Run level: reps <= 1000 -> SMOKE (code-failure detection only; record carries evidence_eligible=false), 20,000 <= reps < 100,000
  -> RESEARCH, reps >= 100,000 -> CONFIRM, otherwise NONSTANDARD.
* At most 4 processes (hard cap).
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import wf_engine as E
import wf_plans as P

MAX_PROCS = 4


def run_level(reps):
    if reps <= 1000:
        return 'SMOKE'
    if 20000 <= reps < 100000:
        return 'RESEARCH'
    if reps >= 100000:
        return 'CONFIRM'
    return 'NONSTANDARD'


def parse_slice(s):
    i, n = s.split('/')
    i, n = int(i), int(n)
    assert n >= 1 and 0 <= i < n, 'slice must be i/n with 0 <= i < n'
    return i, n


def compute_record(plan, cell_id, reps, streams, K):
    """Pure function of (plan, cell_id, reps, streams, K). This is the unit of determinism."""
    d = P.PLAN_DEFS[plan]
    g = P.plan_cells(plan)[cell_id]
    if d['kind'] == 'go':
        assert streams == 1
        rec = E.run_go_cell(g, K, d['base_seed'], d['plan_code'], cell_id, reps)
    elif streams == 1:
        seed, rb, dsum, A = E.run_cell_stream(g, K, d['base_seed'], d['plan_code'], cell_id, 0, reps)
        rec = E.stream_record(plan, cell_id, g, reps, seed, rb, dsum, A)
    else:
        parts = []
        for s in range(1, streams + 1):
            seed, rb, dsum, A = E.run_cell_stream(g, K, d['base_seed'], d['plan_code'], cell_id, s, reps // streams)
            parts.append(E.stream_record(plan, cell_id, g, reps // streams, seed, rb, dsum, A))
        rec = E.combine(parts, plan, cell_id, g)
    rec['plan'] = plan
    rec['schema'] = E.SCHEMA_VERSION
    rec['engine'] = E.ENGINE_VERSION
    rec['plan_hash'] = P.plan_hash(plan, K)
    rec['streams'] = streams
    rec['run_level'] = run_level(reps)
    rec['evidence_eligible'] = rec['run_level'] != 'SMOKE'
    return rec


def _job(a):
    t = time.time()
    rec = compute_record(*a)
    return json.dumps(rec, sort_keys=True), a[1], time.time() - t


def repair_torn_tail(path):
    """Truncate a partial last line (no trailing newline) left by a killed run."""
    if not os.path.exists(path):
        return 0
    with open(path, 'rb+') as f:
        data = f.read()
        if not data or data.endswith(b'\n'):
            return 0
        cut = data.rfind(b'\n') + 1
        f.truncate(cut)
        return len(data) - cut


def done_cells(path, plan_hash, reps, streams):
    done = set()
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            try:
                x = json.loads(line)
            except ValueError:
                continue
            if x.get('plan_hash') == plan_hash and x.get('reps') == reps and x.get('streams') == streams:
                done.add(x['idx'])
    return done


def main(argv):
    if argv[0] != 'run':
        raise SystemExit(__doc__)
    plan = argv[1]
    opt = lambda k, dflt=None: argv[argv.index(k) + 1] if k in argv else dflt
    reps = int(opt('--reps', 20000))
    streams = int(opt('--streams', 1))
    out = opt('--out')
    procs = min(MAX_PROCS, int(opt('--procs', MAX_PROCS)))
    K = json.load(open(opt('--K'))) if opt('--K') else None
    sl = parse_slice(opt('--slice', '0/1'))
    ncell = len(P.plan_cells(plan))
    cells = [int(x) for x in opt('--cells').split(',')] if opt('--cells') else list(range(ncell))
    mine = [c for c in cells if c % sl[1] == sl[0]]
    assert streams in (1, 5) and (streams == 1 or reps % streams == 0)
    torn = repair_torn_tail(out)
    ph = P.plan_hash(plan, K)
    done = done_cells(out, ph, reps, streams)
    todo = [c for c in mine if c not in done]
    print(f'plan {plan} hash {ph[:12]} cells {ncell} slice {sl[0]}/{sl[1]} mine {len(mine)} done {len(mine) - len(todo)} '
          f'todo {len(todo)} torn_bytes_dropped {torn} level {run_level(reps)}', flush=True)
    tim = open(opt('--timing'), 'a') if opt('--timing') else None
    jobs = [(plan, c, reps, streams, K) for c in todo]
    with Pool(procs) as pool, open(out, 'a') as f:
        for line, c, sec in pool.imap_unordered(_job, jobs):
            f.write(line + '\n')
            f.flush()
            os.fsync(f.fileno())
            if tim:
                tim.write(json.dumps(dict(plan=plan, cell=c, reps=reps, sec=round(sec, 3))) + '\n')
                tim.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
