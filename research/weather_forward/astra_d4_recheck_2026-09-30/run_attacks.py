import sys, json, numpy as np
from astra_d4 import *
TRUE_DGP = (0.05, 0.05, 0.10)

def attack(name, R, seed, design_seed=930_777):
    d = prep(design_astra_A(np.random.default_rng(design_seed)))
    rd = op_ready(d)
    tab, W0 = retired_lookup(d)
    c = d['c']; p = c.copy(); tail = d['tail']
    if name == 'A1': p[~tail] = 0.95 * c[~tail]; p[d['cheap']] = 0.170
    if name == 'A2': p[d['cheap']] = 0.18
    if name == 'P3': p[~tail] = 0.90 * c[~tail]
    th = float((d['n'] * (p - c)).sum() / d['C'].sum())
    rng = np.random.default_rng(seed)
    acc = {k: 0 for k in ['cov_old','cov_new','exERT_old','exERT_new','exPCE_old','exPCE_new','rej_old','rej_new','T2','NEG','T1','negInfo']}
    done = 0
    while done < R:
        r = min(500, R - done)
        Y = (latent_uniforms(rng, d, r, TRUE_DGP) < p).astype(float)
        o = analyse_batch(d, Y)
        pT1b = (1 + (W0[None, :] >= o['W'][:, None]).sum(1)) / (W0.size + 1)
        T1 = o['T1a'] | (pT1b <= 0.025)
        Uold = o['wc'] * o['U_core'] + (1 - o['wc']) * tab[o['W']]
        Unew = o['U_new']
        def eco(U):
            return np.where(U < ERT, 'EXCL', np.where(o['T2'] & (o['theta_hat'] >= ERT), np.where(o['gate'], 'CONF', 'NROB'), 'IND'))
        eo, en = eco(Uold), eco(Unew)
        negInfo = (~T1) & o['NEG']
        pce = max(rd['pce'], ERT)
        acc['cov_old'] += (th <= Uold).sum(); acc['cov_new'] += (th <= Unew).sum()
        acc['exERT_old'] += (Uold < ERT).sum(); acc['exERT_new'] += (Unew < ERT).sum()
        acc['exPCE_old'] += (Uold < pce).sum(); acc['exPCE_new'] += (Unew < pce).sum()
        acc['rej_old'] += ((eo == 'EXCL') | (negInfo & (eo != 'CONF'))).sum()
        acc['rej_new'] += (en == 'EXCL').sum()
        acc['T2'] += o['T2'].sum(); acc['NEG'] += o['NEG'].sum(); acc['T1'] += T1.sum(); acc['negInfo'] += negInfo.sum()
        done += r
    out = {k: mc(v / R, R) for k, v in acc.items()}
    out.update(scenario=name, R=R, theta_true=round(th, 4), M_tail=round(o['M_tail'], 4), readiness=rd,
               retired_lookup_W0_4=[round(x, 4) for x in tab[:5]])
    return out

if __name__ == '__main__':
    name, R, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    print(json.dumps(attack(name, R, seed)))
