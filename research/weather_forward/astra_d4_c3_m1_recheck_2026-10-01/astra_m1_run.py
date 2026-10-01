"""ASTRA D4-C3-M1 recheck runner. SYNTHETIC ONLY.
Usage: python3 astra_m1_run.py PLAN REPS [CHUNKS]
Seeds: SeedSequence([77100101, plan_code, cell_index, chunk]) -- fresh, distinct from run D/E/F/G and earlier Astra seeds.
Output: one JSON line per cell (counts summed over chunks)."""
import json
import os
import sys
from multiprocessing import Pool

import astra_m1_engine as E

SEED_BASE = 77100101
B = dict(S=48, D=120, m=17, cap='thin', th=0.0)


def G(**kw):
    g = dict(B)
    g.update(kw)
    return g


def P(phi, rv, kind='date'):
    return ((kind, phi, rv),)


def plan_repro():
    return [
        ('M1 false positive: phi0.8 rv0.05 m17 thin th0', G(persist=P(0.8, 0.05))),
        ('M1 miss: phi0.8 rv0.05 m17 full th0.10', G(cap='full', th=0.10, persist=P(0.8, 0.05))),
        ('M1 miss: phi0.8 rv0.05 m17 thin th0.05', G(th=0.05, persist=P(0.8, 0.05))),
        ('M1 miss: phi0.9 rv0.10 m17 thin th0.05', G(th=0.05, persist=P(0.9, 0.10))),
        ('M1 false positive: phi0.9 rv0.10 m17 thin th0', G(persist=P(0.9, 0.10))),
    ]


def plan_class():
    out = []
    for m in (17, 35):
        for cap in ('thin', 'full'):
            for th in (0.0, 0.05, 0.10):
                out.append((f'class baseline m{m} {cap} th{th}', G(m=m, cap=cap, th=th)))
                for phi in (0.5, 0.7, 0.8, 0.9):
                    for rv in (0.02, 0.05, 0.10):
                        out.append((f'class phi{phi} rv{rv} m{m} {cap} th{th}', G(m=m, cap=cap, th=th, persist=P(phi, rv))))
    return out


