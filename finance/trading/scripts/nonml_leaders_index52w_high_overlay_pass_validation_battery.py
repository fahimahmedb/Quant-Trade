"""Batterie de validation renforcée (Règle 9) pour le #38 (Leaders
52-semaines + overlay 52w-high indice) -- spécification pré-enregistrée
dans PREREG_leaders_index52w_high_overlay_pass_validation_battery.md
(cycle #161), committée AVANT tout calcul de ce script.

Le #38 est une stratégie de PORTEFEUILLE (poids sur ~100 titres NDX-100),
pas un overlay scalaire sur un seul actif -- ne réutilise donc PAS le
format `pos x r_asset` de nonml_pass_validation_battery.py. Réutilise à
la place les poids déjà committés de
`nonml_leaders_index52w_high_overlay_backtest.py::build_weights()` (Règle
7 : pas de réimplémentation divergente), et applique les mêmes 5
contrôles a-e, même convention de coût/turnover, même référence que le
PREREG original du #38 (portefeuille Leaders 1.0x, PAS Buy&Hold).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr  # noqa: E402
from volatility import spa_test  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    build_weights, COST_BPS,
)
from nonml_pass_validation_battery import (  # noqa: E402
    approx_var_trials, parse_backlog_n_trials, CRISIS_WINDOWS,
)

EMBARGO = 5
N_FOLDS = 4


def portfolio_pnl(weights, R, cost_bps, mask=None):
    w = weights if mask is None else weights[mask]
    r = R if mask is None else R[mask]
    turn = np.abs(np.diff(w, axis=0, prepend=w[0:1])).sum(axis=1) / 2.0
    return (w * r).sum(axis=1) - turn * (cost_bps / 1e4)


def total_return(pnl):
    return float(np.cumprod(1.0 + pnl)[-1] - 1.0)


def main():
    dates_full, weights_base, weights_lev, R, _ = build_weights()
    # start = premier indice avec poids non nuls (fin du lookback 252j)
    nz = np.where(weights_base.sum(axis=1) > 0)[0]
    start = int(nz[0])
    w_base, w_lev = weights_base[start:], weights_lev[start:]
    R_s = R[start:]
    dates = pd.to_datetime(dates_full[start:])

    lines = ["# Batterie de validation renforcée (Règle 9) — leaders_index52w_high_overlay (cycle #38)",
             "",
             f"Candidat : Leaders + overlay 52w-high indice ×2.0. Référence : portefeuille "
             f"Leaders 1.0x (cycle #4), **PAS Buy&Hold** — même convention que le PREREG "
             f"original du #38. Coût pré-enregistré {COST_BPS:.0f} bps. {len(R_s)} séances "
             f"({dates[0].date()} → {dates[-1].date()}). Les 5 contrôles doivent TOUS passer "
             "pour un PASS RENFORCÉ.", ""]

    # ------------------------------------------------------------- a. couts
    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | OK |")
    lines.append("|---|---|---|---|---|---|")
    ok_a = True
    for mult in (1, 3, 5):
        cost = COST_BPS * mult
        pnl_b = portfolio_pnl(w_base, R_s, cost)
        pnl_l = portfolio_pnl(w_lev, R_s, cost)
        me_b, me_l = trading_metrics(pnl_b), trading_metrics(pnl_l)
        ret_b, ret_l = total_return(pnl_b), total_return(pnl_l)
        ok = (me_l["sharpe_ann"] > me_b["sharpe_ann"]) and (ret_l > ret_b)
        ok_a &= ok
        lines.append(f"| {cost:.0f} | {me_l['sharpe_ann']:+.2f} | {me_b['sharpe_ann']:+.2f} | "
                      f"{100*ret_l:+.1f}% | {100*ret_b:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient jusqu'à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    # ------------------------------------------------------------- b. crise
    lines.append("## b. Stress de crise (MDD candidat vs référence)")
    lines.append("")
    lines.append("| Fenêtre | Séances | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, any_window = True, False
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
            continue
        any_window = True
        pnl_b = portfolio_pnl(w_base, R_s, COST_BPS, mask.values)
        pnl_l = portfolio_pnl(w_lev, R_s, COST_BPS, mask.values)
        mdd_b = trading_metrics(pnl_b)["max_drawdown_pct"]
        mdd_l = trading_metrics(pnl_l)["max_drawdown_pct"]
        ok = mdd_l >= mdd_b - 1.0
        ok_b &= ok
        lines.append(f"| {label} | {n} | {mdd_l:.1f}% | {mdd_b:.1f}% | {'OUI' if ok else 'non'} |")
    ok_b = ok_b and any_window
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible "
                      "pour ce candidat (échantillon récent, 2022-2026) : ce contrôle ne peut pas "
                      "être exécuté, il ne doit PAS être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'}.**")
    lines.append("")

    # --------------------------------------------------- c. stabilite temp.
    lines.append(f"## c. Stabilité temporelle ({N_FOLDS} folds non chevauchants + embargo {EMBARGO}j)")
    lines.append("")
    lines.append("| Fold | Séances | Période | Sharpe candidat | Sharpe référence | Candidat > référence |")
    lines.append("|---|---|---|---|---|---|")
    T = len(R_s)
    flen = T // N_FOLDS
    n_beat = n_scored = 0
    for k in range(N_FOLDS):
        f0 = k * flen + (EMBARGO if k > 0 else 0)
        f1 = (k + 1) * flen if k < N_FOLDS - 1 else T
        if f1 - f0 < 30:
            continue
        idx_mask = np.zeros(T, dtype=bool)
        idx_mask[f0:f1] = True
        pnl_b = portfolio_pnl(w_base, R_s, COST_BPS, idx_mask)
        pnl_l = portfolio_pnl(w_lev, R_s, COST_BPS, idx_mask)
        s_b = trading_metrics(pnl_b)["sharpe_ann"]
        s_l = trading_metrics(pnl_l)["sharpe_ann"]
        beat = s_l > s_b
        n_beat += int(beat)
        n_scored += 1
        lines.append(f"| {k+1} | {f1-f0} | {dates.iloc[f0].strftime('%m/%Y')}→{dates.iloc[f1-1].strftime('%m/%Y')} | "
                      f"{s_l:+.2f} | {s_b:+.2f} | {'OUI' if beat else 'non'} |")
    ok_c = n_scored > 0 and n_beat > n_scored / 2
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — {n_beat}/{n_scored} folds battus (majorité requise).**")
    lines.append("")

    # --------------------------------------------------- d. SPA 1 candidat
    lines.append("## d. SPA de Hansen à 1 candidat contre la référence")
    lines.append("")
    pnl_b_full = portfolio_pnl(w_base, R_s, COST_BPS)
    pnl_l_full = portfolio_pnl(w_lev, R_s, COST_BPS)
    spa = spa_test({"candidat": -pnl_l_full, "reference": -pnl_b_full}, bench="reference")
    ok_d = spa["p_value"] < 0.05
    lines.append(f"t_SPA = {spa['t_spa']:.3f}, **p = {spa['p_value']:.4f}** (bootstrap stationnaire, "
                 "H0 : la référence Leaders 1.0x n'est battue par aucun candidat).")
    lines.append("")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — seuil p < 0,05.**")
    lines.append("")

    # ------------------------------------------------------------- e. DSR
    lines.append("## e. DSR avec n_trials = taille du backlog AVANT ce cycle (jamais 1)")
    lines.append("")
    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    me_l = trading_metrics(pnl_l_full)
    var_trials = var_trials_annual / 252.0
    de = dsr(me_l["sharpe_daily"], me_l["n"], var_trials, n_trials=n_trials,
             skew=me_l["skew"], kurt_excess=me_l["excess_kurt"])
    ok_e = de["dsr"] > 0.95
    lines.append(f"n_trials={n_trials} (backlog avant ce cycle), var(SR essais) extraite sur "
                 f"{n_extracted} Sharpe du backlog = {var_trials_annual:.4e} (annualisée) → "
                 f"{var_trials:.4e} (journalière). Sharpe quotidien {me_l['sharpe_daily']:+.4f}, "
                 f"seuil SR₀ = {de['sr0_daily']:.4f}, z = {de['z']:+.2f}, **DSR = {de['dsr']:.3f}**.")
    lines.append("")
    lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — seuil DSR > 0,95.**")
    lines.append("")

    # ---------------------------------------------------------- verdict
    allok = all((ok_a, ok_b, ok_c, ok_d, ok_e))
    lines.append("## Verdict de la batterie")
    lines.append("")
    lines.append("| Contrôle | Statut |")
    lines.append("|---|---|")
    for lab, ok in (("a. stress de coûts ×3/×5", ok_a),
                    ("b. stress de crise", ok_b),
                    ("c. stabilité temporelle", ok_c),
                    ("d. SPA 1 candidat", ok_d),
                    (f"e. DSR (n_trials={n_trials})", ok_e)):
        lines.append(f"| {lab} | {'OK' if ok else 'ÉCHEC'} |")
    lines.append("")
    lines.append(f"### {'PASS RENFORCÉ' if allok else 'PASS niveau 1 SEULEMENT — batterie renforcée ÉCHOUÉE'}")
    if not allok:
        lines.append("")
        lines.append("Aucune notification Telegram n'est émise (réservée au PASS RENFORCÉ complet).")

    out = ROOT / "results" / "nonml_leaders_index52w_high_overlay_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
