"""Core-bound coverage stress + boundary + PCE (tail empty unless stated). Conditional-on-design truth."""
import sys, json, math, numpy as np
from multiprocessing import Pool
from astra_d4 import *

RHO = {'TRUE': (0.05, 0.05, 0.10), 'DATE': (0.30, 0.02, 0.10), 'STATION': (0.02, 0.30, 0.10),
       'MIXED': (0.15, 0.15, 0.10), 'REGIME': (0.05, 0.05, 0.10)}

def gen(rng, D, S, m, shape, dom_st, dom_blk, prices, capital):
    act = rng.gamma(shape, 1.0, S); act /= act.sum()
    if dom_st:
        act = act * (1 - dom_st) / (act.sum() - act[0]) ; act[0] = dom_st; act /= act.sum()
    per = rng.poisson(m, D).astype(float)
    if dom_blk:     # dates 0-4 (one block) carry dom_blk of all trades
        tot = per.sum(); per[:5] = 0; rest = per.sum(); per[:5] = dom_blk * rest / (1 - dom_blk) / 5
        per = np.round(per).astype(int)
    per = per.astype(int)
    date = np.repeat(np.arange(D), per); N = date.size
    st = rng.choice(S, N, p=act)
    if prices == 'std': c = rng.uniform(0.35, 0.80, N)
    elif prices == 'fav': c = rng.uniform(0.60, 0.90, N)
    elif prices == 'boundary':
        c = rng.uniform(0.35, 0.80, N); b = rng.random(N) < 0.06; c[b] = rng.uniform(0.04, 0.06, b.sum())
    elif prices == 'wide': c = np.exp(rng.uniform(np.log(0.04), np.log(0.90), N))
    if capital == 'uniform': C = np.full(N, 50.0)
    elif capital == 'partial': C = np.where(rng.random(N) < 0.68, 50.0, rng.uniform(10, 50, N))
    elif capital == 'concentrated': C = np.where(rng.random(N) < 0.5, 50.0, rng.uniform(1, 5, N))
    return finish(dict(date=date, st=st, c=c, C=C, S=S, D=D))

def truth(d, kind, target, rng):
    c, n, C = d['c'], d['n'], d['C']
    if kind == 'uniform':
        p = c * (1 + target)
    elif kind in ('boundary_hidden', 'dominant_station_edge', 'station_het', 'favourite_skew'):
        if kind == 'boundary_hidden':
            b = c < 0.06; base = 0.97
        elif kind == 'dominant_station_edge':
            b = d['st'] == 0; base = 0.97
        elif kind == 'favourite_skew':
            b = c > 0.8; base = 0.99
        if kind == 'station_het':
            delta = rng.normal(0, 0.15, d['S'])[d['st']]
            p = np.clip(c * (1 + delta), 0.001, 0.999)
            # rescale to hit target exactly: add uniform shift
            cur = (n * (p - c)).sum() / C.sum()
            p = np.clip(p + (target - cur) * c, 0.0, 1.0)
        else:
            p = base * c
            need = target * C.sum() - (n * (p - c)).sum()
            k = need / (n[b] * p[b]).sum()
            p[b] = np.minimum(1.0, p[b] * (1 + k))
    return p

def run(cfg):
    name, D, S, m, shape, dom_st, dom_blk, prices, capital, kind, target, rho, R, seed = cfg
    rng = np.random.default_rng(seed)
    per_design = 100
    acc = dict(cov_core=0, cov=0, excl=0, excl_info=0, infosuff=0, lt_pce=0)
    ths = []; kish_bad = 0; done = 0; dfs = []
    while done < R:
        d = gen(rng, D, S, m, shape, dom_st, dom_blk, prices, capital)
        cnt = np.bincount(d['st']); cnt = cnt[cnt > 0]
        kish = cnt.sum() ** 2 / (cnt ** 2).sum()
        if cnt.size < 25 or kish < 15 or np.unique(d['blk']).size < 12:
            kish_bad += 1; continue
        prep(d)
        p = truth(d, kind, target, rng)
        th = float((d['n'] * (p - d['c'])).sum() / d['C'].sum()); ths.append(th)
        core = ~d['tail']; thc = float((d['n'][core] * (p - d['c'])[core]).sum() / d['C'][core].sum())
        Y = (latent_uniforms(rng, d, per_design, RHO[rho], extra='regime' if rho == 'REGIME' else None) < p).astype(float)
        o = analyse_batch(d, Y)
        # IF4 / IF5
        X = (Y - d['c'])[:, core]; e = X - X.mean(1, keepdims=True); ncore = core.sum()
        viid = ncore / (ncore - 1) * (e ** 2).sum(1) / ncore ** 2
        info = (o['se_k'] <= 0.025) & (o['se_k'] ** 2 / viid <= 6)
        acc['cov_core'] += (thc <= o['U_core']).sum(); acc['cov'] += (th <= o['U_new']).sum()
        acc['excl'] += (o['U_new'] < ERT).sum(); acc['excl_info'] += ((o['U_new'] < ERT) & info).sum()
        acc['lt_pce'] += ((o['U_new'] < target) & info).sum()
        acc['infosuff'] += info.sum()
        done += per_design
    out = dict(name=name, D=D, S=S, m=m, rho=rho, kind=kind, prices=prices, capital=capital, dom_st=dom_st,
               dom_blk=dom_blk, target=target, R=done, theta_true_mean=round(float(np.mean(ths)), 4),
               designs_rejected_by_IF3_IF2=kish_bad)
    for k, v in acc.items(): out[k] = mc(v / done, done)
    return out

