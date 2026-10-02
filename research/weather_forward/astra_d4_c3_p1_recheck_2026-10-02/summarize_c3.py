"""Summaries of the cycle-3 recheck runs (Astra). usage: python3 summarize_c3.py derive|gorate|verify|m3|level|probe|persist ..."""
import json, math, sys, collections
import numpy as np


def load(f):
    return [json.loads(l) for l in open(f) if l.strip()]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    ph = k / n; den = 1 + z * z / n; cen = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0, cen - hw), min(1, cen + hw))


def design_of(r):
    g = r['g']
    return (g['pr'] if isinstance(g['pr'], str) else json.dumps(g['pr']), g['m'], g['cap'])


def cross(xs, ps, level):
    """first linear-interpolated upward crossing of `level` along ascending x; None if never attained"""
    for i in range(1, len(xs)):
        if ps[i - 1] < level <= ps[i]:
            return xs[i - 1] + (level - ps[i - 1]) * (xs[i] - xs[i - 1]) / (ps[i] - ps[i - 1])
    if ps and ps[0] >= level:
        return xs[0]   # already above at first point (lower bound only)
    return None


def derive(f_t2='out_derive_t2_20000.jsonl', f_neg='out_derive_neg_20000.jsonl'):
    t2 = load(f_t2); neg = load(f_neg)
    by = collections.defaultdict(list)
    for r in t2:
        by[design_of(r)].append(r)
    res = {}
    print('T2 (lambda_theta 2.15, given INFO_SUFFICIENT, planning model): design | P(INFO) | theta80 | mean SE0_theta | R = theta80/SE0 | curve')
    maxR, argR = 0, None
    for d, rs in by.items():
        rs.sort(key=lambda r: r['g']['th'])
        xs = [r['sum_thW'] / r['reach'] for r in rs if r['reach'] > 200]
        ps = [r['new']['t2'] / r['reach'] for r in rs if r['reach'] > 200]
        pinfo = np.mean([r['reach'] / r['reps'] for r in rs])
        se0 = np.mean([r['sum_se0_op'] / r['nd'] for r in rs])
        x80 = cross(xs, ps, 0.80)
        R = x80 / se0 if x80 else None
        res[d] = dict(x80=x80, se0=se0, R=R, pinfo=pinfo)
        if R and R > maxR:
            maxR, argR = R, d
        print('  %-10s m%-3d %-5s | %.3f | %s | %.4f | %s | %s' % (d[0], d[1], d[2], pinfo, ('%.4f' % x80) if x80 else 'NOT ATTAINED', se0,
                                                                  ('%.3f' % R) if R else '-', ' '.join('%.2f@%.3f' % (p, x) for x, p in zip(xs, ps))))
    print('MAX R_theta = %.3f at %s -> Z_EFF = max(2.4865, ceil(10*max)/10) = %.1f' % (maxR, argR, max(2.4865, math.ceil(round(10 * maxR, 9)) / 10)))
    by = collections.defaultdict(list)
    for r in neg:
        by[design_of(r)].append(r)
    maxK, argK = 0, None
    print('NEG (lambda_kappa 1.80): design | P(INFO) | kappa90 | mean SE0_kappa | R^k | curve (power@kappa)')
    for d, rs in by.items():
        rs.sort(key=lambda r: -r['g']['th'])      # ascending |kappa| (th negative)
        rr = [r for r in rs if r['reach'] > 200]
        xs = [abs(r['sum_kt'] / r['reach']) for r in rr]
        ps = [r['new']['NEG'] / r['reach'] for r in rr]
        se0k = np.mean([r['sum_se0k_op'] / r['nd'] for r in rs])
        k90 = cross(xs, ps, 0.90)
        R = k90 / se0k if k90 else None
        if R and R > maxK:
            maxK, argK = R, d
        res.setdefault(d, {}).update(k90=k90, se0k=se0k, Rk=R)
        print('  %-10s m%-3d %-5s | %.3f | %s | %.4f | %s | %s' % (d[0], d[1], d[2], np.mean([r['reach'] / r['reps'] for r in rs]),
                                                                  ('%.4f' % k90) if k90 else 'NOT ATTAINED', se0k, ('%.3f' % R) if R else '-',
                                                                  ' '.join('%.2f@%.3f' % (p, x) for x, p in zip(xs, ps))))
    sek = min(0.020, math.floor(round(1000 * 0.07 / maxK, 9)) / 1000) if maxK else None
    print('MAX R_kappa = %.3f at %s -> SE_KAPPA_CEILING = min(0.020, floor(1000*0.07/max)/1000) = %s' % (maxK, argK, sek))
    json.dump({str(k): v for k, v in res.items()}, open('out_derive_summary.json', 'w'), indent=1, default=float)


def gorate(f='out_gorate_20000.jsonl'):
    rs = load(f)
    print('law | m | fill | go2 | th_new | k3(se0k<=0.005) | go3 | min SE0_k | first-fail reasons (new)')
    for r in rs:
        g = r['g']; n = r['n_ok']
        print('%-7s m%-3d %-4s | %.3f | %.3f | %.3f | %.3f | %.4f | %s' % (g['pr'], g['m'], g['cap'], r['go2'] / r['reps'], r['th_new'] / r['reps'], r['k3'] / r['reps'],
                                                                     r['go3'] / r['reps'], r['min_se0k'], r['reasons']))
    print('MAX go3 over all cells:', max(r['go3'] for r in rs), ' MIN over cells of min SE0_kappa:', min(r['min_se0k'] for r in rs))


def verify(fo='out_verify_old_20000.jsonl', fn='out_verify_new_20000.jsonl'):
    for lab, f in (('OLD (Z_80, theta-side)', fo), ('NEW (Z_EFF, theta-side)', fn)):
        rs = load(f)
        print(lab)
        worst = None
        for r in rs:
            d = design_of(r)
            n = r['reach']
            if n >= 2000:
                p = r['new']['t2'] / n
                lo, hi = wilson(r['new']['t2'], n)
                if worst is None or p < worst[0]:
                    worst = (p, d, n, lo, hi)
                print('  %-8s m%-3d %-5s ngate %5d GO&INFO %5d P(T2|.)=%.4f [%.4f,%.4f]' % (d[0], d[1], d[2], r['ngate'], n, p, lo, hi))
            else:
                print('  %-8s m%-3d %-5s ngate %5d GO&INFO %5d (<2000: not evaluated)' % (d[0], d[1], d[2], r['ngate'], n))
        print('  WORST:', worst)


if __name__ == '__main__':
    {'derive': derive, 'gorate': gorate, 'verify': verify}[sys.argv[1]](*sys.argv[2:])
