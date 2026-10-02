"""Equivalence gate, LAYER B: the new generator reproduces the old engine's results (statistical, declared tolerance,
identical state decisions) on a FIXED comparison set declared and committed BEFORE the new engine is run on it.

  python3 wf_equiv_stat.py declare                  -> COMPARISON_SET.json (rule-based, touches no result)
  python3 wf_equiv_stat.py compare [--procs 4]      -> runs the new engine on the set, compares with the committed V2 JSONL
                                                       (git show of the V2 ref), writes EQUIVALENCE_LAYER_B_REPORT.json

Why statistical: the old engine consumes one RNG stream sequentially per replication, with replication-dependent draw counts;
a vectorised generator cannot reproduce that stream, so record-for-record equality is infeasible by construction (the
statistics kernel IS record-for-record exact: layer A).  Old = V2 committed 20,000-rep records (same plans, V2 seeds);
new = this engine, same cells, its own seed streams.  Both are Monte-Carlo estimates of the same quantity.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

import wf_engine as E
import wf_plans as P

HERE = os.path.dirname(os.path.abspath(__file__))
REF = 'origin/claude/charming-allen-948kd8'
V2 = 'research/weather_forward/'
OLD_FILES = {
    'm3': 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_M3_OUTPUT_2026-10-02.jsonl',
    'derive': 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_DERIVE_OUTPUT_2026-10-02.jsonl',
    'verify': 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_P1_VERIFY_OUTPUT_2026-10-02.jsonl',
    'confirm': 'WEATHER_FORWARD_V2_D4_C3_P1_RUN_J_CONFIRM_100K_2026-10-02.jsonl',
    'consts': 'WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json',
}
PLAN_FILE = {'m3_class': 'm3', 'm3_astra': 'm3', 'm3_mix': 'm3', 'm3_geo': 'm3', 'm3_m35': 'm3', 'p1_t2': 'derive',
             'p1_neg': 'derive', 'p1_hi': 'derive', 'p1_verify': 'verify', 'p1_go': 'verify'}
# selection rule: cell indices with idx % mod == 0 (all cells when mod == 1); fixed, outcome-free
RULES = {'m3_class': 25, 'm3_astra': 1, 'm3_mix': 5, 'm3_geo': 6, 'm3_m35': 12, 'p1_t2': 24, 'p1_neg': 18, 'p1_hi': 4,
         'p1_verify': 6, 'p1_go': 1}
CONFIRM_PLAN = 'm3_astra'          # all 10 cells re-run at 100,000 reps (5 streams x 20,000) vs the committed combined records
LAMS = (1.00, 1.50, 2.00, 2.15, 2.50, 3.00, 3.50)
SERIES = ('miss', 'fpos', 'sup', 't2', 'uw_miss', 'uw_loss', 'iv_miss', 'T1a', 'NEG', 'T1a_null', 'NEG_null')
TOL = dict(z_max=4.0, mean_abs=1e-3, design_rel=0.01, go_quantile_rel=0.03, marginal_se=3.0, lam_star_steps=1)
DECISION = dict(theta_side=['miss', 'fpos', 'uw_miss'], theta_side_threshold=0.040, kappa_side=['T1a_null', 'NEG_null'],
                kappa_side_threshold=0.020, confirm_theta_wilson_ub=0.050, confirm_kappa_wilson_ub=0.025)


def declare():
    ref_sha = subprocess.check_output(['git', 'rev-parse', REF], text=True).strip()
    cells = {pl: [i for i in range(len(P.plan_cells('p1:' + pl))) if i % mod == 0] for pl, mod in RULES.items()}
    spec = dict(declared_before_run=True, ref=REF, ref_sha=ref_sha, old_files=OLD_FILES, plan_file=PLAN_FILE,
                selection_rule_idx_mod=RULES, cells=cells, n_cells=sum(len(v) for v in cells.values()), reps=20000,
                confirm=dict(plan=CONFIRM_PLAN, cells=cells[CONFIRM_PLAN], reps=100000, streams=5),
                lambdas=LAMS, series=SERIES, tolerances=TOL, decisions=DECISION,
                tests=['T1 two-proportion |z| <= z_max on reach and every (series, lambda) count/reps',
                       'T2 |mean diff| <= mean_abs on conditional means; design sums within design_rel; p1_go quantiles within go_quantile_rel',
                       'T3 decision booleans (criterion at adopted lambdas) identical, unless BOTH estimates are within marginal_se standard errors of the threshold (then reported as marginal flips, not failures)',
                       'T4 selected-lambda (smallest grid value meeting the criterion over the m3 comparison cells): old vs new within lam_star_steps grid steps; reported',
                       'CONFIRM 100,000-rep decisions (Wilson upper bound rules) identical under the same marginal rule'])
    json.dump(spec, open(os.path.join(HERE, 'COMPARISON_SET.json'), 'w'), indent=1)
    print('declared', spec['n_cells'], 'cells + confirm', len(spec['confirm']['cells']), 'ref', ref_sha[:10])


def old_records(spec):
    repo = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
    out = {}
    for key, fn in spec['old_files'].items():
        if key == 'consts':
            continue
        txt = subprocess.check_output(['git', 'show', f"{spec['ref_sha']}:{V2}{fn}"], cwd=repo, text=True)
        for line in txt.splitlines():
            try:
                x = json.loads(line)
            except ValueError:
                continue
            out[(key, x['plan'], x['idx'], x['reps'], bool(x.get('combined_streams')))] = x
    K = json.loads(subprocess.check_output(['git', 'show', f"{spec['ref_sha']}:{V2}{spec['old_files']['consts']}"], cwd=repo, text=True))
    return out, K


def zscore(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2
    pb = (k1 + k2) / (n1 + n2)
    se = math.sqrt(max(pb * (1 - pb) * (1 / n1 + 1 / n2), 1.0 / (n1 * n2)))
    return (p1 - p2) / se


def marginal(p, n, thr, k):
    se = math.sqrt(max(p * (1 - p), 1.0 / n) / n)
    return abs(p - thr) / se <= k


def decisions(rec, lam_theta, lam_kappa):
    n = rec['reps']
    li = {round(l, 2): i for i, l in enumerate(rec['grid'])}
    out = {}
    for s in DECISION['theta_side']:
        k = rec['by_lam'][s][li[lam_theta]]
        out[(s, lam_theta)] = (k / n <= DECISION['theta_side_threshold'], k / n)
    for s in DECISION['kappa_side']:
        k = rec['by_lam'][s][li[lam_kappa]]
        out[(s, lam_kappa)] = (k / n <= DECISION['kappa_side_threshold'], k / n)
    return out


def wilson_ub(k, n, z=1.96):
    return E.wilson(k, n, z)[1]


def compare_cell(old, new, lam_theta, lam_kappa, rep):
    n = old['reps']
    fails, zs, marg = [], [], []
    if 'by_lam' not in old or 'by_lam' not in new:
        if ('by_lam' in old) != ('by_lam' in new):
            fails.append('one engine empty (no reached replications) and the other not')
        return fails, zs, marg
    z = zscore(old['reach']['k'], n, new['reach']['k'], n)
    zs.append(('reach', z))
    li = {round(l, 2): i for i, l in enumerate(old['grid'])}
    for s in SERIES:
        for lam in LAMS:
            i = li[lam]
            zz = zscore(old['by_lam'][s][i], n, new['by_lam'][s][i], n)
            zs.append((f'{s}@{lam}', zz))
    for k in zs:
        if abs(k[1]) > TOL['z_max']:
            fails.append(f'T1 {k[0]} z={k[1]:.2f}')
    for k in old['mean']:
        if abs(old['mean'][k] - new['mean'][k]) > TOL['mean_abs']:
            fails.append(f"T2 mean {k} old {old['mean'][k]} new {new['mean'][k]}")
    for k in ('se0', 'se0k', 'pce_old'):
        o, w = old['design'][k] / max(1, old['design']['n']), new['design'][k] / max(1, new['design']['n'])
        if abs(o - w) > TOL['design_rel'] * max(abs(o), 1e-12):
            fails.append(f'T2 design {k} old {o:.6g} new {w:.6g}')
    do, dn = decisions(old, lam_theta, lam_kappa), decisions(new, lam_theta, lam_kappa)
    for key in do:
        if do[key][0] != dn[key][0]:
            thr = DECISION['theta_side_threshold'] if key[0] in DECISION['theta_side'] else DECISION['kappa_side_threshold']
            if marginal(do[key][1], n, thr, TOL['marginal_se']) and marginal(dn[key][1], n, thr, TOL['marginal_se']):
                marg.append(f'T3 marginal flip {key} old {do[key][1]:.4f} new {dn[key][1]:.4f}')
            else:
                fails.append(f'T3 decision mismatch {key} old {do[key][1]:.4f} new {dn[key][1]:.4f}')
    return fails, zs, marg


def lam_star(recs):
    """Smallest grid lambda at which every record meets the theta-side criterion (declared criterion, 0.040)."""
    for i, lam in enumerate(E.GRID3):
        ok = all(r['by_lam'][s][i] / r['reps'] <= DECISION['theta_side_threshold'] for r in recs if 'by_lam' in r
                 for s in DECISION['theta_side'])
        if ok:
            return lam
    return None


def compare(procs=4):
    spec = json.load(open(os.path.join(HERE, 'COMPARISON_SET.json')))
    old, K = old_records(spec)
    tmp = tempfile.mkdtemp()
    kfile = os.path.join(tmp, 'K.json')
    json.dump(K, open(kfile, 'w'))
    lam_theta, lam_kappa = round(K['lambda_theta'], 2), round(K['lambda_kappa'], 2)
    report = dict(layer='B', spec_ref_sha=spec['ref_sha'], tolerances=TOL, K_used=K, plans={}, total_tests=0,
                  max_abs_z=0.0, failures=[], marginal=[], verdict=None)
    pairs = {}
    for pl, idxs in spec['cells'].items():
        plan = 'p1:' + pl
        out = os.path.join(tmp, pl + '.jsonl')
        subprocess.run([sys.executable, os.path.join(HERE, 'wf_run.py'), 'run', plan, '--reps', str(spec['reps']), '--out', out,
                        '--cells', ','.join(map(str, idxs)), '--procs', str(procs), '--K', kfile], check=True, cwd=HERE,
                       stdout=subprocess.DEVNULL)
        new = {json.loads(l)['idx']: json.loads(l) for l in open(out)}
        pairs[pl] = (idxs, new)
    for pl, (idxs, new) in pairs.items():
        key = PLAN_FILE[pl]
        pr = dict(cells=len(idxs), fails=0, marginal=0, max_abs_z=0.0)
        recs_old, recs_new = [], []
        for i in idxs:
            o = old[(key, pl, i, spec['reps'], False)]
            nw = new[i]
            if pl == 'p1_go':
                f = []
                for k, v in o['counts'].items():
                    z = zscore(v, o['reps'], nw['counts'][k], nw['reps'])
                    report['total_tests'] += 1
                    pr['max_abs_z'] = max(pr['max_abs_z'], abs(z))
                    if abs(z) > TOL['z_max']:
                        f.append(f'T1 go {k} z={z:.2f} old {v} new {nw["counts"][k]}')
                for q in ('se0_q', 'se0k_q', 'pce_old_q', 'pce_new_q'):
                    if o[q] and nw[q]:
                        for a, b in zip(o[q], nw[q]):
                            if abs(a - b) > TOL['go_quantile_rel'] * max(abs(a), 1e-9):
                                f.append(f'T2 go {q} old {o[q]} new {nw[q]}')
                                break
                fails, zs, marg = f, [], []
            else:
                fails, zs, marg = compare_cell(o, nw, lam_theta, lam_kappa, spec['reps'])
                recs_old.append(o); recs_new.append(nw)
            report['total_tests'] += len(zs)
            for _, z in zs:
                pr['max_abs_z'] = max(pr['max_abs_z'], abs(z))
            pr['fails'] += len(fails); pr['marginal'] += len(marg)
            report['failures'] += [f'{pl}[{i}] {x}' for x in fails]
            report['marginal'] += [f'{pl}[{i}] {x}' for x in marg]
        if pl.startswith('m3_') and recs_old:
            pr['lam_star_old'] = lam_star(recs_old); pr['lam_star_new'] = lam_star(recs_new)
            if pr['lam_star_old'] is None or pr['lam_star_new'] is None or \
                    abs(pr['lam_star_old'] - pr['lam_star_new']) > 0.05 * TOL['lam_star_steps'] + 1e-9:
                if not (pr['lam_star_old'] is None and pr['lam_star_new'] is None):
                    report['failures'].append(f'T4 {pl} lambda* old {pr["lam_star_old"]} new {pr["lam_star_new"]}')
        report['plans'][pl] = pr
        report['max_abs_z'] = max(report['max_abs_z'], pr['max_abs_z'])
        print(pl, pr, flush=True)
    # CONFIRM: 100,000 reps = 5 streams x 20,000
    cf = spec['confirm']
    out = os.path.join(tmp, 'confirm.jsonl')
    subprocess.run([sys.executable, os.path.join(HERE, 'wf_run.py'), 'run', 'p1:' + cf['plan'], '--reps', str(cf['reps']), '--streams', '5',
                    '--out', out, '--cells', ','.join(map(str, cf['cells'])), '--procs', str(procs), '--K', kfile], check=True, cwd=HERE,
                   stdout=subprocess.DEVNULL)
    conf = dict(cells=len(cf['cells']), fails=0, marginal=0, max_abs_z=0.0)
    for line in open(out):
        nw = json.loads(line)
        o = old[('confirm', cf['plan'], nw['idx'], cf['reps'], True)]
        fails, zs, marg = compare_cell(o, nw, lam_theta, lam_kappa, cf['reps'])
        li = {round(l, 2): i for i, l in enumerate(o['grid'])}
        for s, ub_thr, lam in (('miss', DECISION['confirm_theta_wilson_ub'], lam_theta), ('fpos', DECISION['confirm_theta_wilson_ub'], lam_theta),
                               ('uw_miss', DECISION['confirm_theta_wilson_ub'], lam_theta), ('T1a_null', DECISION['confirm_kappa_wilson_ub'], lam_kappa),
                               ('NEG_null', DECISION['confirm_kappa_wilson_ub'], lam_kappa)):
            ko, kn = o['by_lam'][s][li[lam]], nw['by_lam'][s][li[lam]]
            do_, dn_ = wilson_ub(ko, cf['reps']) <= ub_thr, wilson_ub(kn, cf['reps']) <= ub_thr
            if do_ != dn_:
                tag = f"CONFIRM {s}@{lam} Wilson-UB decision old {wilson_ub(ko, cf['reps'])} new {wilson_ub(kn, cf['reps'])}"
                if marginal(ko / cf['reps'], cf['reps'], ub_thr, TOL['marginal_se']) and marginal(kn / cf['reps'], cf['reps'], ub_thr, TOL['marginal_se']):
                    marg.append(tag)
                else:
                    fails.append(tag)
        report['total_tests'] += len(zs)
        for _, z in zs:
            conf['max_abs_z'] = max(conf['max_abs_z'], abs(z))
        conf['fails'] += len(fails); conf['marginal'] += len(marg)
        report['failures'] += [f'confirm[{nw["idx"]}] {x}' for x in fails]
        report['marginal'] += [f'confirm[{nw["idx"]}] {x}' for x in marg]
    report['plans']['CONFIRM_100k_m3_astra'] = conf
    report['max_abs_z'] = max(report['max_abs_z'], conf['max_abs_z'])
    report['verdict'] = 'PASS' if not report['failures'] else 'FAIL'
    json.dump(report, open(os.path.join(HERE, 'EQUIVALENCE_LAYER_B_REPORT.json'), 'w'), indent=1)
    print('LAYER B', report['verdict'], 'tests', report['total_tests'], 'max|z|', round(report['max_abs_z'], 2),
          'failures', len(report['failures']), 'marginal flips', len(report['marginal']))
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    if sys.argv[1] == 'declare':
        declare()
    else:
        procs = int(sys.argv[sys.argv.index('--procs') + 1]) if '--procs' in sys.argv else 4
        sys.exit(compare(procs))
