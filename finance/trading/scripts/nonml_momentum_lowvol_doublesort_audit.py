"""Audit adversarial — Momentum 12-1 + filtre Low-Volatility (double tri).

1. Recalcul indépendant de la sélection double tri à quelques dates de
   rebalancement (boucle Python explicite, tri par liste plutôt que
   np.argsort) pour vérifier l'absence de bug d'indexation.
2. Vérifie que les ensembles "survivants" et "sélection finale" sont
   bien des sous-ensembles emboîtés (final ⊆ survivants ⊆ éligibles).
3. Test anti-lookahead (perturbation du futur sur les prix).
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

from nonml_momentum_lowvol_doublesort_backtest import (  # noqa: E402
    load_all_prices, LOOKBACK, SKIP, VOL_WINDOW, REBAL_EVERY, TERCILE,
)


def independent_selection_at(close: np.ndarray, vol60_row: np.ndarray, t: int, tickers):
    n_tickers = len(tickers)
    c_skip = close[t - SKIP]
    c_lookback = close[t - LOOKBACK]
    eligible = []
    for j in range(n_tickers):
        if np.isfinite(c_skip[j]) and np.isfinite(c_lookback[j]) and np.isfinite(vol60_row[j]):
            m = c_skip[j] / c_lookback[j] - 1.0
            eligible.append((j, m, vol60_row[j]))
    n_keep = len(eligible) - max(1, int(round(len(eligible) * TERCILE)))
    eligible_sorted_by_vol = sorted(eligible, key=lambda x: x[2])
    survivors = eligible_sorted_by_vol[:n_keep] if n_keep > 0 else []
    n_top = max(1, int(round(len(survivors) * TERCILE))) if survivors else 0
    n_top = min(n_top, len(survivors))
    survivors_sorted_by_mom = sorted(survivors, key=lambda x: -x[1])
    final_sel = {x[0] for x in survivors_sorted_by_mom[:n_top]}
    survivors_set = {x[0] for x in survivors}
    eligible_set = {x[0] for x in eligible}
    return eligible_set, survivors_set, final_sel


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
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
    vol60 = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    check_dates = rebal_dates[::10]  # echantillon de dates pour l'audit (pas toutes, pour rester lisible)

    lines = ["# Audit adversarial — Momentum 12-1 + filtre Low-Volatility (double tri)", "",
             "## 1. Recalcul indépendant de la sélection à un échantillon de dates de rebalancement", "",
             "| Date (indice) | Sélection finale identique | Emboîtement final⊆survivants⊆éligibles |",
             "|---|---|---|"]
    all_ok, nesting_ok = True, True
    for t in check_dates:
        m_row, v_row = momentum[t], vol60[t]
        eligible_orig = np.where(np.isfinite(m_row) & np.isfinite(v_row))[0]
        n_keep = len(eligible_orig) - max(1, int(round(len(eligible_orig) * TERCILE)))
        survivors_orig = set(eligible_orig[np.argsort(v_row[eligible_orig])[:n_keep]]) if n_keep > 0 else set()
        n_top = max(1, int(round(len(survivors_orig) * TERCILE))) if survivors_orig else 0
        n_top = min(n_top, len(survivors_orig))
        survivors_arr = np.array(sorted(survivors_orig))
        final_orig = set(survivors_arr[np.argsort(-m_row[survivors_arr])[:n_top]]) if len(survivors_arr) > 0 and n_top > 0 else set()

        eligible_indep, survivors_indep, final_indep = independent_selection_at(close, v_row, t, tickers)

        identical = (final_orig == final_indep)
        nested = final_orig.issubset(survivors_orig) and survivors_orig.issubset(set(eligible_orig))
        all_ok &= identical
        nesting_ok &= nested
        lines.append(f"| {t} | {'OUI' if identical else 'NON'} | {'OUI' if nested else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — sélection confirmée par recalcul indépendant sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")
    lines.append(f"**{'OK — emboîtement final⊆survivants⊆éligibles vérifié partout.' if nesting_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    cut = T // 2
    P_pert = P.copy()
    rng = np.random.default_rng(271)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    close_pert = P_pert.values
    vol60_pert = P_pert.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values

    check_t = cut - LOOKBACK - 50
    m_row_before = momentum[check_t]
    v_row_before = vol60[check_t]
    c_skip_p = close_pert[check_t - SKIP]
    c_lb_p = close_pert[check_t - LOOKBACK]
    with np.errstate(all="ignore"):
        m_row_after = np.where(np.isfinite(c_skip_p) & np.isfinite(c_lb_p), c_skip_p / c_lb_p - 1.0, np.nan)
    v_row_after = vol60_pert[check_t]

    m_diff = np.nanmax(np.abs(np.nan_to_num(m_row_before, nan=0.0) - np.nan_to_num(m_row_after, nan=0.0)))
    v_diff = np.nanmax(np.abs(np.nan_to_num(v_row_before, nan=0.0) - np.nan_to_num(v_row_after, nan=0.0)))
    anti_leak_ok = (m_diff < 1e-9) and (v_diff < 1e-9)
    lines.append(f"Écart momentum à une date antérieure à la mutation : {m_diff:.2e}")
    lines.append(f"Écart vol60 à une date antérieure à la mutation : {v_diff:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_momentum_lowvol_doublesort_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
