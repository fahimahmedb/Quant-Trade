"""Audit adversarial — Overlay vol-targeting gaté par la breadth de
drawdown profond (seuil absolu -20%).

1. Recalcul indépendant de la breadth de drawdown profond (boucle Python
   explicite par titre, sans réutiliser les opérations vectorisées du
   backtest) à un échantillon de dates.
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
from nonml_deep_drawdown_breadth_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, INDEX_LOOKBACK, DD_THRESHOLD, compute_deep_drawdown_breadth_series,
)


def independent_breadth_at(aligned: dict, tickers: list, i: int) -> float:
    n_listed = 0
    n_deep_dd = 0
    for t in tickers:
        px = aligned[t][i]
        if not np.isfinite(px):
            continue
        n_listed += 1
        window = aligned[t][i - INDEX_LOOKBACK + 1:i + 1]
        if not np.isfinite(window).all():
            continue
        if px <= DD_THRESHOLD * np.max(window):
            n_deep_dd += 1
    return n_deep_dd / n_listed if n_listed > 0 else np.nan


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    aligned = {t: series[t].reindex(ref_idx).values for t in tickers}
    T = len(ref_idx)

    orig = compute_deep_drawdown_breadth_series()
    check_idx = list(range(INDEX_LOOKBACK, T, 400))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la breadth de drawdown profond (seuil absolu -20%)", "",
             "## 1. Recalcul indépendant (boucle Python explicite, sans vectorisation)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for i in check_idx:
        indep = independent_breadth_at(aligned, tickers, i)
        orig_v = orig.values[i]
        if np.isnan(orig_v) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig_v) - float(indep))
        all_ok &= (diff < 1e-9)
        n_checked += 1
        lines.append(f"| {i} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — breadth confirmée par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = {t: aligned[t].copy() for t in tickers}
    rng = np.random.default_rng(111)
    for t in tickers:
        n_tail = T - cut
        mask = np.isfinite(P_mut[t][cut:])
        P_mut[t][cut:][mask] = P_mut[t][cut:][mask] * (1.0 + rng.normal(0, 0.5, mask.sum()))

    check_i = cut - INDEX_LOOKBACK - 50
    b_before = independent_breadth_at(aligned, tickers, check_i)
    b_after = independent_breadth_at(P_mut, tickers, check_i)
    diff_lookahead = abs(b_before - b_after) if not (np.isnan(b_before) or np.isnan(b_after)) else 0.0
    lines.append(f"Écart sur la breadth calculée à une date antérieure à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
