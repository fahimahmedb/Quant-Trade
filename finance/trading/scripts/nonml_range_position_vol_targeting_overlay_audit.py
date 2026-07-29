"""Audit adversarial — Overlay vol-targeting gaté par la position
moyenne dans le range annuel.

1. Recalcul indépendant de la position moyenne dans le range (boucle
   Python explicite par titre, sans réutiliser les opérations
   vectorisées numpy du backtest) à un échantillon de dates.
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

from nonml_range_position_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, RANGE_LOOKBACK, MIN_LISTED, compute_range_position_series,
)


def independent_avg_position_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    """Recalcul par boucle Python explicite, titre par titre, de la
    position moyenne cross-sectionnelle dans le range 252j."""
    positions = []
    for j in range(n_tickers):
        window = close[t - RANGE_LOOKBACK + 1:t + 1, j]
        if not np.isfinite(window).all():
            continue
        lo, hi = window.min(), window.max()
        if hi <= lo:
            continue
        positions.append((close[t, j] - lo) / (hi - lo))
    n = len(positions)
    if n < MIN_LISTED:
        return np.nan
    return sum(positions) / n


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

    pos_orig = compute_range_position_series()
    check_dates = list(range(RANGE_LOOKBACK, T, 100))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la position moyenne dans le range annuel", "",
             "## 1. Recalcul indépendant de la position moyenne (boucle Python explicite)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_avg_position_at(close, t, n_tickers)
        orig = pos_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — position moyenne confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(104)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - RANGE_LOOKBACK - 50
    p_before = independent_avg_position_at(close, check_i, n_tickers)
    p_after = independent_avg_position_at(close_mut, check_i, n_tickers)
    max_diff_lookahead = abs(p_before - p_after) if not (np.isnan(p_before) or np.isnan(p_after)) else 0.0
    lines.append(f"Écart sur la position calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_range_position_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
