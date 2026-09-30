"""Superpopulation attack: estimand theta = E[N]/E[C] (spec 5.1) over R*'s prospective trade distribution.
Rare sub-cent legs (c = 0.001) arrive at rate r per trade; the realised window often contains none, so M_tail = 0."""
import sys, json, math, numpy as np
from multiprocessing import Pool
from astra_d4 import *
TRUE_DGP = (0.05, 0.05, 0.10)

def one(rng, r, p_tail, th_core, c_tail=0.001):
    S, D = 48, 120
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), rng.poisson(35, D)); N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(0.35, 0.80, N)
    t = rng.random(N) < r
    c[t] = c_tail
    d = finish(dict(date=date, st=st, c=c, C=np.full(N, 50.0), S=S, D=D))
    p = np.where(d['tail'], p_tail, c * (1 + th_core))
    return d, p

def run(cfg):
    name, r, p_tail, th_core, target_pop, thr_kind, R, seed = cfg
    rng = np.random.default_rng(seed)
    th_pop = (1 - r) * th_core + r * (p_tail / 0.001 - 1)
    acc = dict(GO=0, INFO=0, GO_INFO=0, excl=0, cov_cond=0, cov_pop=0, zero_tail=0)
    for _ in range(R):
        d, p = one(rng, r, p_tail, th_core)
        rd = op_ready(d)
        prep(d)
        Y = (latent_uniforms(rng, d, 1, TRUE_DGP) < p).astype(float)
        o = analyse_batch(d, Y)
        core = ~d['tail']
        X = (Y - d['c'])[:, core]; e = X - X.mean(1, keepdims=True); nc = core.sum()
        viid = nc / (nc - 1) * (e ** 2).sum(1) / nc ** 2
        info = bool((o['se_k'][0] <= 0.025) and (o['se_k'][0] ** 2 / viid[0] <= 6))
        cnt = np.bincount(d['st']); cnt = cnt[cnt > 0]
        info = info and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
        thr = ERT if thr_kind == 'ERT' else max(rd['pce'], ERT)
        U = o['U_new'][0]
        th_cond = float((d['n'] * (p - d['c'])).sum() / d['C'].sum())
        acc['GO'] += rd['GO']; acc['INFO'] += info; acc['GO_INFO'] += rd['GO'] and info
        acc['excl'] += rd['GO'] and info and U < thr
        acc['cov_cond'] += th_cond <= U; acc['cov_pop'] += th_pop <= U
        acc['zero_tail'] += not d['tail'].any()
    out = dict(name=name, r=r, expected_tail_legs=round(r * 4200, 2), p_tail=p_tail, theta_core=th_core,
               theta_pop=round(th_pop, 4), threshold=thr_kind, R=R)
    for k, v in acc.items(): out[k] = mc(v / R, R)
    out['excl_given_GO_INFO'] = mc(acc['excl'] / max(acc['GO_INFO'], 1), max(acc['GO_INFO'], 1))
    return out

def rate(p_tail, th_core, target):   # solve (1-r) th_core + r (p/0.001 - 1) = target
    return (target - th_core) / (p_tail / 0.001 - 1 - th_core)

SC = [
 ('S1 p=0.17 core=-0.05 pop=0.025 ERT', 0.17, -0.05, 0.025, 'ERT'),
 ('S2 p=0.17 core=-0.10 pop=0.025 ERT', 0.17, -0.10, 0.025, 'ERT'),
 ('S3 p=0.50 core=-0.10 pop=0.025 ERT', 0.50, -0.10, 0.025, 'ERT'),
 ('S4 p=0.50 core=-0.05 pop=0.025 ERT', 0.50, -0.05, 0.025, 'ERT'),
 ('S5 p=0.05 core=-0.05 pop=0.025 ERT', 0.05, -0.05, 0.025, 'ERT'),
 ('S6 p=1.00 core=-0.10 pop=0.025 ERT', 1.00, -0.10, 0.025, 'ERT'),
 ('S7 p=0.50 core=-0.10 pop=0.05 ERT', 0.50, -0.10, 0.05, 'ERT'),
 ('S8 p=0.50 core=0.00 pop=0.10 PCE', 0.50, 0.00, 0.10, 'PCE'),
 ('S9 p=0.17 core=0.00 pop=0.10 PCE', 0.17, 0.00, 0.10, 'PCE'),
]
if __name__ == '__main__':
    R = int(sys.argv[1])
    cfgs = [(n, rate(p, tc, tg), p, tc, tg, k, R, 950_000 + i) for i, (n, p, tc, tg, k) in enumerate(SC)]
    with Pool(4) as pool:
        for o in pool.imap(run, cfgs):
            print(json.dumps(o), flush=True)
