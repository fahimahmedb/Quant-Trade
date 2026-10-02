"""Equivalence gate, LAYER A: the new statistics kernel is exact on identical inputs.

The V2 reference engine (P1 `one_rep_p1`, M2 helpers, from the git ref below) is run UNMODIFIED except for two inserted
capture statements (anchors asserted) that record the OP trades and the window trades each replication generated. The very
same inputs are then fed to wf_engine.design_arrays / go_pass / window_stats, and every output is compared with the old
engine's output: booleans / ints exactly, floats to rtol 1e-9 (summation-order noise only).

Usage: python3 wf_equiv_kernel.py [--ref REF] [--reps N] [--out FILE.json]
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

import wf_engine as E

REF = 'origin/claude/charming-allen-948kd8'
V2 = 'research/weather_forward/'
FILES = ['WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py', 'WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py',
         'WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json']
A1 = "C_op = m.fills(rng, g['cap'], n_op)\n"
A2 = "    nsh = C / c\n"


def load_reference(ref, scratch):
    repo = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
    shas = {}
    for f in FILES:
        src = subprocess.check_output(['git', 'show', f'{ref}:{V2}{f}'], cwd=repo, text=True)
        if f.endswith('P1_GATE_SIM_2026-10-02.py'):
            i0 = src.index('def one_rep_p1(')
            i1 = src.index('# ----', i0)
            body = src[i0:i1]
            assert body.count(A1) == 1 and body.count(A2) == 1, 'capture anchors not unique inside one_rep_p1'
            body = body.replace(A1, A1 + "    _CAP['op'] = (c_op, C_op, st_op)\n")
            body = body.replace(A2, "    _CAP['win'] = (Tc, day, st, c, C, y, p, thv)\n" + A2)
            src = src[:i0] + body + src[i1:]
            src = src.replace("import numpy as np\n", "import numpy as np\n_CAP = {}\n", 1)
        open(os.path.join(scratch, f), 'w').write(src)
        shas[f] = subprocess.check_output(['git', 'rev-parse', f'{ref}:{V2}{f}'], cwd=repo, text=True).strip()
    spec = importlib.util.spec_from_file_location('p1ref', os.path.join(scratch, FILES[1]))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, json.load(open(os.path.join(scratch, FILES[2]))), shas


CELLS = [
    E.G(cap='thin', th=0.10, pr='mid'),
    E.G(cap='thin', th=0.10, pr='fav', pk='box', pp=30, rv=0.10, P=30, lay='run'),
    E.G(cap='full', th=0.0, pr='mid', pk='mk', pp=0.9, rv=0.05),
    E.G(cap='thin', th=0.10, pr='favmix', pk='ar', pp=0.9, rv=0.10, P=30, lay='rand'),
    E.G(m=35, cap='full', th=0.10, pr='tail3'),
    E.G(m=17, cap='thin', th=0.05, pr='tail1', pk='hemi', pp=0.9, rv=0.10),
    E.G(m=35, cap='thin', th=0.10, pr='fav85', pk='stn', pp=0.9, rv=0.05),
    E.G(m=55, cap='thin', th=0.10, pr='pm89', go='none', pk='ar', pp=0.5, rv=0.02),
    E.G(m=35, cap='full', th='pce_old', pr='fav80', go='th_old'),
    E.G(m=96, cap='thin', th='pce_new', pr='mid', go='th_new'),
    E.G(m=96, cap='full', th='pce_new', pr='pmmix50', go='new', pk='ar', pp=0.5, rv=0.05, P=30, lay='run'),
    E.G(D=60, m=17, cap='thin', th=0.10, pr='mid', pk='mk', pp=0.9, rv=0.10, P=30, lay='run'),
    E.G(D=90, m=96, cap='full', th=0.12, pr='fav', go='none'),
    E.G(m=17, cap='thin', th=-0.12, pr='mid', go='none'),
    E.G(m=17, cap='thin', th=0.0, pr='wide', go='none'),
]
REC_FIELDS = ['th', 'thW', 'kap', 'kt', 'thc', 'w', 'Mt', 'gates', 'H_A', 'HkA', 'HcA', 'H_R0', 'Hk5', 'ntail']
DES_FIELDS = ['se0', 'se0k', 'pce_old', 'pce_new']


def close(a, b):
    return np.allclose(a, b, rtol=1e-9, atol=1e-12, equal_nan=False)


def run(ref=REF, reps=300, out=None):
    scratch = tempfile.mkdtemp()
    p1, K, shas = load_reference(ref, scratch)
    K = dict(K, z_eff=3.0, se_kappa_ceiling=0.012)   # test-only constants so the 'new' gate modes actually pass some reps
    report = dict(layer='A', ref=ref, ref_blob_sha=shas, reps_per_cell=reps, cells=[], mismatches=0)
    for ci, g in enumerate(CELLS):
        rng = np.random.default_rng(np.random.SeedSequence([20261201, ci]))
        ops, wins, olds, designs = [], [], [], []
        for _ in range(reps):
            p1._CAP.clear()
            d, rec = p1.one_rep_p1(rng, g, K)
            ops.append(p1._CAP.get('op'))
            wins.append(p1._CAP.get('win'))
            designs.append(d)
            olds.append(rec)
        S = g['S']
        # ---- design / GO
        rep_op = np.concatenate([np.full(o[0].size, i) for i, o in enumerate(ops)])
        c_op = np.concatenate([o[0] for o in ops]); C_op = np.concatenate([o[1] for o in ops]); st_op = np.concatenate([o[2] for o in ops])
        d = E.design_arrays(rep_op, c_op, C_op, st_op, reps, S, K['z_eff'])
        go = E.go_pass(g.get('go', 'old'), d, K)
        bad = []
        for i, dd in enumerate(designs):
            if (dd is None) != (not d['valid'][i]):
                bad.append(('design_valid', i)); continue
            if dd is None:
                continue
            for f in DES_FIELDS:
                if not np.isclose(dd[f], d[f][i], rtol=1e-9, atol=1e-12):
                    bad.append((f, i))
            if bool(dd['stn']) != bool(d['stn'][i]):
                bad.append(('stn', i))
            if bool(p1.go_pass(g.get('go', 'old'), dd, K)) != bool(go[i]):
                bad.append(('go', i))
        # ---- window kernel on the replications the old engine generated a window for
        idx = [i for i, w in enumerate(wins) if w is not None]
        n_info_old = sum(1 for i in idx if olds[i] is not None)
        if idx:
            Tc = wins[idx[0]][0]
            rep = np.concatenate([np.full(wins[i][1].size, j) for j, i in enumerate(idx)])
            cat = lambda k: np.concatenate([wins[i][k] for i in idx])
            r = E.window_stats(rep, cat(1), cat(2), cat(3), cat(4), cat(5), cat(6), len(idx), Tc, S, g['D'])
            for j, i in enumerate(idx):
                old = olds[i]
                if bool(r['info'][j]) != (old is not None):
                    bad.append(('info', i)); continue
                if old is None:
                    continue
                for f in REC_FIELDS:
                    if not close(float(old[f]), r[f][j]):
                        bad.append((f, i, float(old[f]), float(r[f][j])))
        report['cells'].append(dict(cell=g, reps=reps, window_reps=len(idx), info_reps=n_info_old, mismatches=len(bad),
                                    first=[str(x) for x in bad[:5]]))
        report['mismatches'] += len(bad)
        print(ci, 'win', len(idx), 'info', n_info_old, 'MISMATCH' if bad else 'ok', bad[:3], flush=True)
    report['verdict'] = 'PASS' if report['mismatches'] == 0 else 'FAIL'
    print('LAYER A', report['verdict'])
    if out:
        json.dump(report, open(out, 'w'), indent=1)
    return report


if __name__ == '__main__':
    a = sys.argv[1:]
    ref = a[a.index('--ref') + 1] if '--ref' in a else REF
    reps = int(a[a.index('--reps') + 1]) if '--reps' in a else 300
    out = a[a.index('--out') + 1] if '--out' in a else None
    sys.exit(0 if run(ref, reps, out)['verdict'] == 'PASS' else 1)
