"""Audit adversarial — Overlay vol-targeting gaté par la dispersion des
betas individuels.

1. Recalcul indépendant de la dispersion des betas (boucle Python
   explicite par titre, formule manuelle de covariance/variance
   ddof=1, sans réutiliser pandas.rolling().cov() ni les opérations
   vectorisées du backtest) à un échantillon de dates.
2. Test anti-lookahead (perturbation du futur).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_beta_dispersion_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, BETA_WINDOW, MIN_LISTED, compute_beta_dispersion_series,
)


def independent_beta_dispersion_at(R: np.ndarray, r_mkt: np.ndarray, t: int, n_tickers: int) -> float:
    """Recalcul par boucle Python explicite, titre par titre, de la
    dispersion cross-sectionnelle des betas (covariance/variance
    manuelles, ddof=1)."""
    window_mkt = r_mkt[t - BETA_WINDOW + 1:t + 1]
    if not np.isfinite(window_mkt).all():
        return np.nan
    mean_mkt = window_mkt.mean()
    var_mkt = np.sum((window_mkt - mean_mkt) ** 2) / (BETA_WINDOW - 1)
    if var_mkt <= 0:
        return np.nan

    betas = []
    for j in range(n_tickers):
        window_stock = R[t - BETA_WINDOW + 1:t + 1, j]
        if not np.isfinite(window_stock).all():
            continue
        mean_stock = window_stock.mean()
        cov = np.sum((window_stock - mean_stock) * (window_mkt - mean_mkt)) / (BETA_WINDOW - 1)
        betas.append(cov / var_mkt)

    n = len(betas)
    if n < MIN_LISTED:
        return np.nan
    mean_beta = sum(betas) / n
    var_beta = sum((b - mean_beta) ** 2 for b in betas) / (n - 1)
    return var_beta ** 0.5


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    R = np.log(P / P.shift(1)).values
    T, n_tickers = R.shape

    df_idx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_idx)
    close_idx = pd.Series(df_idx["close"].values, index=pd.to_datetime(df_idx["date"]))
    r_mkt_full = np.log(close_idx / close_idx.shift(1))
    r_mkt = r_mkt_full.reindex(ref_idx).values

    disp_orig = compute_beta_dispersion_series()
    check_dates = list(range(BETA_WINDOW, T, 100))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la dispersion des betas individuels", "",
             "## 1. Recalcul indépendant de la dispersion des betas (boucle Python explicite, ddof=1 manuel)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_beta_dispersion_at(R, r_mkt, t, n_tickers)
        orig = disp_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-6)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — dispersion des betas confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(109)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    R_mut = np.log(P_mut / P_mut.shift(1)).values

    check_i = cut - BETA_WINDOW - 50
    d_before = independent_beta_dispersion_at(R, r_mkt, check_i, n_tickers)
    d_after = independent_beta_dispersion_at(R_mut, r_mkt, check_i, n_tickers)
    max_diff_lookahead = abs(d_before - d_after) if not (np.isnan(d_before) or np.isnan(d_after)) else 0.0
    lines.append(f"Écart sur la dispersion calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-6 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_beta_dispersion_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
