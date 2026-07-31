"""ML-1 -- batterie de validation renforcee (5 controles a-e du §2.4 de
ML_STRATEGY_BACKLOG.md / Regle 9 de PROTOCOLE_ANTI_SNOOPING.md), adaptee ML.

Ne doit tourner que sur un PASS niveau 1. Lit le .npz sauvegarde par
ml_meta_labeling_logitl2_ndx_backtest.py (positions OOS, rendements log
t->t+1, dates, cout, var_trials, n_trials cumule).

Convention identique a l'Etape B : rendements LOG, couts sur |delta position|
via backtest() de finance/src/prediction.py (position initiale 0, pas 1 :
le candidat n'est pas un overlay long-only, il peut etre short).

Usage : python3 ml_meta_labeling_logitl2_ndx_battery.py [tag]
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
warnings.filterwarnings("ignore")

from prediction import backtest, dsr, trading_metrics  # noqa: E402
from volatility import spa_test  # noqa: E402

EMBARGO = 5
N_FOLDS = 4
CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]

TAG = sys.argv[1] if len(sys.argv) > 1 else "ml_meta_labeling_logitl2_ndx"
d = np.load(ROOT / "results" / f"{TAG}_pnl.npz", allow_pickle=True)
pos, r = d["pos"], d["r_asset"]
dates = pd.to_datetime(d["dates"].astype(str))
COST = float(d["cost_bps"])
VAR_TRIALS, N_TRIALS = float(d["var_trials"]), int(d["n_trials"])
bh = np.ones(len(r))


def pair(pos_a, pos_b, r_w, cost):
    return trading_metrics(backtest(pos_a, r_w, cost)), trading_metrics(backtest(pos_b, r_w, cost))


def criterion(mc, mb):
    """Critere niveau 1 du PREREG §5 : (Sharpe ET rendement) OU Calmar."""
    a = (mc["sharpe_ann"] > mb["sharpe_ann"]) and (mc["ann_return_pct"] > mb["ann_return_pct"])
    b = np.isfinite(mc["calmar"]) and np.isfinite(mb["calmar"]) and mc["calmar"] > mb["calmar"]
    return bool(a or b)


L = []
w = L.append
w(f"# ML-1 — Batterie de validation renforcée ({TAG})\n")
w(f"Coût pré-enregistré {COST:.0f} bps, {len(r)} séances OOS "
  f"({dates[0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y}). Les 5 contrôles doivent TOUS "
  "passer pour un PASS RENFORCÉ.\n")

# --------------------------------------------------------- a. stress de couts
w("## a. Stress de coûts (×1, ×3, ×5)\n")
w("| Coût (bps) | Sharpe Meta | Sharpe BH | Rdt ann. Meta | Rdt ann. BH | Calmar Meta | Calmar BH | Critère |")
w("|---|---|---|---|---|---|---|---|")
ok_a = True
for mult in (1, 3, 5):
    mc, mb = pair(pos, bh, r, COST * mult)
    ok = criterion(mc, mb)
    ok_a &= ok
    w(f"| {COST*mult:.0f} | {mc['sharpe_ann']:+.2f} | {mb['sharpe_ann']:+.2f} | "
      f"{mc['ann_return_pct']:+.1f} % | {mb['ann_return_pct']:+.1f} % | "
      f"{mc['calmar']:+.2f} | {mb['calmar']:+.2f} | {'OUI' if ok else 'non'} |")
w(f"\n**{'OK' if ok_a else 'ÉCHEC'} — tient jusqu'à ×5 le coût nominal.**\n")

# --------------------------------------------------------- b. stress de crise
w("## b. Stress de crise (MDD Meta vs Buy & Hold)\n")
w("| Fenêtre | Séances | MDD Meta | MDD BH | Pas pire que BH |")
w("|---|---|---|---|---|")
ok_b, any_window = True, False
for label, d0, d1 in CRISIS_WINDOWS:
    m = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
    nw = int(m.sum())
    if nw < 20:
        w(f"| {label} | {nw} | — | — | hors couverture (<20 séances) |")
        continue
    any_window = True
    mc, mb = pair(pos[m.values], bh[m.values], r[m.values], COST)
    ok = mc["max_drawdown_pct"] >= mb["max_drawdown_pct"] - 1.0  # tolérance 1 pt
    ok_b &= ok
    w(f"| {label} | {nw} | {mc['max_drawdown_pct']:.1f} % | {mb['max_drawdown_pct']:.1f} % | "
      f"{'OUI' if ok else 'non'} |")
ok_b = ok_b and any_window
w(f"\n**{'OK' if ok_b else ('PENDING — aucune fenêtre couverte' if not any_window else 'ÉCHEC')}.**\n")

# ------------------------------------------------ c. stabilite temporelle
w(f"## c. Stabilité temporelle ({N_FOLDS} folds non chevauchants + embargo {EMBARGO} j)\n")
w("| Fold | Séances | Période | Sharpe Meta | Sharpe BH | Meta > BH |")
w("|---|---|---|---|---|---|")
T = len(r)
flen = T // N_FOLDS
n_beat = n_scored = 0
for k in range(N_FOLDS):
    f0 = k * flen + (EMBARGO if k > 0 else 0)
    f1 = (k + 1) * flen if k < N_FOLDS - 1 else T
    if f1 - f0 < 30:
        continue
    mc, mb = pair(pos[f0:f1], bh[f0:f1], r[f0:f1], COST)
    beat = mc["sharpe_ann"] > mb["sharpe_ann"]
    n_beat += int(beat)
    n_scored += 1
    w(f"| {k+1} | {f1-f0} | {dates[f0]:%m/%Y}→{dates[f1-1]:%m/%Y} | "
      f"{mc['sharpe_ann']:+.2f} | {mb['sharpe_ann']:+.2f} | {'OUI' if beat else 'non'} |")
ok_c = n_scored > 0 and n_beat > n_scored / 2
w(f"\n**{'OK' if ok_c else 'ÉCHEC'} — {n_beat}/{n_scored} folds battus (majorité requise).**\n")

# ------------------------------------------------------- d. SPA a 1 candidat
w("## d. SPA de Hansen à 1 candidat contre Buy & Hold\n")
pnl_c, pnl_b = backtest(pos, r, COST), backtest(bh, r, COST)
spa = spa_test({"Meta": -pnl_c, "BuyHold": -pnl_b}, bench="BuyHold")
ok_d = spa["p_value"] < 0.05
w(f"t_SPA = {spa['t_spa']:.3f}, **p = {spa['p_value']:.4f}** (bootstrap stationnaire, "
  "H0 : Buy & Hold n'est battu par aucun candidat).\n")
w(f"**{'OK' if ok_d else 'ÉCHEC'} — seuil p < 0,05.**\n")

# ----------------------------------------------------------------- e. DSR
w(f"## e. DSR avec n_trials = {N_TRIALS} (total cumulé campagne ML, jamais 1)\n")
mc = trading_metrics(pnl_c)
de = dsr(mc["sharpe_daily"], mc["n"], VAR_TRIALS, n_trials=N_TRIALS,
         skew=mc["skew"], kurt_excess=mc["excess_kurt"])
ok_e = de["dsr"] > 0.95
w(f"Sharpe quotidien {mc['sharpe_daily']:+.4f}, σ²(SR essais) = {VAR_TRIALS:.4e}, "
  f"seuil SR₀ = {de['sr0_daily']:.4f}, z = {de['z']:+.2f}, **DSR = {de['dsr']:.3f}**.\n")
w(f"**{'OK' if ok_e else 'ÉCHEC'} — seuil DSR > 0,95.**\n")

# ------------------------------------------------------------------ verdict
allok = all((ok_a, ok_b, ok_c, ok_d, ok_e))
w("## Verdict de la batterie\n")
w("| Contrôle | Statut |")
w("|---|---|")
for lab, ok in (("a. stress de coûts ×3/×5", ok_a), ("b. stress de crise", ok_b),
                ("c. stabilité temporelle", ok_c), ("d. SPA 1 candidat", ok_d),
                (f"e. DSR (n_trials={N_TRIALS})", ok_e)):
    w(f"| {lab} | {'OK' if ok else 'ÉCHEC'} |")
w("")
w(f"### {'PASS RENFORCÉ' if allok else 'PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE'}\n")
if not allok:
    w("Aucune notification n'est émise : la règle réserve l'alerte au PASS "
      "RENFORCÉ complet (5 contrôles sur 5).")

out = ROOT / "results" / f"{TAG}_battery.md"
out.write_text("\n".join(L))
print("\n".join(L))
print(f"\n[BATTERIE] {'PASS_RENFORCE' if allok else 'ECHEC'}")
