"""Batterie de validation renforcée (Règle 9) — #261 (tilt Amihud
illiquidité), ADAPTÉE au format PORTEFEUILLE multi-actifs
(spécification pré-enregistrée dans
`PREREG_amihud_illiquidity_tilt_pass_validation_battery.md`, committée
avant ce script).

Réutilise STRICTEMENT (Règle 7) les fonctions de contrôle a-e déjà
écrites et validées au #259
(`nonml_momentum_turnover_doublesort_pass_validation_battery.py`) --
génériques sur des paires (rendement brut, turnover) candidat/référence,
aucune modification. Seule la reconstruction des séries change (tilt
Amihud vs Buy&Hold équipondéré, au lieu du double-tri momentum+turnover
vs momentum seul).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_momentum_turnover_doublesort_pass_validation_battery import (  # noqa: E402
    check_a_cost_stress, check_b_crisis_stress, check_c_temporal_stability,
    check_d_spa, check_e_dsr,
)
from nonml_amihud_illiquidity_tilt_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day,
    ILLIQ_WINDOW, REBAL_EVERY, COST_BPS, TERCILE,
)


def build_raw_series():
    """Reconstruit (rendement brut, turnover, dates) pour le tilt
    illiquidité (candidat) et Buy&Hold équipondéré (référence), avant
    application des coûts."""
    close_series = load_all_prices()
    vol_series = load_all_volume()
    tickers = sorted(set(close_series.keys()) & set(vol_series.keys()))
    ref_idx = None
    for t in tickers:
        ref_idx = close_series[t].index if ref_idx is None else ref_idx.union(close_series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: close_series[t].reindex(ref_idx) for t in tickers})
    V = pd.DataFrame({t: vol_series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    exists = np.isfinite(P.values)
    R = np.log(P / P.shift(1))
    R.iloc[0, :] = 0.0
    R_safe = np.nan_to_num(R.values, nan=0.0)

    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R.values) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg = pd.DataFrame(illiq_daily).rolling(ILLIQ_WINDOW).mean().values

    weights_illiq = np.zeros((T, n_tickers))
    weights_bh = np.zeros((T, n_tickers))
    n_top = max(1, int(round(n_tickers * TERCILE)))

    rebal_dates = list(range(ILLIQ_WINDOW, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        illiq = illiq_avg[t]
        eligible = np.where(np.isfinite(illiq) & (illiq > 0))[0]
        n_top_t = min(n_top, len(eligible))
        if n_top_t > 0:
            top_idx = eligible[np.argsort(-illiq[eligible])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_illiq[t:end] = w
        listed = exists[t]
        n_listed = listed.sum()
        if n_listed > 0:
            weights_bh[t:end] = listed.astype(float) / n_listed

    weights_illiq = lag_one_day(weights_illiq)
    weights_bh = lag_one_day(weights_bh)

    start = ILLIQ_WINDOW
    raw_illiq = (weights_illiq[start:] * R_safe[start:]).sum(axis=1)
    raw_bh = (weights_bh[start:] * R_safe[start:]).sum(axis=1)
    turn_illiq = np.abs(np.diff(weights_illiq[start:], axis=0, prepend=weights_illiq[start:start+1])).sum(axis=1) / 2.0
    turn_bh = np.abs(np.diff(weights_bh[start:], axis=0, prepend=weights_bh[start:start+1])).sum(axis=1) / 2.0
    dates = P.index[start:]
    return raw_illiq, turn_illiq, raw_bh, turn_bh, dates


def main():
    name = "amihud_illiquidity_tilt"
    raw_illiq, turn_illiq, raw_bh, turn_bh, dates = build_raw_series()
    cost_bps = COST_BPS

    lines = [f"# Batterie de validation renforcée — {name} (adaptée au format portefeuille)",
             "",
             f"Coût pré-enregistré : {cost_bps:.1f} bps. {len(raw_illiq)} séances. "
             "Candidat = tilt Amihud illiquidité (#261). "
             "Référence = Buy&Hold équipondéré (univers).",
             ""]

    lines.append("## a. Stress de coûts (1x, 3x, 5x)")
    lines.append("")
    lines.append("| Coût (bps) | Sharpe candidat | Sharpe référence | Rendement candidat | Rendement référence | PASS |")
    lines.append("|---|---|---|---|---|---|")
    ok_a, rows_a = check_a_cost_stress(raw_illiq, turn_illiq, raw_bh, turn_bh, cost_bps)
    for cost, s_c, s_r, r_c, r_r, ok in rows_a:
        lines.append(f"| {cost:.1f} | {s_c:+.2f} | {s_r:+.2f} | {100*r_c:+.1f}% | {100*r_r:+.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_a else 'ÉCHEC'} — tient à 5x le coût nominal : {'oui' if ok_a else 'NON'}.**")
    lines.append("")

    lines.append("## b. Stress de crise (MDD candidat vs référence sur fenêtres historiques connues)")
    lines.append("")
    lines.append("| Fenêtre | Séances dispo | MDD candidat | MDD référence | Pas pire que référence |")
    lines.append("|---|---|---|---|---|")
    ok_b, rows_b, any_window = check_b_crisis_stress(raw_illiq, turn_illiq, raw_bh, turn_bh, dates, cost_bps)
    for label, n, mdd_c, mdd_r, ok in rows_b:
        if mdd_c is None:
            lines.append(f"| {label} | {n} | -- | -- | hors couverture (<20 séances) |")
        else:
            lines.append(f"| {label} | {n} | {mdd_c:.1f}% | {mdd_r:.1f}% | {'OUI' if ok else 'non'} |")
    lines.append("")
    if not any_window:
        lines.append("**PENDING — aucune fenêtre de crise couverte par l'historique disponible (2021-2026, "
                     "univers NDX-100 prix+volume) : ce contrôle ne peut pas être exécuté, il ne doit PAS "
                     "être compté comme un OK silencieux (Règle 5).**")
    else:
        lines.append(f"**{'OK' if ok_b else 'ÉCHEC'} — MDD jamais pire que la référence sur les fenêtres couvertes : {'oui' if ok_b else 'NON'}.**")
    lines.append("")

    lines.append("## c. Stabilité temporelle (folds non chevauchants + embargo 5j)")
    lines.append("")
    lines.append("| Fold | Séances | Sharpe candidat | Sharpe référence | Bat référence |")
    lines.append("|---|---|---|---|---|")
    ok_c, rows_c, n_beat, n_scored = check_c_temporal_stability(raw_illiq, turn_illiq, raw_bh, turn_bh, cost_bps)
    for k, n, s_c, s_r, beat in rows_c:
        lines.append(f"| {k} | {n} | {s_c:+.2f} | {s_r:+.2f} | {'OUI' if beat else 'non'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_c else 'ÉCHEC'} — bat la référence sur {n_beat}/{n_scored} folds "
                 f"(majorité {'atteinte' if ok_c else 'NON atteinte'}).**")
    lines.append("")

    lines.append("## d. SPA à 1 candidat contre la référence")
    lines.append("")
    ok_d, p_spa = check_d_spa(raw_illiq, turn_illiq, raw_bh, turn_bh, cost_bps)
    lines.append(f"p-value SPA : {p_spa:.4f}")
    lines.append(f"**{'OK' if ok_d else 'ÉCHEC'} — significatif à 5% : {'oui' if ok_d else 'NON'}.**")
    lines.append("")

    lines.append("## e. DSR avec n_trials = taille totale du backlog (jamais 1)")
    lines.append("")
    e_res = check_e_dsr(raw_illiq, turn_illiq, cost_bps)
    if e_res is None:
        lines.append("**PENDING — n_trials ou var_trials introuvable dans le backlog.**")
        ok_e = False
    else:
        n_trials, n_extracted, var_trials, d = e_res
        ok_e = d >= 0.95
        lines.append(f"n_trials = {n_trials} (taille du backlog après le #261), "
                     f"Var(Sharpe essais) estimée sur {n_extracted} Sharpe extraits du backlog "
                     f"= {var_trials:.6f} (échelle journalière).")
        lines.append(f"DSR = {d:.4f}")
        lines.append(f"**{'OK' if ok_e else 'ÉCHEC'} — DSR ≥ 0.95 : {'oui' if ok_e else 'NON'}.**")
    lines.append("")

    n_ok = sum([ok_a, ok_b, ok_c, ok_d, ok_e])
    lines.append(f"## Verdict global : {n_ok}/5")
    lines.append("")
    lines.append(f"**{'PASS RENFORCÉ (5/5)' if n_ok == 5 else f'PAS de PASS RENFORCÉ ({n_ok}/5)'}.**")

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_pass_validation_battery.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
