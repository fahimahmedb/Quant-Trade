"""Mechanical summaries of the cycle-3 raw outputs (run J). Reads committed JSONL only; no simulation, no randomness.

  python3 THIS.py m3 [LAMBDA_THETA LAMBDA_KAPPA]     lambda selection over the new-law cells (declared rule) and level tables
  python3 THIS.py p1derive LAMBDA_THETA LAMBDA_KAPPA derivation of Z_EFF and SE_KAPPA_CEILING (declared rule), constants JSON to stdout
  python3 THIS.py verify                              p1_verify and p1_go tables (needs the constants file)
"""
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
M3 = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl')
P1D = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl')
P1V = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_VERIFY_OUTPUT_2026-10-02.jsonl')
CONF = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_CONFIRM_100K_2026-10-02.jsonl')
RUNH = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_OUTPUT_2026-10-01.jsonl')
CONFH = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_M2_RUN_H_CONFIRM_100K_2026-10-01.jsonl')
CONSTS = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json')
GRID3 = [round(1.0 + 0.05 * i, 2) for i in range(51)]


def load(path):
    out = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def wil(k, n, z=1.96):
    if n == 0:
        return (None, None)
    ph = k / n; den = 1 + z * z / n
    cen = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0.0, cen - hw), min(1.0, cen + hw))


def li(lam, grid):
    return int(round((lam - 1.0) / 0.05))


def depname(g):
    pk = g.get('pk')
    if not pk:
        return 'none'
    return {'ar': 'AR', 'mk': 'two-state', 'box': 'trailing', 'hemi': 'hemi', 'stn': 'stn'}[pk] + '%s/rv%s' % (g['pp'], g['rv'])


def deffam(g):
    pk = g.get('pk')
    if not pk:
        return 'none'
    return {'ar': 'AR(1) phi %s', 'mk': 'two-state phi %s', 'box': 'trailing mean L=%s', 'hemi': 'hemisphere AR phi %s',
            'stn': 'station AR phi %s'}[pk] % g['pp']


def calname(g):
    P = g.get('P', 0)
    return 'P0' if not P else ('P30-' + g.get('lay', 'rand'))


def rates(rec, lt, lk):
    """Per-cell rates at lambda (theta, kappa) from by_lam arrays (GRID <= 3.50 for run J; run H arrays end at 2.50)."""
    n = rec['reps']; b = rec['by_lam']
    it, ik = li(lt, None), li(lk, None)
    if it >= len(b['miss']):
        it = len(b['miss']) - 1
    if ik >= len(b['miss']):
        ik = len(b['miss']) - 1
    r = dict(n=n, reach=rec['reach']['p'] or 0.0, reachk=rec['reach']['k'],
             miss=b['miss'][it], fpos=b['fpos'][it], uw=b['uw_miss'][it], iv=b['iv_miss'][it],
             t1a=b['T1a_null'][ik], neg=b['NEG_null'][ik], t2=b['t2'][it], sup=b['sup'][it])
    return r


def in_class(g):
    """Membership of D_P* (8.1c): phi <= 0.9 (AR / two-state), trailing L in {15, 30}, rv <= 0.10."""
    pk = g.get('pk')
    if pk in ('ar', 'hemi', 'stn') and g['pp'] > 0.9:
        return False
    if pk == 'mk' and g['pp'] > 0.9:
        return False
    if pk == 'box' and g['pp'] not in (15, 30):
        return False
    if pk and g['rv'] > 0.10:
        return False
    return True


def surf(r, key):
    return r[key] / r['n']


SURF = [('miss', 'L_W miss'), ('fpos', 'size (false REALIZED_WINDOW positive)'), ('uw', 'U_W miss'),
        ('t1a', 'T1a false'), ('neg', 'NEG false')]
TARGET = dict(miss=0.040, fpos=0.040, uw=0.040, t1a=0.020, neg=0.020)


