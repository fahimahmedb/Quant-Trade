"""False PROSPECTIVE_VALUE_CONFIRMED search: common profitable core + rare catastrophic dates, theta_P = 0 exactly
(or slightly below). Seeds 990_000+. Usage: python3 run_confirm_attack.py scan REPS | refine REPS"""
import sys, json, numpy as np
from multiprocessing import Pool
import astra_c2r2 as a
EC = {'full': 50.0, 'partial': 0.68 * 50 + 0.32 * 30, 'thin': 15.0}

def eta_for(m, th0, K, capm, target=0.0):
    # solve [(1-eta) m E[C] th0 - eta K 50] / [(1-eta) m E[C] + eta K 50] = target
    A = m * EC[capm]; B = K * 50.0
    return (A * th0 - target * A) / (A * th0 - target * A + B * (1 + target))

def cfg_list():
    out = []
    for m in (17, 35):
        for capm in ('full', 'thin'):
            for K, var in ((96, 'date96'), (48, 'template48'), (m, 'dateM')):
                for th0 in (0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10):
                    out.append(dict(name=f'cat {var} m={m} cap={capm} th0={th0}', m=m, th0=th0, kind='catastrophe', K=K,
                                    cap=capm, eta=eta_for(m, th0, K, capm), thP=0.0))
        # station-comonotone catastrophe (all catastrophe trades at one station), date-comonotone
        for th0 in (0.03, 0.05):
            out.append(dict(name=f'cat station-one m={m} th0={th0}', m=m, th0=th0, kind='catastrophe', K=96, cap='full',
                            eta=eta_for(m, th0, 96, 'full'), thP=0.0, special_station_one=True))
    return out

def job(args):
    sc, reps, seed = args
    return json.dumps(a.run(sc, reps, seed))

if __name__ == '__main__':
    mode, reps = sys.argv[1], int(sys.argv[2])
    if mode == 'scan':
        jobs = [(sc, reps, 990_000 + i) for i, sc in enumerate(cfg_list())]
    else:
        names = sys.argv[3].split('|')
        cl = {c['name']: c for c in cfg_list()}
        jobs = [(cl[nm], reps, 995_000 + i) for i, nm in enumerate(names)]
    with Pool(4) as p:
        for line in p.imap(job, jobs):
            print(line, flush=True)
