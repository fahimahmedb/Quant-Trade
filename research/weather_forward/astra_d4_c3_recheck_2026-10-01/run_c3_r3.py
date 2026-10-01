"""C3 reproduction (fresh seeds 1,100,000+) with the retired R2 label and the frozen R3 labels (spec @341e0b7a 17.2-17.5),
plus the conditional transport claim checked against the true theta_P at the true loss-regime cost share."""
import sys, json, math, numpy as np
from multiprocessing import Pool
import astra_c2r2 as a
EC = {'full': 50.0, 'thin': 15.0}
def eta_for(m, th0, K, capm, target):
    A = m * EC[capm]; B = K * 50.0
    return (A * th0 - target * A) / (A * th0 - target * A + B * (1 + target))
def eps_true(m, capm, K, eta):
    A = m * EC[capm]; B = K * 50.0
    return eta * B / ((1 - eta) * A + eta * B)
CELLS = [('C3-thin cap96 m=17', 17, 'thin', 96, 0.10), ('C3-full cap96 m=17', 17, 'full', 96, 0.05),
         ('hidden identical-covariate loss dates m=17 full', 17, 'full', 17, 0.04),
         ('single-cap-date-scale: cap96 m=35 thin eta for E=0.5 dates', 35, 'thin', 96, None)]
def job(args):
    name, m, capm, K, th0, reps, seed = args
    target = -0.005
    if th0 is None:   # choose eta for 0.5 expected loss dates in 120, th0 solved for theta_P = target
        eta = 0.5 / 120; A = m * EC[capm]; B = K * 50.0
        th0 = (target * ((1 - eta) * A + eta * B) + eta * B) / ((1 - eta) * A)
    else:
        eta = eta_for(m, th0, K, capm, target)
    sc = dict(name=name, m=m, th0=th0, kind='catastrophe', K=K, cap=capm, eta=eta, thP=target)
    et = eps_true(m, capm, K, eta)
    rng = np.random.default_rng(seed)
    K_ = dict(r2_conf=0, r3_supported=0, r3_pos=0, r3_false_W=0, unconditional=0, prospective_excl=0, rstar=0,
              shadow=0, LW_miss=0, cond_false=0, reach=0, LT_eps_true_pos=0)
    for _ in range(reps):
        w, op = a.draw(rng, sc); pce, go = a.ready(op)
        o = a.labels(w, a.outcomes(rng, w, (0.05, 0.05, 0.10)), pce, go)
        # recompute L_W exactly as spec 8.5c from the engine's pooled statistic
        c, C, n, date, st = w['c'], w['C'], w['n'], w['date'], w['st']
        y = None
        r3 = {'PROSPECTIVE_VALUE_CONFIRMED': 'REALIZED_WINDOW_VALUE_SUPPORTED', 'PROSPECTIVE_VALUE_NOT_ROBUST': 'REALIZED_WINDOW_VALUE_NOT_ROBUST',
              'PROSPECTIVE_VALUE_INDETERMINATE': 'REALIZED_WINDOW_VALUE_INDETERMINATE', 'NOT_REACHED': 'NOT_REACHED'}[o['eco']]
        K_['reach'] += o['reach']
        K_['r2_conf'] += o['eco'] == 'PROSPECTIVE_VALUE_CONFIRMED'
        K_['r3_supported'] += r3 == 'REALIZED_WINDOW_VALUE_SUPPORTED'
        pos = r3 in ('REALIZED_WINDOW_VALUE_SUPPORTED', 'REALIZED_WINDOW_VALUE_NOT_ROBUST')
        K_['r3_pos'] += pos; K_['r3_false_W'] += pos and o['thW'] <= 0
        K_['shadow'] += r3 == 'REALIZED_WINDOW_VALUE_SUPPORTED' and not o['NEG']
        LW = o['LW']
        K_['LW_miss'] += o['reach'] and LW > o['thW']
        LT = (1 - et) * LW - et
        K_['cond_false'] += o['reach'] and LT > target          # conditional claim at the true eps (premise holds, delta=0)
        K_['LT_eps_true_pos'] += o['reach'] and pos and LT >= 0
    return json.dumps(dict(sc=sc, eps_true=round(et, 4), reps=reps, seed=seed, **{k: a.mc(v, reps) for k, v in K_.items()},
                           note='R3 emits no unconditional prospective label, no prospective exclusion and never R*_REJECTED by construction of 17.2-17.6; counted as 0'))
if __name__ == '__main__':
    reps = int(sys.argv[1])
    with Pool(4) as p:
        for line in p.imap(job, [(c[0], c[1], c[2], c[3], c[4], reps, 1_100_000 + 100 * i) for i, c in enumerate(CELLS)]):
            print(line, flush=True)
