"""Honest old-vs-new benchmark (speed and peak RAM). Each measurement is a fresh subprocess (clean RSS high-water mark),
single process, same cell spec, same reps, same machine, run sequentially. Old = V2 P1 engine from git (unmodified).
The new engine's outputs are different Monte-Carlo draws of the same estimand, so only cost is compared here
(correctness lives in the equivalence reports).

  python3 wf_bench.py            -> BENCHMARK_REPORT.json (+ prints a table)
"""
import importlib.util
import json
import os
import resource
import subprocess
import sys
import tempfile
import time

import wf_engine as E
import wf_equiv_kernel as K1

HERE = os.path.dirname(os.path.abspath(__file__))
REPS = 2000
CELLS = [
    ('light  m17 thin mid, no persistence', E.G(cap='thin', th=0.10, pr='mid')),
    ('class  m17 thin fav box30 rv.10 +30 paused', E.G(cap='thin', th=0.10, pr='fav', pk='box', pp=30, rv=0.10, P=30, lay='run')),
    ('class  m17 full mid mk .9 rv.05', E.G(cap='full', th=0.10, pr='mid', pk='mk', pp=0.9, rv=0.05)),
    ('m35    thin fav85 ar.9 rv.10 +30 paused', E.G(m=35, cap='thin', th=0.10, pr='fav85', pk='ar', pp=0.9, rv=0.10, P=30, lay='run')),
    ('m55    full mid, go none', E.G(m=55, cap='full', th=0.12, pr='mid', go='none')),
    ('m96    full mid ar.9 rv.05, go none (heavy)', E.G(m=96, cap='full', th=0.10, pr='mid', pk='ar', pp=0.9, rv=0.05, go='none')),
    ('D60    m17 thin mid mk .9 rv.10 +30 paused', E.G(D=60, cap='thin', th=0.10, pr='mid', pk='mk', pp=0.9, rv=0.10, P=30, lay='run')),
]
KC = dict(z_eff=7.2, se_kappa_ceiling=0.005)


def worker(which, idx):
    g = CELLS[idx][1]
    t = time.perf_counter()
    if which == 'new':
        seed, rb, ds, A = E.run_cell_stream(g, KC, 1, 2, idx, 0, REPS)
        rec = E.stream_record('b', idx, g, REPS, seed, rb, ds, A)
    else:
        scratch = tempfile.mkdtemp()
        p1, _, _ = K1.load_reference(K1.REF, scratch)
        t = time.perf_counter()
        rec = p1.run_cell('m3_class', idx, g, REPS, 0, KC)
    sec = time.perf_counter() - t
    print(json.dumps(dict(sec=sec, rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, reach=rec['reach']['p'])))


def main():
    rows = []
    for i, (name, _) in enumerate(CELLS):
        row = dict(cell=name, reps=REPS)
        for which in ('old', 'new'):
            r = subprocess.run([sys.executable, __file__, 'worker', which, str(i)], capture_output=True, text=True, cwd=HERE)
            row[which] = json.loads(r.stdout.strip().splitlines()[-1])
        row['speedup'] = round(row['old']['sec'] / row['new']['sec'], 2)
        row['ram_ratio_new_over_old'] = round(row['new']['rss_mb'] / row['old']['rss_mb'], 2)
        rows.append(row)
        print(f"{name:50s} old {row['old']['sec']:7.2f}s {row['old']['rss_mb']:6.0f}MB | new {row['new']['sec']:7.2f}s "
              f"{row['new']['rss_mb']:6.0f}MB | speedup x{row['speedup']}", flush=True)
    rep = dict(reps=REPS, cpu=os.cpu_count(), rows=rows,
               total_old_sec=round(sum(r['old']['sec'] for r in rows), 2), total_new_sec=round(sum(r['new']['sec'] for r in rows), 2))
    rep['overall_speedup'] = round(rep['total_old_sec'] / rep['total_new_sec'], 2)
    json.dump(rep, open(os.path.join(HERE, 'BENCHMARK_REPORT.json'), 'w'), indent=1)
    print('overall speedup x', rep['overall_speedup'])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        worker(sys.argv[2], int(sys.argv[3]))
    else:
        main()