BASE = dict(D=120, S=48, m=35, shape=2.0, dom_st=0, dom_blk=0, prices='std', capital='partial')
def C(name, kind='uniform', target=0.02, rho='TRUE', R=4000, **kw):
    b = dict(BASE); b.update(kw)
    return (name, b['D'], b['S'], b['m'], b['shape'], b['dom_st'], b['dom_blk'], b['prices'], b['capital'], kind, target, rho, R)

MIN = dict(D=60, S=25, m=35)
PLAN = {
 'coverage': [
  C('G01 120/48 TRUE'), C('G02 120/48 strong date', rho='DATE'), C('G03 120/48 strong station', rho='STATION'),
  C('G04 120/48 mixed', rho='MIXED'), C('G05 120/48 regime spanning blocks', rho='REGIME'),
  C('G06 120/48 unequal stations (gamma 0.7)', shape=0.7), C('G07 120/48 dominant station 20%', dom_st=0.20),
  C('G08 120/48 dominant date block 25%', dom_blk=0.25), C('G09 120/48 favourite-skew', kind='favourite_skew', prices='fav'),
  C('G10 120/48 boundary hidden edge', kind='boundary_hidden', prices='boundary'),
  C('G11 120/48 station-heterogeneous edge', kind='station_het'),
  C('G12 120/48 edge only at dominant station', kind='dominant_station_edge', dom_st=0.20),
  C('G13 120/48 concentrated capital', capital='concentrated'),
  C('M01 60/25 TRUE', **MIN), C('M02 60/25 strong date', rho='DATE', **MIN), C('M03 60/25 strong station', rho='STATION', **MIN),
  C('M04 60/25 mixed', rho='MIXED', **MIN), C('M05 60/25 regime', rho='REGIME', **MIN),
  C('M06 60/25 dominant station 12%', dom_st=0.12, **MIN), C('M07 60/25 dominant block 25%', dom_blk=0.25, **MIN),
  C('M08 60/25 boundary hidden', kind='boundary_hidden', prices='boundary', **MIN),
  C('M09 60/25 favourite-skew', kind='favourite_skew', prices='fav', **MIN),
  C('M10 60/25 m=17 mixed wide prices', rho='MIXED', prices='wide', D=60, S=25, m=17),
  C('M11 60/25 edge at dominant station, station dep', kind='dominant_station_edge', dom_st=0.12, rho='STATION', **MIN),
 ],
 'boundary': [C(f'B {t} {g}', target=t, rho=r, **(MIN if g=='min' else {})) for t in (0.02, 0.021, 0.025, 0.03)
              for g, r in (('std', 'TRUE'), ('min', 'TRUE'), ('min', 'MIXED'), ('min', 'STATION'))],
 'pce': [C(f'P {t} {g}', target=t, rho=r, **(MIN if g=='min' else {})) for t in (0.05, 0.07, 0.08, 0.10)
         for g, r in (('std', 'TRUE'), ('min', 'MIXED'))],
}
if __name__ == '__main__':
    which = sys.argv[1]
    cfgs = [c + (940_000 + 1000 * list(PLAN).index(which) + i,) for i, c in enumerate(PLAN[which])]
    with Pool(4) as pool:
        for r in pool.imap(run, cfgs):
            print(json.dumps(r), flush=True)
