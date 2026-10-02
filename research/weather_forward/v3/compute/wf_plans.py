"""Weather V3 / S0 - plan registry: the V2 D4-C3 cell builders (M2 run H plans and P1 run J plans), ported verbatim.

The builders below are copied unchanged from WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py (plans class_, fav35, geo,
outside, power, astra) and WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM_2026-10-02.py (plans m3_*, p1_*), with `m.G` -> `G`.
NOT ported: M2 `t1b` (PINM, B = 2,000 draws per replication - a per-replication Monte-Carlo inside the replication) and run-G
`LW_CAL` (superseded). Seeds: SeedSequence([base_seed, plan_code, cell_idx, stream]) with the V2 base seeds / plan codes so
V3 cell ids are the V2 cell ids.

New V3 plans register through `register_plan(name, base_seed, plan_code, builder, K=None)`.
"""
import hashlib
import json

from wf_engine import G, ENGINE_VERSION, SCHEMA_VERSION, rep_block

# ---------------------------------------------------------------- M2 (run H) builders
def DEPS(full=True):
    d = [dict()]
    for phi in ((0.5, 0.7, 0.8, 0.9) if full else (0.8, 0.9)):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='ar', pp=phi, rv=rv))
    for phi in (0.8, 0.9):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='mk', pp=phi, rv=rv))
    for L in (15, 30):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='box', pp=L, rv=rv))
    return d


def plan_class():
    """Main D_P* grid at m = 17 (where every run-G / Astra worst cell lies): 25 dependence x 3 CORE price laws x 3 calendars
    x 2 fills x theta {0, 0.10}."""
    cells = []
    for dep in DEPS(True):
        for pr in ('mid', 'fav', 'favmix'):
            for cal in (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run')):
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=17, cap=cap, th=th, pr=pr, **cal, **dep))
    return cells


def plan_fav35():
    """m = 35 slice (IF5 screens most persistent windows) and the theta = 0.05 slice, worst-shape dependence only."""
    cells = []
    deps = [dict()] + [dict(pk='ar', pp=0.9, rv=rv) for rv in (0.02, 0.05, 0.10)] + \
        [dict(pk='mk', pp=0.9, rv=rv) for rv in (0.05, 0.10)] + [dict(pk='box', pp=30, rv=rv) for rv in (0.05, 0.10)]
    for dep in deps:
        for pr in ('mid', 'fav'):
            for cal in (dict(P=0), dict(P=30, lay='rand')):
                for cap in ('thin', 'full'):
                    cells.append(G(m=35, cap=cap, th=0.0, pr=pr, **cal, **dep))
                    cells.append(G(m=35, cap=cap, th=0.10, pr=pr, **cal, **dep))
                cells.append(G(m=17, cap='thin', th=0.05, pr=pr, **cal, **dep))
    return cells


def plan_geo():
    """Other class geometries: truncated windows (D 60 / 90), price laws 'wide' / 'low', hemisphere / station regimes,
    tail mixes (U_W with M_tail > 0)."""
    cells = []
    deps = [dict(), dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='box', pp=30, rv=0.05)]
    for D in (60, 90):
        for dep in deps:
            for pr in ('mid', 'fav'):
                for th in (0.0, 0.10):
                    cells.append(G(D=D, th=th, pr=pr, **dep))
    for pr in ('wide', 'low'):
        for dep in deps:
            cells.append(G(th=0.0, pr=pr, **dep))
    for pk in ('hemi', 'stn'):
        for rv in (0.05, 0.10):
            for pr in ('mid', 'fav'):
                for th in (0.0, 0.10):
                    cells.append(G(th=th, pr=pr, pk=pk, pp=0.9, rv=rv))
    for pr, m, cap in (('tail1', 17, 'thin'), ('tail3', 35, 'full')):
        for dep in deps:
            for th in (0.0, 0.10):
                cells.append(G(m=m, cap=cap, th=th, pr=pr, **dep))
    return cells


def plan_outside():
    """Outside D_P* (disclosure only): phi 0.95 / 0.97, rv 0.20, two-component memory."""
    cells = []
    for pr in ('mid', 'fav'):
        for phi, rv in ((0.95, 0.05), (0.95, 0.10), (0.97, 0.05)):
            for th in (0.0, 0.10):
                cells.append(G(th=th, pr=pr, pk='ar', pp=phi, rv=rv))
        for th in (0.0, 0.10):
            cells.append(G(th=th, pr=pr, pk='ar', pp=0.9, rv=0.20))
            cells.append(G(th=th, pr=pr, pk='box', pp=60, rv=0.05))
    return cells