def m3(args):
    recs = [r for r in load(M3) if r['plan'].startswith('m3_') and r['plan'] != 'm3_probe' and not r.get('combined_streams')]
    print('new-law cells loaded:', len(recs), {p: sum(1 for r in recs if r['plan'] == p) for p in sorted({r['plan'] for r in recs})})
    ok = [r for r in recs if 'by_lam' in r]
    for lt in [x for x in GRID3 if x >= 1.70]:
        w = max(surf(rates(r, lt, 1.6), 'miss') for r in ok), max(surf(rates(r, lt, 1.6), 'fpos') for r in ok), \
            max(surf(rates(r, lt, 1.6), 'uw') for r in ok)
        if max(w) <= 0.040:
            print('lambda_theta (smallest >= 1.70 meeting 0.040 on miss/size/U_W):', lt, 'worst miss/size/uw', [round(x, 4) for x in w])
            LT = lt
            break
        elif lt in (1.70, 1.75, 1.80, 1.90, 2.0, 2.2, 2.5):
            print('  lambda_theta', lt, 'worst miss/size/uw', [round(x, 4) for x in w])
    else:
        LT = None
        print('NO lambda_theta <= 3.50 meets the criterion')
    for lk in [x for x in GRID3 if x >= 1.60]:
        w = max(surf(rates(r, 1.7, lk), 't1a') for r in ok), max(surf(rates(r, 1.7, lk), 'neg') for r in ok)
        if max(w) <= 0.020:
            print('lambda_kappa (smallest >= 1.60 meeting 0.020):', lk, 'worst T1a/NEG', [round(x, 4) for x in w])
            LK = lk
            break
        elif lk in (1.60, 1.65, 1.70, 1.80, 2.0):
            print('  lambda_kappa', lk, 'worst T1a/NEG', [round(x, 4) for x in w])
    else:
        LK = None
        print('NO lambda_kappa <= 3.50 meets the criterion')
    if len(args) >= 2:
        LT, LK = float(args[0]), float(args[1])
    if LT is None or LK is None:
        return
    print('\n== failed candidate: cycle-2 lambda (1.70 / 1.60) over the enlarged class, worst new-law cells ==')
    for key, nm in SURF:
        lam_t, lam_k = 1.70, 1.60
        worst = sorted(ok, key=lambda r: -surf(rates(r, lam_t, lam_k), key))[:3]
        print(' ', nm, [(round(surf(rates(r, lam_t, lam_k), key), 4), r['g']['pr'], depname(r['g']), calname(r['g']), r['g']['cap'], r['g']['th'], r['g']['m']) for r in worst])
    print('\n== adopted lambda_theta %.2f / lambda_kappa %.2f: worst 3 new-law cells per surface (cells to confirm at 100k) ==' % (LT, LK))
    conf = []
    for key, nm in SURF:
        worst = sorted(ok, key=lambda r: -surf(rates(r, LT, LK), key))[:3]
        for r in worst:
            conf.append((r['plan'], r['idx']))
        print(' ', nm)
        for r in worst:
            print('     %.4f  %s %s %s %s th=%s m=%s reach=%.3f  [%s %d]' % (surf(rates(r, LT, LK), key), r['g']['pr'], depname(r['g']), calname(r['g']),
                  r['g']['cap'], r['g']['th'], r['g']['m'], r['reach']['p'], r['plan'], r['idx']))
    for r in ok:
        if r['plan'] == 'm3_astra':
            conf.append((r['plan'], r['idx']))
    iv = sorted(ok, key=lambda r: -surf(rates(r, LT, LK), 'iv'))[:2]
    conf += [(r['plan'], r['idx']) for r in iv]
    print('CONFIRM_CELLS', sorted(set(conf)))
    # level tables over old (run H) + new cells
    old = [r for r in load(RUNH) if 'by_lam' in r and r['plan'] in ('class_', 'fav35', 'geo', 'astra', 'power') and in_class(r['g'])]
    print('\n== level tables at adopted lambda (old D_P* cells from run H, GRID <= 2.50; new-law cells from run J) ==')
    allc = [(r, 'old') for r in old] + [(r, 'new') for r in ok]

    def worst_by(keyf, label):
        d = defaultdict(lambda: dict(miss=0, fpos=0, uw=0, t1a=0, neg=0, iv=0))
        for r, src in allc:
            if r['reach']['k'] == 0:
                continue
            kf = keyf(r['g'])
            rr = rates(r, LT, LK)
            for k in d[kf]:
                d[kf][k] = max(d[kf][k], surf(rr, k))
        print(label)
        for kf in sorted(d, key=str):
            v = d[kf]
            print('   %-28s miss %.4f size %.4f U_W %.4f T1a %.4f NEG %.4f headline %.4f' % (kf, v['miss'], v['fpos'], v['uw'], v['t1a'], v['neg'], v['iv']))
    worst_by(deffam, ' by dependence family')
    worst_by(lambda g: g['pr'], ' by CORE price law')
    worst_by(calname, ' by calendar')
    worst_by(lambda g: 'D%s' % g['D'], ' by D')
    worst_by(lambda g: 'm%s' % g['m'], ' by m')
    worst_by(lambda g: 'all', ' all of D_P**')
    # conditional on reach (reach >= 0.10)
    cm = defaultdict(float)
    for r, src in allc:
        if r['reach']['p'] >= 0.10:
            rr = rates(r, LT, LK)
            for k in ('miss', 'fpos', 'uw', 't1a', 'neg'):
                cm[k] = max(cm[k], rr[k] / max(1, rr['reachk']))
    print(' conditional on reach (cells with reach >= 0.10): ', {k: round(v, 4) for k, v in cm.items()})
    for r, src in sorted(allc, key=lambda x: -rates(x[0], LT, LK)['miss'] / max(1, x[0]['reach']['k']) * (x[0]['reach']['p'] >= 0.10))[:3]:
        rr = rates(r, LT, LK)
        print('   top conditional L_W miss', round(rr['miss'] / max(1, rr['reachk']), 4), r['g']['pr'], depname(r['g']), calname(r['g']), r['g']['m'], r['g']['cap'], 'reach', r['reach']['p'])


