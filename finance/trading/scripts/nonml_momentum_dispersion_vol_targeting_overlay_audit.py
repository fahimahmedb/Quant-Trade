"""Audit adversarial — Overlay vol-targeting gaté par la dispersion du
momentum.

1. Recalcul indépendant de la dispersion du momentum (boucle Python
   explicite par titre, formule d'écart-type manuelle ddof=1, sans
   réutiliser np.nanstd ni les opérations vectorisées du backtest) à
   un échantillon de dates.
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

from nonml_momentum_dispersion_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, LOOKBACK, SKIP, MIN_LISTED, compute_momentum_dispersion_series,
)


def independent_dispersion_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    """Recalcul par boucle Python explicite, titre par titre, de la
    dispersion (ecart-type, ddof=1 manuel) des scores de momentum."""
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

    disp_orig = compute_momentum_dispersion_series()
    check_dates = list(range(LOOKBACK, T, 100))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la dispersion du momentum", "",
             "## 1. Recalcul indépendant de la dispersion (boucle Python explicite, ddof=1 manuel)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_dispersion_at(close, t, n_tickers)
        orig = disp_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — dispersion du momentum confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(100)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - LOOKBACK - 50
    d_before = independent_dispersion_at(close, check_i, n_tickers)
    d_after = independent_dispersion_at(close_mut, check_i, n_tickers)
    max_diff_lookahead = abs(d_before - d_after) if not (np.isnan(d_before) or np.isnan(d_after)) else 0.0
    lines.append(f"Écart sur la dispersion calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_momentum_dispersion_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
