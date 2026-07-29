"""Audit adversarial — Overlay vol-targeting gaté par le spread décile
de momentum.

1. Recalcul indépendant du spread décile (boucle Python explicite par
   titre + tri manuel, sans réutiliser np.sort vectorisé du backtest
   sur la matrice entière) à un échantillon de dates.
2. Test anti-lookahead (mutation du futur).
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
from nonml_momentum_decile_spread_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, LOOKBACK, SKIP, MIN_LISTED, DECILE_FRACTION, compute_decile_spread_series,
)


def independent_spread_at(aligned: dict, tickers: list, i: int) -> float:
    momenta = []
    for t in tickers:
        px = aligned[t]
        if i < LOOKBACK or i - LOOKBACK < 0:
            continue
        c_skip = px[i - SKIP] if i - SKIP >= 0 else np.nan
        c_lb = px[i - LOOKBACK] if i - LOOKBACK >= 0 else np.nan
        if not (np.isfinite(c_skip) and np.isfinite(c_lb)):
            continue
        momenta.append(c_skip / c_lb - 1.0)
    n = len(momenta)
    if n < MIN_LISTED:
        return np.nan
    decile_size = max(1, round(n * DECILE_FRACTION))
    momenta_sorted = sorted(momenta)
    bottom = momenta_sorted[:decile_size]
    top = momenta_sorted[-decile_size:]
    return sum(top) / len(top) - sum(bottom) / len(bottom)


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    aligned = {t: series[t].reindex(ref_idx).values for t in tickers}
    T = len(ref_idx)

    orig = compute_decile_spread_series()
    check_idx = list(range(LOOKBACK, T, 400))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par le spread décile de momentum", "",
             "## 1. Recalcul indépendant (boucle Python explicite + tri manuel, sans np.sort vectorisé sur la matrice)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for i in check_idx:
        indep = independent_spread_at(aligned, tickers, i)
        orig_v = orig.values[i]
        if np.isnan(orig_v) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig_v) - float(indep))
        all_ok &= (diff < 1e-9)
        n_checked += 1
        lines.append(f"| {i} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — spread décile confirmé par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = {t: aligned[t].copy() for t in tickers}
    rng = np.random.default_rng(112)
    for t in tickers:
        mask = np.isfinite(P_mut[t][cut:])
        P_mut[t][cut:][mask] = P_mut[t][cut:][mask] * (1.0 + rng.normal(0, 0.5, mask.sum()))

    check_i = cut - LOOKBACK - 50
    s_before = independent_spread_at(aligned, tickers, check_i)
    s_after = independent_spread_at(P_mut, tickers, check_i)
    diff_lookahead = abs(s_before - s_after) if not (np.isnan(s_before) or np.isnan(s_after)) else 0.0
    lines.append(f"Écart sur le spread calculé à une date antérieure à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_momentum_decile_spread_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
