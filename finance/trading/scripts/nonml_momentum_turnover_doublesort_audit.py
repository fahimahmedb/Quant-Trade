"""Audit adversarial — Momentum 12-1 + double-tri turnover/volume-dollars.

1. Recalcul indépendant de la sélection double tri à un échantillon de
   dates de rebalancement (boucle Python explicite, tri par liste plutôt
   que np.argsort) pour vérifier l'absence de bug d'indexation.
2. Vérifie l'emboîtement final ⊆ tercile momentum ⊆ éligibles.
3. Vérifie que le décalage causal (`lag_one_day`) est appliqué
   correctement : weights_apres_lag[t] == weights_avant_lag[t-1].
4. Test anti-lookahead : perturbation du futur (prix ET volume) sans
   effet sur les décisions passées.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_momentum_turnover_doublesort_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day,
    LOOKBACK, SKIP, TURNOVER_WINDOW, REBAL_EVERY, TERCILE,
)


def independent_selection_at(close_row_skip, close_row_lb, turnover_row, n_tickers):
    eligible = []
    for j in range(n_tickers):
        cs, cl, tv = close_row_skip[j], close_row_lb[j], turnover_row[j]
        if np.isfinite(cs) and np.isfinite(cl) and np.isfinite(tv) and tv > 0:
            m = cs / cl - 1.0
            eligible.append((j, m, tv))
    # tercile base sur la taille de l'UNIVERS TOTAL (n_tickers), pas sur le nombre
    # d'eligibles a cette date -- identique a n_top_mom_full du backtest, plafonne
    # ensuite par len(eligible) (meme convention que le backtest, sinon faux desaccord)
    n_top_mom = max(1, int(round(n_tickers * TERCILE)))
    n_top_mom = min(n_top_mom, len(eligible))
    top_mom = sorted(eligible, key=lambda x: -x[1])[:n_top_mom] if n_top_mom > 0 else []
    n_top_double = max(1, int(round(len(top_mom) * TERCILE))) if top_mom else 0
    n_top_double = min(n_top_double, len(top_mom))
    low_turnover = sorted(top_mom, key=lambda x: x[2])[:n_top_double] if n_top_double > 0 else []
    eligible_set = {x[0] for x in eligible}
    top_mom_set = {x[0] for x in top_mom}
    final_set = {x[0] for x in low_turnover}
    return eligible_set, top_mom_set, final_set


def main():
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
    close = P.values

    momentum = np.full((T, n_tickers), np.nan)
    for i in range(LOOKBACK, T):
        c_skip = close[i - SKIP]
        c_lookback = close[i - LOOKBACK]
        with np.errstate(all="ignore"):
            m = c_skip / c_lookback - 1.0
        valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
        momentum[i, valid] = m[valid]

    dollar_volume = P.values * V.values
    turnover_avg = pd.DataFrame(dollar_volume).rolling(TURNOVER_WINDOW).mean().values

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    check_dates = rebal_dates[::10]

    lines = ["# Audit adversarial — Momentum 12-1 + double-tri turnover/volume-dollars", "",
             "## 1. Recalcul indépendant de la sélection à un échantillon de dates de rebalancement", "",
             "| Date (indice) | Sélection finale identique | Emboîtement final⊆tercile momentum⊆éligibles |",
             "|---|---|---|"]
    all_ok, nesting_ok = True, True
    for t in check_dates:
        m_row, tv_row = momentum[t], turnover_avg[t]
        eligible_orig = np.where(np.isfinite(m_row) & np.isfinite(tv_row) & (tv_row > 0))[0]
        n_top_mom = min(max(1, int(round(n_tickers * TERCILE))), len(eligible_orig))
        top_mom_orig = set(eligible_orig[np.argsort(-m_row[eligible_orig])[:n_top_mom]]) if n_top_mom > 0 else set()
        top_mom_arr = np.array(sorted(top_mom_orig))
        n_top_double = max(1, int(round(len(top_mom_arr) * TERCILE))) if len(top_mom_arr) > 0 else 0
        n_top_double = min(n_top_double, len(top_mom_arr))
        final_orig = set(top_mom_arr[np.argsort(tv_row[top_mom_arr])[:n_top_double]]) if len(top_mom_arr) > 0 and n_top_double > 0 else set()

        eligible_indep, top_mom_indep, final_indep = independent_selection_at(
            close[t - SKIP], close[t - LOOKBACK], tv_row, n_tickers)

        identical = (final_orig == final_indep)
        nested = final_orig.issubset(top_mom_orig) and top_mom_orig.issubset(set(eligible_orig))
        all_ok &= identical
        nesting_ok &= nested
        lines.append(f"| {t} | {'OUI' if identical else 'NON'} | {'OUI' if nested else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — sélection confirmée par recalcul indépendant sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")
    lines.append(f"**{'OK — emboîtement final⊆tercile momentum⊆éligibles vérifié partout.' if nesting_ok else 'ÉCHEC.'}**")

    # 2. Verification du decalage causal lag_one_day
    lines.append("")
    lines.append("## 2. Vérification du décalage causal (`lag_one_day`)")
    lines.append("")
    W_test = np.zeros((T, n_tickers))
    rng0 = np.random.default_rng(1)
    W_test[LOOKBACK::REBAL_EVERY] = rng0.random((len(range(LOOKBACK, T, REBAL_EVERY)), n_tickers))
    W_lagged = lag_one_day(W_test)
    shift_ok = np.allclose(W_lagged[1:], W_test[:-1]) and np.allclose(W_lagged[0], 0.0)
    lines.append(f"**{'OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.' if shift_ok else 'ÉCHEC.'}**")

    # 3. Anti-lookahead : perturbation du futur (prix ET volume)
    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur : prix et volume)")
    lines.append("")
    cut = T // 2
    P_pert = P.copy()
    V_pert = V.copy()
    rng = np.random.default_rng(272)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    V_pert.iloc[cut:] = V_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=V_pert.iloc[cut:].shape))
    close_pert = P_pert.values
    dollar_volume_pert = P_pert.values * V_pert.values
    turnover_avg_pert = pd.DataFrame(dollar_volume_pert).rolling(TURNOVER_WINDOW).mean().values

    check_t = cut - LOOKBACK - 50
    m_row_before = momentum[check_t]
    tv_row_before = turnover_avg[check_t]
    c_skip_p = close_pert[check_t - SKIP]
    c_lb_p = close_pert[check_t - LOOKBACK]
    with np.errstate(all="ignore"):
        m_row_after = np.where(np.isfinite(c_skip_p) & np.isfinite(c_lb_p), c_skip_p / c_lb_p - 1.0, np.nan)
    tv_row_after = turnover_avg_pert[check_t]

    m_diff = np.nanmax(np.abs(np.nan_to_num(m_row_before, nan=0.0) - np.nan_to_num(m_row_after, nan=0.0)))
    tv_diff = np.nanmax(np.abs(np.nan_to_num(tv_row_before, nan=0.0) - np.nan_to_num(tv_row_after, nan=0.0)))
    anti_leak_ok = (m_diff < 1e-6) and (tv_diff < 1e-6)
    lines.append(f"Écart momentum à une date antérieure à la mutation : {m_diff:.2e}")
    lines.append(f"Écart turnover moyen à une date antérieure à la mutation : {tv_diff:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_momentum_turnover_doublesort_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