def conf_tab(args):
    LT, LK = float(args[0]), float(args[1])
    cs = load(CONF)
    print('confirm lines:', len(cs))
    for r in cs:
        rr = rates(r, LT, LK)
        n = r['reps']
        out = []
        for key, nm in SURF + [('iv', 'headline')]:
            k = rr[key]
            lo, hi = wil(k, n)
            out.append('%s %.4f [%.4f, %.4f]' % (key, k / n, lo, hi))
        g = r['g']
        print('%s#%d %s %s %s %s th=%s m=%s reach %.3f | %s' % (r['plan'], r['idx'], g['pr'], depname(g), calname(g), g['cap'], g['th'], g['m'], r['reach']['p'], ' | '.join(out)))


def interp(xs, ys, target, rising=True):
    """First crossing of target by (xs, ys) with linear interpolation; xs must be increasing. None if never attained."""
    for i in range(len(xs)):
        if ys[i] >= target:
            if i == 0:
                return xs[0]
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            return x0 + (target - y0) * (x1 - x0) / (y1 - y0) if y1 != y0 else x1
    return None


def p1derive(args):
    LT, LK = float(args[0]), float(args[1])
    it, ik = li(LT, None), li(LK, None)
    recs = [r for r in load(P1D) if not r.get('combined_streams')]
    T2 = defaultdict(list); NG = defaultdict(list)
    for r in recs:
        g = r['g']
        if r['plan'] == 'p1_t2':
            T2[(g['pr'], g['m'], g['cap'])].append(r)
        elif r['plan'] == 'p1_neg':
            NG[(g['pr'], g['m'], g['cap'])].append(r)
    print('cells: t2 laws', len(T2), 'neg laws', len(NG))
    Rs = {}; unatt = []
    print('\n== T2 power given INFO_SUFFICIENT (lambda_theta %.2f) ==' % LT)
    for key in sorted(T2):
        cells = sorted(T2[key], key=lambda r: r['mean']['thW'] if 'mean' in r else -1)
        cells = [r for r in cells if 'by_lam' in r]
        xs = [r['mean']['thW'] for r in cells]
        ys = [r['by_lam']['t2'][it] / max(1, r['reach']['k']) for r in cells]
        joint = [r['by_lam']['t2'][it] / r['reps'] for r in cells]
        reach = cells[-1]['reach']['p'] if cells else 0
        se0 = cells[0]['design']['se0'] / cells[0]['design']['n']
        t80 = interp(xs, ys, 0.80)
        if t80 is None:
            unatt.append(key)
        else:
            Rs[key] = t80 / se0
        # monotone-safety: also report max y
        print('  %-28s SE0 %.4f reach(INFO) %.3f  theta80 %s  R %s  maxpow %.3f  joint-maxpow %.3f' % (str(key), se0, reach, 'None' if t80 is None else '%.4f' % t80,
              'NA' if t80 is None else '%.3f' % (t80 / se0), max(ys) if ys else 0, max(joint) if joint else 0))
    zmax = max(Rs.values()) if Rs else None
    z_eff = max(2.4865, math.ceil(10 * zmax - 1e-9) / 10) if zmax else None
    print('max R_l (attainable laws):', zmax, '-> Z_EFF', z_eff, '| unattainable laws:', unatt)
    Rk = {}; unattk = []
    print('\n== NEG power given INFO_SUFFICIENT (lambda_kappa %.2f) ==' % LK)
    for key in sorted(NG):
        cells = [r for r in NG[key] if 'by_lam' in r]
        cells = sorted(cells, key=lambda r: -r['mean']['kt'])         # |kappa| increasing
        xs = [-r['mean']['kt'] for r in cells]
        ys = [r['by_lam']['NEG'][ik] / max(1, r['reach']['k']) for r in cells]
        se0k = cells[0]['design']['se0k'] / cells[0]['design']['n']
        k90 = interp(xs, ys, 0.90)
        p07 = None
        for x, y in zip(xs, ys):
            if abs(x - 0.07) < 0.003:
                p07 = y
        if k90 is None:
            unattk.append(key)
        else:
            Rk[key] = k90 / se0k
        print('  %-28s SE0k %.4f kappa90 %s  R %s  NEG power at -0.07 %s' % (str(key), se0k, 'None' if k90 is None else '%.4f' % k90,
              'NA' if k90 is None else '%.2f' % (k90 / se0k), 'NA' if p07 is None else '%.3f' % p07))
    rkmax = max(Rk.values()) if Rk else None
    ceil_k = min(0.020, math.floor(1000 * 0.07 / rkmax) / 1000) if rkmax else 0.0
    print('max R^k_l:', rkmax, '-> SE_KAPPA_CEILING', ceil_k, '| unattainable:', unattk)
    print('\nCONSTANTS_JSON', json.dumps(dict(z_eff=z_eff, se_kappa_ceiling=ceil_k, lambda_theta=LT, lambda_kappa=LK,
                                             max_R_theta=zmax, max_R_kappa=rkmax, unattainable_t2=[list(k) for k in unatt],
                                             unattainable_neg=[list(k) for k in unattk])))


