"""Audit adversarial — Double porte AND dispersion momentum + tendance
52w-high.

1. Recalcul indépendant des deux portes (formules explicites, sans
   réutiliser les fonctions vectorisées du backtest) à un échantillon
   de dates.
2. Test anti-lookahead (perturbation du futur).
3. Vérifie la logique AND (porte combinée ⊆ chaque porte individuelle).
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
from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, LOOKBACK, SKIP, MIN_LISTED, compute_momentum_dispersion_series,
)
from nonml_momentum_dispersion_trend_and_overlay_backtest import INDEX_LOOKBACK  # noqa: E402

INDEX_THRESHOLD = 0.95


def independent_dispersion_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    scores = []
    for j in range(n_tickers):
        if t < LOOKBACK:
            continue
        c_skip = close[t - SKIP, j]
        c_lb = close[t - LOOKBACK, j]
        if not (np.isfinite(c_skip) and np.isfinite(c_lb)):
            continue
        scores.append(c_skip / c_lb - 1.0)
    n = len(scores)
    if n < MIN_LISTED:
        return np.nan
    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / (n - 1)
    return var ** 0.5


def independent_trend_at(close_idx: np.ndarray, t: int) -> bool:
    window = close_idx[t - INDEX_LOOKBACK + 1:t + 1]
    if not np.isfinite(window).all():
        return None
    hi = window.max()
    return bool(close_idx[t] >= INDEX_THRESHOLD * hi)


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close_stocks = P.values

    df_idx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_idx)
    close_idx = df_idx["close"].values
    dates_idx = pd.to_datetime(df_idx["date"])

    disp_orig = compute_momentum_dispersion_series()

    check_dates_stocks = list(range(LOOKBACK, T, 150))
    lines = ["# Audit adversarial — Double porte AND dispersion momentum + tendance 52w-high", "",
             "## 1. Recalcul indépendant des deux portes (formules explicites)", "",
             "| Date dispersion (indice titres) | Écart dispersion |",
             "|---|---|"]
    all_ok = True
    for t in check_dates_stocks:
        indep = independent_dispersion_at(close_stocks, t, n_tickers)
        orig = disp_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")

    lines.append("")
    lines.append("| Date indice (indice NDX) | Écart tendance |")
    lines.append("|---|---|")
    for t in range(INDEX_LOOKBACK, len(close_idx), 700):
        indep_trend = independent_trend_at(close_idx, t)
        rolling_max = pd.Series(close_idx).rolling(INDEX_LOOKBACK).max().values
        orig_trend = bool(close_idx[t] >= INDEX_THRESHOLD * rolling_max[t]) if np.isfinite(rolling_max[t]) else None
        concord = (indep_trend == orig_trend)
        all_ok &= concord
        lines.append(f"| {t} | {'concorde' if concord else 'DIVERGENCE'} |")

    lines.append("")
    lines.append(f"**{'OK — dispersion et tendance confirmées par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut_stocks = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(106)
    P_mut.iloc[cut_stocks:] = P_mut.iloc[cut_stocks:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut_stocks:].shape))
    close_stocks_mut = P_mut.values
    check_i_stocks = cut_stocks - LOOKBACK - 50
    d_before = independent_dispersion_at(close_stocks, check_i_stocks, n_tickers)
    d_after = independent_dispersion_at(close_stocks_mut, check_i_stocks, n_tickers)
    diff_disp = abs(d_before - d_after) if not (np.isnan(d_before) or np.isnan(d_after)) else 0.0

    cut_idx = int(len(close_idx) * 0.8)
    close_idx_mut = close_idx.copy()
    rng2 = np.random.default_rng(1060)
    close_idx_mut[cut_idx:] = close_idx_mut[cut_idx:] * (1.0 + rng2.normal(0, 0.1, len(close_idx) - cut_idx))
    check_i_idx = cut_idx - INDEX_LOOKBACK - 50
    t_before = independent_trend_at(close_idx, check_i_idx)
    t_after = independent_trend_at(close_idx_mut, check_i_idx)
    trend_leak_ok = (t_before == t_after)

    lines.append(f"Écart dispersion à une date antérieure à la mutation : {diff_disp:.2e}")
    lines.append(f"Concordance tendance à une date antérieure à la mutation : {'OK' if trend_leak_ok else 'ÉCHEC'}")
    leak_ok = (diff_disp < 1e-9) and trend_leak_ok
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if leak_ok else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Vérification de la logique AND (porte combinée ⊆ chaque porte individuelle)")
    lines.append("")
    from nonml_trend_vol_targeting_overlay_backtest import near_high_mask  # noqa: E402
    trend_gate_full = near_high_mask(close_idx)
    median_disp = disp_orig.rolling(252).median()
    disp_gate_full = (disp_orig >= median_disp).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    and_gate_full = trend_gate_full & disp_gate_full
    subset_trend_ok = bool(np.all(~and_gate_full | trend_gate_full))
    subset_disp_ok = bool(np.all(~and_gate_full | disp_gate_full))
    lines.append(f"Porte AND ⊆ porte tendance : {'OK' if subset_trend_ok else 'ÉCHEC'}. "
                 f"Porte AND ⊆ porte dispersion : {'OK' if subset_disp_ok else 'ÉCHEC'}.")

    out = ROOT / "results" / "nonml_momentum_dispersion_trend_and_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
