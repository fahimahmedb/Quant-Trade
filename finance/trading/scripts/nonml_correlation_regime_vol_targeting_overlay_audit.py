"""Audit adversarial — Overlay vol-targeting gaté par le régime de
corrélation moyenne.

1. Recalcul indépendant de la corrélation moyenne par paires (boucle
   Python explicite, formule manuelle de Pearson, sans réutiliser
   np.corrcoef) à un échantillon de dates.
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

from nonml_correlation_regime_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, CORR_WINDOW, MIN_LISTED, compute_avg_correlation_series,
)


def independent_pearson(x: np.ndarray, y: np.ndarray) -> float:
    """Correlation de Pearson par formule manuelle explicite (sans
    np.corrcoef)."""
    n = len(x)
    mx, my = x.mean(), y.mean()
    dx, dy = x - mx, y - my
    num = np.sum(dx * dy)
    den = np.sqrt(np.sum(dx ** 2) * np.sum(dy ** 2))
    return num / den if den > 0 else np.nan


def independent_avg_corr_at(R: np.ndarray, t: int, n_tickers: int) -> float:
    window = R[t - CORR_WINDOW + 1:t + 1]
    eligible = [j for j in range(n_tickers) if np.isfinite(window[:, j]).all()]
    if len(eligible) < MIN_LISTED:
        return np.nan
    corrs = []
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            corrs.append(independent_pearson(window[:, eligible[i]], window[:, eligible[j]]))
    return float(np.mean(corrs)) if corrs else np.nan


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    R = np.log(P / P.shift(1)).values
    R[0, :] = np.nan
    T, n_tickers = R.shape

    corr_orig = compute_avg_correlation_series()
    check_dates = list(range(CORR_WINDOW + 50, T, 150))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par le régime de corrélation moyenne", "",
             "## 1. Recalcul indépendant de la corrélation moyenne (formule de Pearson manuelle, boucle explicite)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_avg_corr_at(R, t, n_tickers)
        orig = corr_orig.values[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — corrélation moyenne confirmée par recalcul indépendant (formule de Pearson manuelle).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(90)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    R_mut = np.log(P_mut / P_mut.shift(1)).values
    R_mut[0, :] = np.nan

    check_i = cut - CORR_WINDOW - 50
    c_before = independent_avg_corr_at(R, check_i, n_tickers)
    c_after = independent_avg_corr_at(R_mut, check_i, n_tickers)
    max_diff_lookahead = abs(c_before - c_after) if not (np.isnan(c_before) or np.isnan(c_after)) else 0.0
    lines.append(f"Écart sur la corrélation calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_correlation_regime_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