def verify(args):
    K = json.load(open(CONSTS))
    print('constants', K)
    rs = [r for r in load(P1V) if r['plan'] == 'p1_verify' and 'by_lam' in r or (r['plan'] == 'p1_verify' and r.get('empty'))]
    LT = K['lambda_theta']; it = li(LT, None)
    print('\n== power AT THE DESIGN OWN theta_PCE, given GO(theta-side) and INFO_SUFFICIENT ==')
    for r in sorted(rs, key=lambda r: (r['g']['th'], r['g']['pr'], r['g']['m'], r['g']['cap'])):
        g = r['g']
        n = r['reps']; kk = r['reach']['k']
        if r.get('empty') or kk == 0:
            print('  %s %-7s m%-3s %-4s GO&INFO reps 0 of %d' % (g['th'], g['pr'], g['m'], g['cap'], n)); continue
        t2 = r['by_lam']['t2'][it]
        lo, hi = wil(t2, kk)
        print('  %s %-7s m%-3s %-4s GO&INFO %6d (%.3f)  P(T2|GO&INFO) %.3f [%.3f, %.3f]  mean theta_PCE %.3f realised thW %.3f' % (
            g['th'], g['pr'], g['m'], g['cap'], kk, kk / n, t2 / kk, lo, hi, r['design']['pce_old' if g['th'] == 'pce_old' else 'pce_new'] / max(1, r['design']['n']), r['mean']['thW']))


def gorates(args):
    rs = [r for r in load(P1V) if r['plan'] == 'p1_go']
    print('== GO rates (old = cycle-2 GO; new = cycle-3 GO) per price law ==')
    d = defaultdict(list)
    for r in rs:
        g = r['g']; c = r['counts']; n = r['reps']
        d[g['pr']].append((g['m'], g['cap'], c['old'] / n, c['th_new'] / n, c['k_new'] / n, c['new'] / n, r['se0_q'], r['se0k_q'], r['pce_new_q'], c))
    for pr in d:
        print(pr)
        for m_, cap, o, t, k, nw, s0, s0k, pn, c in sorted(d[pr], key=lambda x: (x[1], x[0])):
            print('   m%-3s %-4s GO_old %.3f  theta-side_new %.3f  kappa-side_new %.3f  GO_new %.3f | SE0 med %s SE0k med %s thetaPCE_new med %s' % (
                m_, cap, o, t, k, nw, s0[1] if s0 else None, s0k[1] if s0k else None, pn[1] if pn else None))


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    {'m3': m3, 'confirm': conf_tab, 'p1derive': p1derive, 'verify': verify, 'go': gorates}[cmd](args)