def plan_power():
    """Power / feasibility cost (no persistence unless stated): T2 / SUPPORTED at theta_PCE, 0.10, 0.12, 0.15;
    T1a at kappa ~ +0.035 (theta 0.06 on 'mid'); NEG at kappa ~ -0.07 (theta -0.12 on 'mid')."""
    cells = []
    for m, cap, pce in ((17, 'thin', 0.09), (17, 'full', 0.08), (35, 'thin', 0.07), (35, 'full', 0.07)):
        for th in sorted({pce, 0.10, 0.12, 0.15, 0.20}):
            cells.append(G(m=m, cap=cap, th=th))
        cells.append(G(m=m, cap=cap, th=0.06))
        cells.append(G(m=m, cap=cap, th=-0.12))
        cells.append(G(m=m, cap=cap, th=-0.06))
        cells.append(G(m=m, cap=cap, th=pce, pk='ar', pp=0.8, rv=0.05))
    return cells


def plan_astra():
    """Astra @ac777a87 counterexample cells, verbatim geometry (m 17), run here at 20,000 (and by `cell` at 100,000)."""
    return [
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.9, rv=0.05),          # miss 0.0635 @100k
        G(cap='thin', th=0.0, pr='fav', pk='ar', pp=0.9, rv=0.05),           # false positive 0.0605 @100k
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.9, rv=0.10),          # miss 0.0852
        G(cap='thin', th=0.0, pr='fav', pk='ar', pp=0.9, rv=0.10),           # size 0.0721
        G(cap='thin', th=0.10, pr='mid', pk='ar', pp=0.9, rv=0.05, P=30, lay='rand'),   # 30 paused 0.0531 @100k
        G(cap='thin', th=0.10, pr='mid', pk='mk', pp=0.9, rv=0.05),          # two-state 0.0526
        G(cap='thin', th=0.10, pr='mid', pk='box', pp=30, rv=0.05),          # literal spec-9 boxcar 0.0597
        G(cap='thin', th=0.0, pr='mid', pk='box', pp=30, rv=0.05),           # boxcar size 0.0522
        G(cap='thin', th=0.0, pr='mid', pk='ar', pp=0.9, rv=0.05),           # M2: T1a / NEG / U_W at kappa = 0
        G(cap='thin', th=0.0, pr='mid', pk='ar', pp=0.9, rv=0.10),
        G(cap='thin', th=0.10, pr='mid', pk='ar', pp=0.9, rv=0.05),          # run-G worst grid cell 0.0471 @100k (Astra)
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.95, rv=0.05),         # outside: phi 0.95 0.0769
    ]



# ---------------------------------------------------------------- P1 (run J) builders
# mean CORE ask of each GO-feasible law (turns a target kappa into a theta for the NEG cells)
LAW_MEAN = dict(mid=0.575, favmix=0.6875, fav=0.80, fav80=0.85, fav85=0.875, pm89=0.89)

NEWLAWS = ('fav80', 'fav85', 'pm89')
CALS = (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run'))


def plan_m3_class():
    """The cycle-2 class grid (25 dependence x 3 calendars x 2 fills x theta {0, 0.10}, m = 17) on the three NEW CORE price laws."""
    cells = []
    for dep in DEPS(True):
        for pr in NEWLAWS:
            for cal in CALS:
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=17, cap=cap, th=th, pr=pr, **cal, **dep))
    return cells


def plan_m3_mix():
    """Two-point price mixtures: share 10 / 50 / 90 % of a point mass at 0.89, the rest U(0.35, 0.80)."""
    cells = []
    deps = [dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='mk', pp=0.9, rv=0.10),
            dict(pk='box', pp=30, rv=0.05), dict(pk='box', pp=30, rv=0.10)]
    for pr in ('pmmix10', 'pmmix50', 'pmmix90'):
        for dep in deps:
            for cal in (dict(P=0), dict(P=30, lay='run')):
                for th in (0.0, 0.10):
                    cells.append(G(m=17, cap='thin', th=th, pr=pr, **cal, **dep))
    return cells


