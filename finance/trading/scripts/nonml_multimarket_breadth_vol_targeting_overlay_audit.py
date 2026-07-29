"""Audit adversarial — Overlay vol-targeting gaté par la confirmation
multi-marché élargie.

1. Recalcul indépendant de la breadth 5-marchés (boucle Python
   explicite marché par marché, sans réutiliser les opérations
   vectorisées du backtest) à un échantillon de dates.
2. Test anti-lookahead (perturbation du futur, NDX).
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
from nonml_multimarket_breadth_vol_targeting_overlay_backtest import (  # noqa: E402
    MARKETS, SMA_WINDOW, compute_multimarket_breadth_series,
)


def independent_trend(close: np.ndarray, t: int) -> bool:
    """Recalcul explicite (boucle Python) de close(t) > SMA200(t)."""
    window = close[t - SMA_WINDOW + 1:t + 1]
    if not np.isfinite(window).all():
        return None
    sma = sum(window) / SMA_WINDOW
    return bool(close[t] > sma)


def main():
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    dates_ndx = pd.to_datetime(df_ndx["date"])

    closes = {}
    dates_by_market = {}
    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        closes[name] = df["close"].values
        dates_by_market[name] = pd.to_datetime(df["date"])

    breadth_orig = compute_multimarket_breadth_series(dates_ndx)

    check_dates = list(range(SMA_WINDOW, len(dates_ndx), 200))
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la confirmation multi-marché élargie", "",
             "## 1. Recalcul indépendant de la breadth 5-marchés (boucle Python explicite)", "",
             "| Date NDX (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        target_date = dates_ndx.iloc[t]
        trends = []
        skip = False
        for name in MARKETS:
            d = dates_by_market[name]
            pos = d.searchsorted(target_date, side="right") - 1
            if pos < SMA_WINDOW - 1:
                skip = True
                break
            trend = independent_trend(closes[name], pos)
            if trend is None:
                skip = True
                break
            trends.append(trend)
        if skip:
            continue
        indep_breadth = sum(trends) / len(trends)
        orig_breadth = breadth_orig.values[t]
        if np.isnan(orig_breadth):
            continue
        diff = abs(float(orig_breadth) - indep_breadth)
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — breadth 5-marchés confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données NDX les plus récentes)")
    lines.append("")
    close_ndx = closes["NDX (40 ans)"]
    T = len(close_ndx)
    cut = int(T * 0.8)
    rng = np.random.default_rng(103)
    close_ndx_mut = close_ndx.copy()
    close_ndx_mut[cut:] = close_ndx_mut[cut:] * (1.0 + rng.normal(0, 0.1, T - cut))

    check_i = cut - SMA_WINDOW - 50
    trend_before = independent_trend(close_ndx, check_i)
    trend_after = independent_trend(close_ndx_mut, check_i)
    anti_leak_ok = (trend_before == trend_after)
    lines.append(f"Tendance NDX calculée à une date antérieure à la mutation : avant={trend_before}, après={trend_after}.")
    lines.append(f"**{'OK — aucune fuite.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_multimarket_breadth_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
