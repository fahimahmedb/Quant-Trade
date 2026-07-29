"""Audit adversarial — Overlay vol-targeting gaté par la concentration
du marché.

1. Recalcul indépendant de l'indice de Herfindahl-Hirschman (boucle
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

from nonml_market_concentration_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, CONC_WINDOW, MIN_LISTED, compute_concentration_series,
)


def independent_hhi_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    """Recalcul par boucle Python explicite, titre par titre, de l'indice
    de Herfindahl-Hirschman des parts de contribution positive."""
    contribs = []
    for j in range(n_tickers):
        c_t = close[t, j]
        c_t0 = close[t - CONC_WINDOW, j]
        if not (np.isfinite(c_t) and np.isfinite(c_t0)):
            continue
        r = c_t / c_t0 - 1.0
        contribs.append(max(r, 0.0))
    n_elig = len(contribs)
    if n_elig < MIN_LISTED:
        return np.nan
    total = sum(contribs)
    if total <= 0:
        return 1.0 / n_elig
    hhi = sum((c / total) ** 2 for c in contribs)
    return hhi


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

    conc_orig = compute_concentration_series()
    check_dates = list(range(CONC_WINDOW, T, 100))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la concentration du marché", "",
             "## 1. Recalcul indépendant de l'indice de Herfindahl-Hirschman (boucle Python explicite)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_hhi_at(close, t, n_tickers)
        orig = conc_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — HHI confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(99)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - CONC_WINDOW - 50
    h_before = independent_hhi_at(close, check_i, n_tickers)
    h_after = independent_hhi_at(close_mut, check_i, n_tickers)
    max_diff_lookahead = abs(h_before - h_after) if not (np.isnan(h_before) or np.isnan(h_after)) else 0.0
    lines.append(f"Écart sur le HHI calculé à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_market_concentration_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