def plan_m3_m35():
    cells = []
    deps = [dict()] + [dict(pk='ar', pp=0.9, rv=rv) for rv in (0.02, 0.05, 0.10)] + \
        [dict(pk='mk', pp=0.9, rv=rv) for rv in (0.05, 0.10)] + [dict(pk='box', pp=30, rv=rv) for rv in (0.05, 0.10)]
    for dep in deps:
        for pr in NEWLAWS:
            for cal in (dict(P=0), dict(P=30, lay='rand')):
                for cap in ('thin', 'full'):
                    cells.append(G(m=35, cap=cap, th=0.0, pr=pr, **cal, **dep))
                    cells.append(G(m=35, cap=cap, th=0.10, pr=pr, **cal, **dep))
                cells.append(G(m=17, cap='thin', th=0.05, pr=pr, **cal, **dep))
    return cells


def plan_m3_geo():
    cells = []
    deps = [dict(), dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='box', pp=30, rv=0.05)]
    for D in (60, 90):
        for dep in deps:
            for pr in NEWLAWS:
                for th in (0.0, 0.10):
                    cells.append(G(D=D, th=th, pr=pr, **dep))
    for pk in ('hemi', 'stn'):
        for rv in (0.05, 0.10):
            for pr in NEWLAWS:
                for th in (0.0, 0.10):
                    cells.append(G(th=th, pr=pr, pk=pk, pp=0.9, rv=rv))
    return cells


def plan_m3_astra():
    """Astra @8874dc54 M3 counterexamples verbatim (trailing mean 30, rv 0.10, m 17) and their price-law neighbours."""
    b = dict(pk='box', pp=30, rv=0.10)
    return [
        G(cap='full', th=0.10, pr='fav85', P=30, lay='run', **b),            # 0.0587 @100k, cycle-2 lambda
        G(cap='thin', th=0.10, pr='fav85', P=30, lay='run', **b),            # 0.0557
        G(cap='full', th=0.10, pr='fav85', P=0, **b),                        # 0.0523 (no pauses)
        G(cap='thin', th=0.0, pr='fav85', P=30, lay='run', **b),             # T1a 0.0262
        G(cap='thin', th=0.10, pr='fav80', P=30, lay='run', **b),            # 0.0506
        G(cap='full', th=0.10, pr='fav85', P=30, lay='rand', **b),           # 0.0522
        G(cap='thin', th=0.10, pr='pm89', P=30, lay='run', **b),
        G(cap='thin', th=0.0, pr='pm89', P=30, lay='run', **b),
        G(cap='thin', th=0.0, pr='fav80', P=30, lay='run', **b),
        G(cap='full', th=0.0, pr='fav85', P=30, lay='run', **b),
    ]


def plan_m3_probe():
    """Post-calibration price-law sensitivity at the adopted lambda: in-between laws (inside the stated class by monotone
    interpolation, tested) and laws OUTSIDE the stated class (disclosure only): pm899, pm85, pm80, fav88, fav60."""
    cells = []
    deps = [dict(pk='box', pp=30, rv=0.10), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='mk', pp=0.9, rv=0.10)]
    for pr in ('pm899', 'pm85', 'pm80', 'fav88', 'fav60'):
        for dep in deps:
            for th in (0.0, 0.10):
                cells.append(G(cap='thin', th=th, pr=pr, P=30, lay='run', **dep))
    return cells


def plan_m3_probe2():
    """Addendum probe (declared after the 20,000-replication m3_probe, before it was run): the m 35 geometry that binds
    the adopted lambda for pm89, now for the outside / neighbouring laws pm899 and fav88."""
    cells = []
    b = dict(pk='box', pp=30, rv=0.10)
    for pr in ('pm899', 'fav88'):
        for cap in ('thin', 'full'):
            cells.append(G(m=35, cap=cap, th=0.10, pr=pr, P=0, **b))
    return cells


def plan_m3_probe3():
    """Addendum (m13): Astra's off-grid conditional-on-reach cell, D 60 counted dates + 30 contiguous paused, two-state phi 0.9
    rv 0.10, at the adopted lambda; three price laws, theta {0, 0.10}, thin, m 17."""
    cells = []
    for pr in ('mid', 'fav', 'pm89'):
        for th in (0.0, 0.10):
            cells.append(G(D=60, m=17, cap='thin', th=th, pr=pr, P=30, lay='run', pk='mk', pp=0.9, rv=0.10))
    return cells


