"""Refinement of the worst false-confirmation cells at theta_P = -0.005 (strictly inside the null), 20,000 reps each.
Seeds 996_000+. Also reports the conditional rate given a reachable analysis state."""
import json, sys
from multiprocessing import Pool
import astra_c2r2 as a
from run_confirm_attack import eta_for
CELLS = [
 ('date96', 17, 'thin', 0.10), ('date96', 17, 'thin', 0.05), ('date96', 35, 'thin', 0.08),
 ('date96', 17, 'full', 0.05), ('date96', 35, 'full', 0.03), ('template48', 17, 'full', 0.04),
 ('dateM', 17, 'full', 0.04), ('dateM', 35, 'full', 0.02),
]
def mk(var, m, capm, th0):
    K = {'date96': 96, 'template48': 48, 'dateM': m}[var]
    return dict(name=f'REFINE cat {var} m={m} cap={capm} th0={th0} thP=-0.005', m=m, th0=th0, kind='catastrophe', K=K,
                cap=capm, eta=eta_for(m, th0, K, capm, target=-0.005), thP=-0.005)
def job(args):
    sc, reps, seed = args
    # 20,000 reps split in 5 chunks with distinct seeds for a chunk-level stability check
    parts = [a.run(sc, reps // 5, seed + k) for k in range(5)]
    tot = {}
    for key in ('conf', 'reach', 'fwd', 'zero_sp', 'notrob'):
        k = sum(round(p[key]['p'] * p[key]['n']) for p in parts); tot[key] = a.mc(k, reps)
    tot['conf_given_reach'] = a.mc(sum(round(p['conf']['p'] * p['conf']['n']) for p in parts),
                                   max(1, sum(round(p['reach']['p'] * p['reach']['n']) for p in parts)))
    tot['chunk_conf'] = [p['conf']['p'] for p in parts]
    return json.dumps(dict(sc=sc, reps=reps, seed=seed, theta_P=-0.005, **tot))
if __name__ == '__main__':
    reps = int(sys.argv[1])
    with Pool(4) as p:
        for line in p.imap(job, [(mk(*c), reps, 996_000 + 100 * i) for i, c in enumerate(CELLS)]):
            print(line, flush=True)
