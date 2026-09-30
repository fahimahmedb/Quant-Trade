"""C2 reproduction under the retired R1 rule and the frozen R2 rule; observed-count stratification. Seeds 991_000+."""
import sys, json, numpy as np
from multiprocessing import Pool
import astra_c2r2 as a

def r_for(thP, th0, c_t, p_t): return (thP - th0) / (p_t / c_t - 1 - th0)
SC = [
 dict(name='S1 p=0.17 core=-0.05 thP=0.025', m=35, th0=-0.05, kind='rare_tail_trade', c_t=0.001, p_t=0.17, r=r_for(0.025, -0.05, 0.001, 0.17), thP=0.025),
 dict(name='p=0.50 core=-0.10 thP=0.025', m=35, th0=-0.10, kind='rare_tail_trade', c_t=0.001, p_t=0.5, r=r_for(0.025, -0.10, 0.001, 0.5), thP=0.025),
 dict(name='p=1.00 core=-0.10 thP=0.025', m=35, th0=-0.10, kind='rare_tail_trade', c_t=0.001, p_t=1.0, r=r_for(0.025, -0.10, 0.001, 1.0), thP=0.025),
 dict(name='PCE p=0.50 core=0 thP=0.10', m=35, th0=0.0, kind='rare_tail_trade', c_t=0.001, p_t=0.5, r=r_for(0.10, 0.0, 0.001, 0.5), thP=0.10),
 dict(name='jackpot date K=96 p=1 core=-0.10 thP=0.025', m=35, th0=-0.10, kind='jackpot', K=96, c_t=0.001, p_t=1.0),
]
def job(args):
    sc, reps, seed = args
    rng = np.random.default_rng(seed)
    if sc['kind'] == 'jackpot':
        # eta so theta_P = 0.025: ordinary date mass 35*50*(-0.10); jackpot date mass 96*50*(951.4... uses c_t=0.001 -> 999)
        A = 35 * 50.0; B = 96 * 50.0; g = 1 / sc['c_t'] - 1; th0 = sc['th0']; t = 0.025
        sc = dict(sc, eta=(A * (t - th0)) / (A * (t - th0) + B * (g - t)), thP=0.025)
    out = a.run(sc, reps, seed)
    # observed-count stratification (retired R1 rule vs R2), rerun with same seed family
    by = {}
    rng = np.random.default_rng(seed + 1)
    for _ in range(reps):
        w, op = a.draw(rng, sc); pce, go = a.ready(op)
        o = a.labels(w, a.outcomes(rng, w, (0.05, 0.05, 0.10)), pce, go)
        k = int(((w['c'] < 0.002)).sum()); k = k if k < 10 else 10
        b = by.setdefault(k, [0, 0, 0, 0]); b[0] += 1; b[1] += o['r1_excl']; b[2] += o['eco'] not in (
            'PROSPECTIVE_VALUE_CONFIRMED', 'PROSPECTIVE_VALUE_NOT_ROBUST', 'PROSPECTIVE_VALUE_INDETERMINATE', 'NOT_REACHED'); b[3] += o['reach'] and o['U_W'] < 0
    out['by_observed_subcent'] = {k: dict(n=v[0], r1_false_excl=round(v[1] / v[0], 4), r2_prospective_excl=v[2], rw_loss_confirmed=round(v[3] / v[0], 4)) for k, v in sorted(by.items())}
    return json.dumps(out)
if __name__ == '__main__':
    reps = int(sys.argv[1])
    with Pool(4) as p:
        for line in p.imap(job, [(sc, reps, 991_000 + 10 * i) for i, sc in enumerate(SC)]):
            print(line, flush=True)