P1_LAWS = ('mid', 'favmix', 'fav', 'fav80', 'fav85', 'pm89')
P1_DESIGNS = ((17, 'thin'), (17, 'full'), (35, 'thin'), (35, 'full'), (55, 'thin'), (55, 'full'))
P1_THETA = (0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30)
P1_KAPPA = (-0.03, -0.05, -0.07, -0.09, -0.12, -0.16, -0.20, -0.25)


def plan_p1_t2():
    """P1 derive (T2): power curve of the calibrated T2 over the GO-feasible laws; no persistence, no pauses, no GO filter."""
    cells = []
    for pr in P1_LAWS:
        for mm, cap in P1_DESIGNS:
            for th in P1_THETA:
                cells.append(G(m=mm, cap=cap, th=th, pr=pr, go='none'))
    return cells


def plan_p1_neg():
    """P1 derive (NEG): power curve of NEG over kappa_core in P1_KAPPA (theta = kappa / mean CORE ask of the law)."""
    cells = []
    for pr in P1_LAWS:
        for mm, cap in P1_DESIGNS:
            for kp in P1_KAPPA:
                cells.append(G(m=mm, cap=cap, th=round(kp / LAW_MEAN[pr], 6), pr=pr, go='none'))
    return cells


def plan_p1_hi():
    """Best-case throughput (m 80 / 96 trades per date; the engine caps a date at 2 x 48 = 96): NEG power at kappa -0.07 / -0.12."""
    cells = []
    for pr in ('mid', 'fav', 'fav85'):
        for mm in (80, 96):
            for cap in ('thin', 'full'):
                for kp in (-0.07, -0.12, -0.20):
                    cells.append(G(m=mm, cap=cap, th=round(kp / LAW_MEAN[pr], 6), pr=pr, go='none'))
    return cells


def plan_p1_verify():
    """Power AT THE DESIGN'S OWN theta_PCE under the old (Z80) and the new multiplier, theta-side GO only; theta := the
    replication's own theta_PCE.  Laws x m in {17, 35, 55, 96} x fills."""
    cells = []
    for rule in ('old', 'new'):
        for pr in P1_LAWS:
            for mm in (17, 35, 55, 96):
                for cap in ('thin', 'full'):
                    cells.append(G(m=mm, cap=cap, th='pce_' + rule, pr=pr, go='th_' + rule))
    return cells




PLAN_DEFS = {}


def register_plan(name, base_seed, plan_code, builder, kind='cells'):
    PLAN_DEFS[name] = dict(name=name, base_seed=base_seed, plan_code=plan_code, builder=builder, kind=kind)


for _n, _c, _f in (('class', 1, plan_class), ('fav35', 2, plan_fav35), ('geo', 3, plan_geo), ('outside', 4, plan_outside),
                   ('power', 6, plan_power), ('astra', 7, plan_astra)):
    register_plan('m2:' + _n, 20261101, _c, _f)
for _n, _c, _f in (('m3_class', 11, plan_m3_class), ('m3_mix', 12, plan_m3_mix), ('m3_m35', 13, plan_m3_m35),
                   ('m3_geo', 14, plan_m3_geo), ('m3_astra', 15, plan_m3_astra), ('m3_probe', 16, plan_m3_probe),
                   ('m3_probe2', 17, plan_m3_probe2), ('m3_probe3', 18, plan_m3_probe3), ('p1_t2', 21, plan_p1_t2),
                   ('p1_neg', 22, plan_p1_neg), ('p1_hi', 23, plan_p1_hi), ('p1_verify', 24, plan_p1_verify)):
    register_plan('p1:' + _n, 20261102, _c, _f)


def plan_cells(name):
    return PLAN_DEFS[name]['builder']()


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def plan_hash(name, K=None):
    """sha256 over everything that defines the experiment except reps/streams: plan identity, seed namespace, every cell spec
    (in order), the constants K, the engine + schema versions and the per-cell rep-block sizes."""
    d = PLAN_DEFS[name]
    cells = plan_cells(name)
    payload = dict(name=name, base_seed=d['base_seed'], plan_code=d['plan_code'], cells=cells, K=K or {},
                   engine=ENGINE_VERSION, schema=SCHEMA_VERSION, rep_blocks=[rep_block(g) for g in cells])
    return hashlib.sha256(canonical(payload).encode()).hexdigest()
