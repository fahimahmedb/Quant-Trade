"""Summaries of Astra cycle-2 outputs (joint-with-reach rates, Wilson 95%).  Usage: python3 summarize_m2.py FILE [FILE...]"""
import json
import math
import sys

import astra_m2_engine as E

GRID = [round(1.0 + 0.05 * i, 2) for i in range(31)]
IT, IK = GRID.index(1.70), GRID.index(1.60)


def rows(files):
    for f in files:
        for l in open(f):
            if l.strip():
                yield json.loads(l)


def fmt(k, n):
    w = E.wilson(k, n)
    return '%.4f [%.4f, %.4f]' % (k / n, w[0], w[1])


def in_class(g):
    for c in g['comps']:
        if c[0] in ('ar', 'mk', 'hemi', 'stn') and c[1] > 0.9:
            return False
        if c[0] == 'box' and c[1] not in (15, 30):
            return False
        if c[2] > 0.10:
            return False
    if len(g['comps']) > 1:
        return False
    if g['pr'] not in ('mid', 'fav', 'favmix', 'wide', 'low', 'tail1', 'tail3'):
        return False
    if g['m'] not in (17, 35) or g['D'] not in (60, 90, 120) or g['P'] not in (0, 30) or g['lay'] not in ('rand', 'run'):
        return False
    if g.get('pr_op'):
        return False
    if g['th'] not in (0.0, 0.05, 0.10):
        return False
    return True


def table(files, show_all=True):
    R = list(rows(files))
    print('%-62s %6s | %-24s %-24s %-24s %-24s %-24s | old miss / T1a / NEG / UW' % (
        'cell', 'reach', 'L_W miss', 'size', 'U_W miss', 'T1a null', 'NEG null'))
    for r in R:
        n = r['reps']
        if r['reach'] == 0:
            print('%-62s %6.3f | NO_GO / no reach' % (r['key'], 0))
            continue
        nw, o = r['new'], r['old']
        tag = '' if in_class(r['g']) else ' (off-grid/outside)'
        print('%-62s %6.3f | %-24s %-24s %-24s %-24s %-24s | %.4f / %.4f / %.4f / %.4f%s' % (
            r['key'], r['reach'] / n, fmt(nw['miss'], n), fmt(nw['fpos'], n), fmt(nw['uwmiss'], n), fmt(nw['T1a_null'], n),
            fmt(nw['NEG_null'], n), o['miss'] / n, o['T1a_null'] / n, o['NEG_null'] / n, o['uwmiss'] / n, tag))


def worst(files, only_class=True, top=5):
    R = [r for r in rows(files) if r['reach'] > 0 and (in_class(r['g']) or not only_class)]
    out = {}
    for k in ('miss', 'fpos', 'uwmiss', 'T1a_null', 'NEG_null', 'head_noncov'):
        s = sorted(R, key=lambda r: -r['new'][k] / r['reps'])[:top]
        out[k] = [(round(r['new'][k] / r['reps'], 5), E.wilson(r['new'][k], r['reps']), r['key'], round(r['reach'] / r['reps'], 3)) for r in s]
    # given reach (reach >= 0.10)
    s = sorted([r for r in R if r['reach'] / r['reps'] >= 0.10], key=lambda r: -r['new']['miss'] / r['reach'])[:3]
    out['miss_given_reach'] = [(round(r['new']['miss'] / r['reach'], 4), r['key'], round(r['reach'] / r['reps'], 3)) for r in s]
    # lambda selection with Astra's own replications
    lt = next((GRID[i] for i in range(31) if all(max(r['g_' + k][i] / r['reps'] for r in R) <= 0.040
                                                for k in ('miss', 'fpos', 'uwmiss'))), None)
    R0 = [r for r in R if r['g']['th'] == 0.0]
    lk = next((GRID[i] for i in range(31) if all(max(r['g_' + k][i] / r['reps'] for r in R0) <= 0.020
                                                for k in ('T1a_null', 'NEG_null'))), None)
    out['lambda_selection_on_these_cells'] = dict(cells=len(R), lambda_theta=lt, lambda_kappa=lk)
    out['old_worst'] = {k: max((r['old'][k] / r['reps'], r['key']) for r in R) for k in ('miss', 'fpos', 'T1a_null', 'NEG_null', 'uwmiss')}
    out['loss_vs_headline_new'] = sum(r['new']['loss_vs_headline'] for r in R)
    out['LW_above_old'] = sum(r['new']['LW_above_old'] for r in R)
    out['UW_below_old'] = sum(r['new']['UW_below_old'] for r in R)
    return out


if __name__ == '__main__':
    mode = sys.argv[1]
    files = sys.argv[2:]
    if mode == 'table':
        table(files)
    else:
        print(json.dumps(worst(files, only_class=(mode == 'worst')), indent=1))
