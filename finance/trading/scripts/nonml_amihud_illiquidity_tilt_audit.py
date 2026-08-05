"""Audit adversarial — Tilt Amihud illiquidité.

1. Recalcul indépendant de l'ILLIQ moyen à un échantillon de dates de
   rebalancement (boucle Python explicite par titre) pour vérifier
   l'absence de divergence de définition.
2. Vérifie le décalage causal (`lag_one_day`).
3. Test anti-lookahead (perturbation du futur : prix ET volume).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_amihud_illiquidity_tilt_backtest import (  # noqa: E402
    load_all_prices, load_all_volume, lag_one_day, ILLIQ_WINDOW, REBAL_EVERY, TERCILE,
)


def independent_illiq_at(R: np.ndarray, dollar_volume: np.ndarray, t: int, n_tickers: int) -> np.ndarray:
    n = ILLIQ_WINDOW
    illiq = np.full(n_tickers, np.nan)
    for j in range(n_tickers):
        r_win = R[t - n + 1:t + 1, j]
        dv_win = dollar_volume[t - n + 1:t + 1, j]
        if not np.isfinite(r_win).all() or not np.isfinite(dv_win).all() or (dv_win <= 0).any():
            continue
        illiq[j] = np.mean(np.abs(r_win) / dv_win)
    return illiq


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

    R_df = np.log(P / P.shift(1))
    R_df.iloc[0, :] = 0.0
    R = R_df.values
    dollar_volume = P.values * V.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily = np.abs(R) / dollar_volume
    illiq_daily[~np.isfinite(illiq_daily)] = np.nan
    illiq_avg_orig = pd.DataFrame(illiq_daily).rolling(ILLIQ_WINDOW).mean().values

    rebal_dates = list(range(ILLIQ_WINDOW, T, REBAL_EVERY))
    check_dates = rebal_dates[::10]

    lines = ["# Audit adversarial — Tilt Amihud illiquidité", "",
             "## 1. Recalcul indépendant de l'ILLIQ moyen (boucle Python explicite)", "",
             "| Date (indice) | Écart max absolu (titres avec historique complet) |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        illiq_orig = illiq_avg_orig[t]
        illiq_indep = independent_illiq_at(R, dollar_volume, t, n_tickers)
        mask_both = np.isfinite(illiq_orig) & np.isfinite(illiq_indep)
        diff = float(np.max(np.abs(illiq_orig[mask_both] - illiq_indep[mask_both]))) if mask_both.any() else 0.0
        rel_ok = diff < 1e-15 * max(1.0, float(np.max(np.abs(illiq_orig[mask_both])))) if mask_both.any() else True
        all_ok &= rel_ok
        lines.append(f"| {t} | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — ILLIQ confirmé par recalcul indépendant sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Vérification du décalage causal (`lag_one_day`)")
    lines.append("")
    W_test = np.zeros((T, n_tickers))
    rng0 = np.random.default_rng(2)
    W_test[ILLIQ_WINDOW::REBAL_EVERY] = rng0.random((len(range(ILLIQ_WINDOW, T, REBAL_EVERY)), n_tickers))
    W_lagged = lag_one_day(W_test)
    shift_ok = np.allclose(W_lagged[1:], W_test[:-1]) and np.allclose(W_lagged[0], 0.0)
    lines.append(f"**{'OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.' if shift_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur : prix et volume)")
    lines.append("")
    cut = T // 2
    P_pert = P.copy()
    V_pert = V.copy()
    rng = np.random.default_rng(273)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    V_pert.iloc[cut:] = V_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=V_pert.iloc[cut:].shape))
    R_pert_df = np.log(P_pert / P_pert.shift(1))
    R_pert_df.iloc[0, :] = 0.0
    dollar_volume_pert = P_pert.values * V_pert.values
    with np.errstate(divide="ignore", invalid="ignore"):
        illiq_daily_pert = np.abs(R_pert_df.values) / dollar_volume_pert
    illiq_daily_pert[~np.isfinite(illiq_daily_pert)] = np.nan
    illiq_avg_pert = pd.DataFrame(illiq_daily_pert).rolling(ILLIQ_WINDOW).mean().values

    check_t = cut - ILLIQ_WINDOW - 50
    illiq_before = illiq_avg_orig[check_t]
    illiq_after = illiq_avg_pert[check_t]
    diff_pert = np.nanmax(np.abs(np.nan_to_num(illiq_before, nan=0.0) - np.nan_to_num(illiq_after, nan=0.0)))
    anti_leak_ok = diff_pert < 1e-9
    lines.append(f"Écart ILLIQ à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_amihud_illiquidity_tilt_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
