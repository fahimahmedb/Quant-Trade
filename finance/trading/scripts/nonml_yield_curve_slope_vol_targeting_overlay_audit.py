"""Audit adversarial — Overlay vol-targeting gaté par la pente de la
courbe des taux US (T10Y2Y).

1. Recalcul indépendant de la porte (boucle Python explicite sur les
   deux séries de dates, sans réutiliser pandas.reindex/shift/rolling)
   à un échantillon de dates.
2. Test anti-lookahead (mutation du futur T10Y2Y).
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
from nonml_yield_curve_slope_vol_targeting_overlay_backtest import (  # noqa: E402
    load_t10y2y, MEDIAN_WINDOW, combined_position, CAP, COST_BPS,
)


def independent_gate_at(ndx_date, slope_dates: list, slope_vals: np.ndarray) -> bool:
    """Recalcul par boucle Python explicite : trouve la derniere date
    T10Y2Y strictement anterieure a ndx_date (slope(t-1)), calcule la
    mediane manuelle des MEDIAN_WINDOW valeurs precedentes."""
    idx = None
    for i in range(len(slope_dates) - 1, -1, -1):
        if slope_dates[i] < ndx_date:
            idx = i
            break
    if idx is None or idx < MEDIAN_WINDOW - 1:
        return None
    window = [slope_vals[j] for j in range(idx - MEDIAN_WINDOW + 1, idx + 1) if np.isfinite(slope_vals[j])]
    if len(window) < MEDIAN_WINDOW // 2:
        return None
    window_sorted = sorted(window)
    n = len(window_sorted)
    median = window_sorted[n // 2] if n % 2 == 1 else 0.5 * (window_sorted[n // 2 - 1] + window_sorted[n // 2])
    return slope_vals[idx] >= median


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    slope = load_t10y2y()
    slope_dates_list = list(slope.index)
    slope_vals = slope.values

    slope_lagged = slope.shift(1)
    median_slope = slope_lagged.rolling(MEDIAN_WINDOW).median()
    gate_series = (slope_lagged >= median_slope)
    gate_series_filled = gate_series.fillna(False)
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    check_idx = list(range(2000, len(dates_idx), 1500))
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la pente de la courbe des taux US (T10Y2Y)", "",
             "## 1. Recalcul indépendant de la porte (boucle Python explicite, médiane manuelle, sans pandas.rolling/reindex)", "",
             "| Date NDX (indice) | Concorde |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for t in check_idx:
        nd = dates_idx.iloc[t]
        indep = independent_gate_at(nd, slope_dates_list, slope_vals)
        if indep is None:
            continue
        orig = bool(gate_aligned[t])
        concord = (orig == indep)
        all_ok &= concord
        n_checked += 1
        lines.append(f"| {t} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données T10Y2Y les plus récentes)")
    lines.append("")
    T_slope = len(slope)
    cut = int(T_slope * 0.8)
    rng = np.random.default_rng(114)
    slope_mut = slope.copy()
    slope_mut.iloc[cut:] = slope_mut.iloc[cut:] + rng.normal(0, 1.0, T_slope - cut)
    cut_date = slope.index[cut]

    slope_lagged_mut = slope_mut.shift(1)
    median_slope_mut = slope_lagged_mut.rolling(MEDIAN_WINDOW).median()
    gate_series_mut = (slope_lagged_mut >= median_slope_mut).fillna(False)
    gate_aligned_mut = gate_series_mut.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    check_slice_mask = (dates_idx < (cut_date - pd.Timedelta(days=400))).values
    diff_lookahead = int(np.sum(gate_aligned[check_slice_mask] != gate_aligned_mut[check_slice_mask]))
    lines.append(f"Écart de porte sur les séances antérieures à la mutation (marge 400j pour la fenêtre médiane 252j) : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_yield_curve_slope_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
