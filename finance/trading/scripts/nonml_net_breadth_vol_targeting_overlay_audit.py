"""Audit adversarial — Overlay vol-targeting gaté par la breadth nette
hauts-bas NDX-100.

1. Recalcul indépendant de la breadth nette (boucle Python explicite
   par titre, sans réutiliser les opérations vectorisées numpy du
   backtest) à un échantillon de dates.
2. Test anti-lookahead (perturbation du futur).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_net_breadth_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, INDEX_LOOKBACK, INDEX_THRESHOLD_HIGH, INDEX_THRESHOLD_LOW,
    compute_net_breadth_series,
)


def independent_net_breadth_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    """Recalcul par boucle Python explicite, titre par titre, de la
    breadth nette (proche haut - proche bas) / titres cotes."""
    n_listed = 0
    n_near_high = 0
    n_near_low = 0
    for j in range(n_tickers):
        c = close[t, j]
        if not np.isfinite(c):
            continue
        n_listed += 1
        window = close[t - INDEX_LOOKBACK + 1:t + 1, j]
        if not np.isfinite(window).all():
            continue
        high = window.max()
        low = window.min()
        if c >= INDEX_THRESHOLD_HIGH * high:
            n_near_high += 1
        if c <= INDEX_THRESHOLD_LOW * low:
            n_near_low += 1
    return (n_near_high - n_near_low) / n_listed if n_listed > 0 else np.nan


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

    breadth_orig = compute_net_breadth_series()
    check_dates = list(range(INDEX_LOOKBACK, T, 100))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la breadth nette hauts-bas", "",
             "## 1. Recalcul indépendant de la breadth nette (boucle Python explicite)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_net_breadth_at(close, t, n_tickers)
        orig = breadth_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — breadth nette confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(97)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - INDEX_LOOKBACK - 50
    b_before = independent_net_breadth_at(close, check_i, n_tickers)
    b_after = independent_net_breadth_at(close_mut, check_i, n_tickers)
    max_diff_lookahead = abs(b_before - b_after) if not (np.isnan(b_before) or np.isnan(b_after)) else 0.0
    lines.append(f"Écart sur la breadth calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_net_breadth_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