def plan_worst():
    return [
        ('WORST class phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, persist=P(0.9, 0.05))),
        ('WORST class phi0.9 rv0.05 m17 full th0.10', G(cap='full', th=0.10, persist=P(0.9, 0.05))),
    ]


def plan_beyond():
    out = []
    # 1. between grid points inside the stated bounds (phi <= 0.9, rv <= 0.10): rv and m between grid values
    for m in (12, 17, 20, 25):
        for rv in (0.03, 0.05, 0.07):
            out.append((f'grid-gap phi0.9 rv{rv} m{m} thin th0.10', G(m=m, th=0.10, persist=P(0.9, rv))))
    # 2. outside the class: longer persistence
    out.append(('beyond phi0.95 rv0.05 m17 thin th0', G(persist=P(0.95, 0.05))))
    out.append(('beyond phi0.95 rv0.05 m17 thin th0.10', G(th=0.10, persist=P(0.95, 0.05))))
    out.append(('beyond two-component phi0.5 rv0.05 + phi0.97 rv0.02 m17 thin th0.10',
                G(th=0.10, persist=(('date', 0.5, 0.05), ('date', 0.97, 0.02)))))
    # 3. regime combined with station dependence / hemisphere / station-specific persistence
    out.append(('beyond regime phi0.9 rv0.05 + station rho 0.10 m17 thin th0.10',
                G(th=0.10, rho=(0.05, 0.10, 0.10), persist=P(0.9, 0.05))))
    out.append(('beyond hemisphere regimes phi0.9 rv0.10 m17 thin th0.10', G(th=0.10, persist=P(0.9, 0.10, 'hemi'))))
    out.append(('beyond station-specific AR phi0.9 rv0.10 m17 thin th0.10', G(th=0.10, persist=P(0.9, 0.10, 'station'))))
    # 4. geometry edges
    out.append(('edge min geometry 60/25 phi0.9 rv0.05 m17 thin th0.10', G(D=60, S=25, th=0.10, persist=P(0.9, 0.05))))
    out.append(('edge min geometry 60/25 phi0.9 rv0.05 m35 full th0.10', G(D=60, S=25, m=35, cap='full', th=0.10, persist=P(0.9, 0.05))))
    out.append(('edge 120 counted + 30 paused dates phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, pause=30, persist=P(0.9, 0.05))))
    out.append(('edge dominant station 20% phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, dom_st=0.20, persist=P(0.9, 0.05))))
    out.append(('edge dominant date phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, dom_date=True, persist=P(0.9, 0.05))))
    out.append(('edge heterogeneous returns sd0.10 phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, het=0.10, persist=P(0.9, 0.05))))
    out.append(('edge thick m35 full phi0.9 rv0.02 th0.10', G(m=35, cap='full', th=0.10, persist=P(0.9, 0.02))))
    # 5. price mix (all CORE) at the class edge
    for pr in ('fav', 'low', 'wide', 'barbell'):
        for th in (0.0, 0.10):
            out.append((f'price {pr} phi0.9 rv0.05 m17 thin th{th}', G(prices=pr, th=th, persist=P(0.9, 0.05))))
            out.append((f'price {pr} no persistence m17 thin th{th}', G(prices=pr, th=th)))
    return out


def plan_frozen():
    """T1a / NEG / U_W at the kappa_core = 0 boundary (th = 0) and U_W at negative theta."""
    out = []
    for m, cap in ((17, 'thin'), (17, 'full'), (35, 'full')):
        out.append((f'frozen baseline m{m} {cap} th0', G(m=m, cap=cap)))
        for phi, rv in ((0.8, 0.05), (0.9, 0.02), (0.9, 0.05), (0.9, 0.10)):
            out.append((f'frozen phi{phi} rv{rv} m{m} {cap} th0', G(m=m, cap=cap, persist=P(phi, rv))))
    for pr in ('fav', 'barbell'):
        out.append((f'frozen price {pr} phi0.9 rv0.05 m17 thin th0', G(prices=pr, persist=P(0.9, 0.05))))
        out.append((f'frozen price {pr} baseline m17 thin th0', G(prices=pr)))
    out.append(('frozen U_W at th -0.05 phi0.9 rv0.05 m17 thin', G(th=-0.05, persist=P(0.9, 0.05))))
    out.append(('frozen U_W at th -0.05 baseline m17 thin', G(th=-0.05)))
    return out


def plan_mech():
    """The spec-9 mechanism itself: the error of a 30-date trailing-mean bias correction applied to a date-common
    shock is a 30-date boxcar moving average (autocorrelation 1 - k/30, integrated memory 30 days); plus a non-Gaussian
    two-state regime with the same autocorrelation as AR(0.9). Latent variance within the class bound (<= 0.10)."""
    out = []
    for rv in (0.02, 0.05, 0.10):
        out.append((f'mech boxcar30 rv{rv} m17 thin th0.10', G(th=0.10, persist2=(('boxcar', 30, rv),))))
    out.append(('mech boxcar30 rv0.05 m17 thin th0 (size)', G(persist2=(('boxcar', 30, 0.05),))))
    out.append(('mech boxcar30 rv0.05 m17 full th0.10', G(cap='full', th=0.10, persist2=(('boxcar', 30, 0.05),))))
    out.append(('mech boxcar30 rv0.05 m35 full th0.10', G(m=35, cap='full', th=0.10, persist2=(('boxcar', 30, 0.05),))))
    out.append(('mech boxcar20 rv0.05 m17 thin th0.10', G(th=0.10, persist2=(('boxcar', 20, 0.05),))))
    out.append(('mech boxcar20 rv0.10 m17 thin th0.10', G(th=0.10, persist2=(('boxcar', 20, 0.10),))))
    out.append(('mech markov stay0.95 (corr 0.9^k) rv0.05 m17 thin th0.10', G(th=0.10, persist2=(('markov', 0.95, 0.05),))))
    out.append(('mech markov stay0.95 (corr 0.9^k) rv0.10 m17 thin th0.10', G(th=0.10, persist2=(('markov', 0.95, 0.10),))))
    # frozen surfaces under the boxcar mechanism (kappa_core = 0)
    out.append(('mech boxcar30 rv0.05 m17 full th0 (frozen surfaces)', G(cap='full', persist2=(('boxcar', 30, 0.05),))))
    return out


def plan_fav():
    """CORE favourite-heavy price mixes (all legs CORE, c <= 0.90 as R* permits) inside the declared dependence grid."""
    out = []
    for phi in (0.5, 0.7, 0.8, 0.9):
        for rv in (0.05, 0.10):
            for cap in ('thin', 'full'):
                for th in (0.0, 0.10):
                    out.append((f'fav phi{phi} rv{rv} m17 {cap} th{th}', G(prices='fav', cap=cap, th=th, persist=P(phi, rv))))
    for th in (0.0, 0.10):
        out.append((f'fav baseline m35 full th{th}', G(prices='fav', m=35, cap='full', th=th)))
        out.append((f'fav phi0.9 rv0.05 m35 full th{th}', G(prices='fav', m=35, cap='full', th=th, persist=P(0.9, 0.05))))
        out.append((f'favmix50 phi0.9 rv0.05 m17 thin th{th}', G(prices='favmix', th=th, persist=P(0.9, 0.05))))
        out.append((f'favmix50 phi0.8 rv0.05 m17 thin th{th}', G(prices='favmix', th=th, persist=P(0.8, 0.05))))
    return out


def plan_confirm():
    return [('CONFIRM fav phi0.9 rv0.05 m17 thin th0.10', G(prices='fav', th=0.10, persist=P(0.9, 0.05))),
            ('CONFIRM fav phi0.9 rv0.05 m17 thin th0 (size)', G(prices='fav', persist=P(0.9, 0.05))),
            ('CONFIRM 120 counted + 30 paused phi0.9 rv0.05 m17 thin th0.10', G(th=0.10, pause=30, persist=P(0.9, 0.05)))]


PLANS = dict(fav=(7, plan_fav), confirm=(8, plan_confirm), repro=(1, plan_repro), cls=(2, plan_class), worst=(3, plan_worst), beyond=(4, plan_beyond),
             frozen=(5, plan_frozen), mech=(6, plan_mech))


def job(a):
    code, idx, chunk, name, g, reps = a
    seed = [SEED_BASE, code, idx, chunk]
    return idx, chunk, seed, E.run(g, reps, seed)


if __name__ == '__main__':
    plan = sys.argv[1]
    reps = int(sys.argv[2])
    chunks = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    code, fn = PLANS[plan]
    cells = fn()
    if len(sys.argv) > 4:
        sel = set(int(x) for x in sys.argv[4].split(','))
        cells_idx = [(i, c) for i, c in enumerate(cells) if i in sel]
    else:
        cells_idx = list(enumerate(cells))
    per = reps // chunks
    jobs = [(code, i, k, name, g, per) for i, (name, g) in cells_idx for k in range(chunks)]
    acc = {}
    with Pool(int(os.environ.get('ASTRA_PROCS', '4'))) as pool:
        for idx, chunk, seed, K in pool.imap(job, jobs):
            a = acc.setdefault(idx, dict(K=dict.fromkeys(K, 0), seeds=[], done=0))
            for k, v in K.items():
                a['K'][k] += v
            a['seeds'].append(seed)
            a['done'] += 1
            if a['done'] == chunks:
                name, g = cells[idx]
                out = E.summarise(name, g, per * chunks, a['seeds'], a['K'])
                out['plan'] = plan
                out['cell_index'] = idx
                print(json.dumps(out), flush=True)
