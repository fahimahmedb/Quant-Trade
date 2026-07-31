"""ML-4 -- batterie de validation renforcee (5 controles a-e du §2.4 de
ML_STRATEGY_BACKLOG.md / Regle 9 de PROTOCOLE_ANTI_SNOOPING.md), adaptee ML.

Ne doit tourner que sur un marche ayant passe le critere niveau 1 du PREREG §5.
Executee **separement par marche** : `spa_test` compare un candidat a UN SEUL
benchmark partage, donc AUCUN SPA joint multi-marches n'est tente (limite
mecanique deja rencontree cote non-ML aux cycles #150/#159). Un SPA et un DSR
distincts sont calcules sur chaque marche concerne.

Lit le .npz sauvegarde par ml_crossmarket_pooling_backtest.py (positions OOS,
rendements log t->t+1, dates, cout, var_trials, n_trials cumule).

Usage : python3 ml_crossmarket_pooling_battery.py <tag_marche> [<tag_marche> ...]
        tags : russell2000 | sp500 | dax
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
CAND = "LogitL2Pooled"
CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]

TAGS = sys.argv[1:]
if not TAGS:
    raise SystemExit("usage: ml_crossmarket_pooling_battery.py <tag_marche> [...]")


def pair(pos_a, pos_b, r_w, cost):
    return (trading_metrics(backtest(pos_a, r_w, cost)),
            trading_metrics(backtest(pos_b, r_w, cost)))


def criterion(mc, mb):
    """Critere niveau 1 du PREREG §5 : (Sharpe ET rendement) OU Calmar."""
    a = (mc["sharpe_ann"] > mb["sharpe_ann"]) and (mc["ann_return_pct"] > mb["ann_return_pct"])
    b = np.isfinite(mc["calmar"]) and np.isfinite(mb["calmar"]) and mc["calmar"] > mb["calmar"]
    return bool(a or b)


GLOBAL = {}
for TAG in TAGS:
    d = np.load(ROOT / "results" / f"ml_crossmarket_pooling_{TAG}_pnl.npz",
                allow_pickle=True)
    pos, r = d["pos"], d["r_asset"]
    dates = pd.to_datetime(d["dates"].astype(str))
    COST = float(d["cost_bps"])
    VAR_TRIALS, N_TRIALS = float(d["var_trials"]), int(d["n_trials"])
    MARKET = str(d["market"])
    bh = np.ones(len(r))

    L = []
    w = L.append
    w(f"# ML-4 — Batterie de validation renforcée — {MARKET}\n")
    w(f"Candidat `{CAND}`, coût pré-enregistré {COST:.0f} bps, {len(r)} séances "
      f"OOS ({dates[0]:%d/%m/%Y} → {dates[-1]:%d/%m/%Y}). Les 5 contrôles "
      "doivent TOUS passer pour un PASS RENFORCÉ **sur ce marché**.\n")
    w("Batterie exécutée **marché par marché** : `spa_test` compare un candidat "
      "à UN SEUL benchmark partagé, aucun SPA joint multi-marchés n'est tenté "
      "(PREREG §6, limite mécanique des cycles non-ML #150/#159).\n")

    # ----------------------------------------------------- a. stress de couts
    w("## a. Stress de coûts (×1, ×3, ×5)\n")
    w(f"| Coût (bps) | Sharpe {CAND} | Sharpe BH | Rdt ann. {CAND} | Rdt ann. BH | "
      f"Calmar {CAND} | Calmar BH | Critère |")
    w("|---|---|---|---|---|---|---|---|")
    ok_a = True
    for mult in (1, 3, 5):
        mc, mb = pair(pos, bh, r, COST * mult)
        ok = criterion(mc, mb)
        ok_a &= ok
        w(f"| {COST*mult:.0f} | {mc['sharpe_ann']:+.2f} | {mb['sharpe_ann']:+.2f} | "
          f"{mc['ann_return_pct']:+.1f} % | {mb['ann_return_pct']:+.1f} % | "
          f"{mc['calmar']:+.2f} | {mb['calmar']:+.2f} | {'OUI' if ok else 'non'} |")
    w(f"\n**{'OK' if ok_a else 'ÉCHEC'} — le critère doit tenir jusqu'à ×5 le "
      "coût nominal.**\n")

    # ----------------------------------------------------- b. stress de crise
    w(f"## b. Stress de crise (MDD {CAND} vs Buy & Hold)\n")
    w(f"| Fenêtre | Séances | MDD {CAND} | MDD BH | Pas pire que BH |")
    w("|---|---|---|---|---|")
    ok_b, any_window = True, False
    for label, d0, d1 in CRISIS_WINDOWS:
        m = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        nw = int(m.sum())
        if nw < 20:
            w(f"| {label} | {nw} | — | — | hors couverture (<20 séances) |")
            continue
        any_window = True
        mc, mb = pair(pos[m], bh[m], r[m], COST)
        ok = mc["max_drawdown_pct"] >= mb["max_drawdown_pct"] - 1.0  # tolérance 1 pt
        ok_b &= ok
        w(f"| {label} | {nw} | {mc['max_drawdown_pct']:.1f} % | "
          f"{mb['max_drawdown_pct']:.1f} % | {'OUI' if ok else 'non'} |")
    ok_b = ok_b and any_window
    w(f"\n**{'OK' if ok_b else ('PENDING — aucune fenêtre couverte' if not any_window else 'ÉCHEC')}.**\n")

    # ------------------------------------------------ c. stabilite temporelle
    w(f"## c. Stabilité temporelle ({N_FOLDS} folds non chevauchants + embargo "
      f"{EMBARGO} j)\n")
    w(f"| Fold | Séances | Période | Sharpe {CAND} | Sharpe BH | {CAND} > BH |")
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
          f"{mc['sharpe_ann']:+.2f} | {mb['sharpe_ann']:+.2f} | "
          f"{'OUI' if beat else 'non'} |")
    ok_c = n_scored > 0 and n_beat > n_scored / 2
    w(f"\n**{'OK' if ok_c else 'ÉCHEC'} — {n_beat}/{n_scored} folds battus "
      "(majorité requise).**\n")

    # --------------------------------------------------- d. SPA a 1 candidat
    w("## d. SPA de Hansen à 1 candidat contre Buy & Hold\n")
    pnl_c, pnl_b = backtest(pos, r, COST), backtest(bh, r, COST)
    spa = spa_test({CAND: -pnl_c, "BuyHold": -pnl_b}, bench="BuyHold")
    ok_d = spa["p_value"] < 0.05
    w(f"t_SPA = {spa['t_spa']:.3f}, **p = {spa['p_value']:.4f}** (bootstrap "
      "stationnaire, H0 : Buy & Hold n'est battu par aucun candidat).\n")
    w(f"**{'OK' if ok_d else 'ÉCHEC'} — seuil p < 0,05.**\n")

    # ------------------------------------------------------------- e. DSR
    w(f"## e. DSR avec n_trials = {N_TRIALS} (total cumulé campagne ML, jamais 1)\n")
    mc = trading_metrics(pnl_c)
    de = dsr(mc["sharpe_daily"], mc["n"], VAR_TRIALS, n_trials=N_TRIALS,
             skew=mc["skew"], kurt_excess=mc["excess_kurt"])
    ok_e = de["dsr"] > 0.95
    w(f"Sharpe quotidien {mc['sharpe_daily']:+.4f}, σ²(SR essais) = "
      f"{VAR_TRIALS:.4e}, seuil SR₀ = {de['sr0_daily']:.4f}, z = {de['z']:+.2f}, "
      f"**DSR = {de['dsr']:.3f}**.\n")
    w(f"**{'OK' if ok_e else 'ÉCHEC'} — seuil DSR > 0,95.**\n")

    # ---------------------------------------------------------------- verdict
    allok = all((ok_a, ok_b, ok_c, ok_d, ok_e))
    GLOBAL[MARKET] = allok
    w("## Verdict de la batterie (ce marché)\n")
    w("| Contrôle | Statut |")
    w("|---|---|")
    for lab, ok in (("a. stress de coûts ×3/×5", ok_a),
                    ("b. stress de crise", ok_b),
                    ("c. stabilité temporelle", ok_c),
                    ("d. SPA 1 candidat", ok_d),
                    (f"e. DSR (n_trials={N_TRIALS})", ok_e)):
        w(f"| {lab} | {'OK' if ok else 'ÉCHEC'} |")
    w("")
    w(f"### {'PASS RENFORCÉ (' + MARKET + ')' if allok else 'PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE (' + MARKET + ')'}\n")
    if not allok:
        w("Aucune notification n'est émise pour ce marché : la règle réserve "
          "l'alerte au PASS RENFORCÉ complet (5 contrôles sur 5).")

    out = ROOT / "results" / f"ml_crossmarket_pooling_{TAG}_battery.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\n[BATTERIE {MARKET}] {'PASS_RENFORCE' if allok else 'ECHEC'}\n")

print("== resume batterie ==")
for k, v in GLOBAL.items():
    print(f"   {k:<13} {'PASS_RENFORCE' if v else 'ECHEC'}")
