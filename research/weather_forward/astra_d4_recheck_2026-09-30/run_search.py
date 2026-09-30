"""Adversarial random search over the conditional (fixed trade-set) admissible class. Checks, per replication, the
deterministic invariant  [U < thr <= theta]  =>  [U_core < theta_core]  and records false-exclusion rates."""
import sys, json, math, numpy as np
from multiprocessing import Pool
from astra_d4 import *
FRACS = [0, 0.0002, 0.0005, 0.001, 0.01, 0.02, 0.05, 0.10, 0.16, 0.25, 0.40]
TPRICE = [0.001, 0.002, 0.005, 0.01, 0.02, 0.039]
CORE_EFF = [-0.15, -0.10, -0.05, 0.0, 0.02]
TMULT = ['zero', 'implied', '2', '5', '10', 'one', 'tune', 'tune', 'tune', 'tune', 'tune', 'tune']
DEP = ['indep', 'date', 'station', 'perfect_tail', 'jackpot']
CAP = ['uniform', 'concentrated', 'dominant_tail']
GEOM = [(120, 48, 35), (60, 25, 35), (60, 25, 17)]

def config(rng):
    return dict(frac=float(rng.choice(FRACS)), tp=float(rng.choice(TPRICE)), ce=float(rng.choice(CORE_EFF)),
                tm=str(rng.choice(TMULT)),
                dep=str(rng.choice(DEP)), cap=str(rng.choice(CAP)), geom=GEOM[rng.integers(3)],
                core_lo=float(rng.choice([0.04, 0.2, 0.35, 0.6])))

def run(args):
    cfg, R, seed = args
    rng = np.random.default_rng(seed)
    D, S, m = cfg['geom']
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), rng.poisson(m, D)); N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(cfg['core_lo'], 0.90, N)
    k = int(round(cfg['frac'] * N)) if cfg['frac'] >= 0.001 else int(rng.poisson(cfg['frac'] * N * 5))
    ti = rng.choice(N, k, replace=False) if k else np.array([], int)
    c[ti] = cfg['tp']
    if cfg['cap'] == 'uniform': C = np.full(N, 50.0)
    elif cfg['cap'] == 'concentrated': C = np.where(rng.random(N) < 0.5, 50.0, rng.uniform(1, 5, N))
    else: C = np.full(N, 10.0); C[ti] = 50.0
    d = prep(finish(dict(date=date, st=st, c=c, C=C, S=S, D=D)))
    tail = d['tail']; core = ~tail
    p = c * (1 + cfg['ce']); p = np.minimum(p, 1)
    tm = cfg['tm']
    pt = {'zero': 0.0, 'implied': cfg['tp'], 'one': 1.0}.get(tm, None)
    if tm == 'tune' and tail.any():   # tail p chosen so that theta sits just above theta_ERT (edge hidden in the tail)
        base = (d['n'][core] * (p - c)[core]).sum()
        pt = cfg['tp'] + ((ERT + 0.001) * C.sum() - base) / d['n'][tail].sum()
        pt = float(np.clip(pt, 0.0, 1.0))
    elif tm == 'tune':
        pt = cfg['tp']
    p[tail] = pt if pt is not None else min(1.0, float(tm) * cfg['tp'])
    th = float((d['n'] * (p - c)).sum() / C.sum())
    thc = float((d['n'][core] * (p - c)[core]).sum() / C[core].sum())
    rho = {'indep': (0.0, 0.0, 0.0), 'date': (0.30, 0.02, 0.10), 'station': (0.02, 0.30, 0.10),
           'perfect_tail': (0.05, 0.05, 0.10), 'jackpot': (0.05, 0.05, 0.10)}[cfg['dep']]
    rd = op_ready(d)
    thrs = {'ERT': ERT, 'PCE': max(rd['pce'], ERT)}
    acc = dict(fERT=0, fPCE=0, viol=0, cov=0)
    Uv = latent_uniforms(rng, d, R, rho)
    if cfg['dep'] in ('perfect_tail', 'jackpot') and tail.any():
        u = rng.random((R, 1))
        Uv[:, tail] = u                         # all tail legs share one uniform: comonotone jackpot
    Y = (Uv < p).astype(float)
    o = analyse_batch(d, Y)
    thc_ok = o['U_core'] >= thc
    for nm, t in thrs.items():
        fe = (o['U_new'] < t) & (th >= t)
        acc['f' + nm] = int(fe.sum())
        acc['viol'] += int((fe & thc_ok).sum())        # false exclusion WITHOUT a core miss => invariant broken
    acc['cov'] = int((th <= o['U_new']).sum())
    return dict(cfg={k: (v if not isinstance(v, tuple) else list(v)) for k, v in cfg.items()}, R=R, N=int(N), k_tail=int(tail.sum()),
                theta=round(th, 4), theta_core=round(thc, 4), M_tail=round(o['M_tail'], 4), GO=rd['GO'], pce=rd['pce'],
                fERT=acc['fERT'] / R, fPCE=acc['fPCE'] / R, viol=acc['viol'], cov=acc['cov'] / R)

if __name__ == '__main__':
    n, R = int(sys.argv[1]), int(sys.argv[2])
    master = np.random.default_rng(960_000)
    jobs = []
    for i in range(n):
        cfg = config(master)
        jobs.append((cfg, R, 961_000 + i))
    with Pool(4) as pool:
        for o in pool.imap_unordered(run, jobs, chunksize=4):
            print(json.dumps(o), flush=True)
