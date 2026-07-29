"""Audit adversarial — Tilt sur l'asymétrie (skewness) individuelle.

1. Recalcul indépendant de la skewness à un échantillon de dates de
   rebalancement (boucle Python explicite par titre, formule G1
   corrigée du biais de Fisher-Pearson calculée à la main plutôt que
   pandas.rolling().skew()) pour vérifier l'absence de divergence de
   définition.
2. Test anti-lookahead (perturbation du futur).
3. Vérifie la mécanique de l'univers dynamique.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_skewness_tilt_backtest import load_all_prices, SKEW_WINDOW, REBAL_EVERY  # noqa: E402


def independent_skew_at(R: np.ndarray, t: int, n_tickers: int) -> np.ndarray:
    """Formule G1 (asymetrie corrigee du biais de Fisher-Pearson, meme
    definition que pandas.Series.skew()) calculee explicitement par une
    boucle Python, sans reutiliser pandas.rolling()."""
    n = SKEW_WINDOW
    skew = np.full(n_tickers, np.nan)
    for j in range(n_tickers):
        window = R[t - n + 1:t + 1, j]
        if not np.isfinite(window).all():
            continue
        mean = window.mean()
        dev = window - mean
        m2 = np.sum(dev ** 2) / n
        m3 = np.sum(dev ** 3) / n
        s = np.sqrt(np.sum(dev ** 2) / (n - 1))  # ecart-type echantillon (ddof=1)
        if s == 0:
            continue
        g1 = m3 / (m2 ** 1.5) if m2 > 0 else np.nan
        # correction du biais de Fisher-Pearson (formule pandas/scipy bias=False)
        skew[j] = (np.sqrt(n * (n - 1)) / (n - 2)) * g1
    return skew


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape

    R_df = np.log(P / P.shift(1))
    R_df.iloc[0, :] = 0.0
    R = R_df.values
    skew60_orig = R_df.rolling(SKEW_WINDOW).skew().values

    rebal_dates = list(range(SKEW_WINDOW, T, REBAL_EVERY))
    check_dates = rebal_dates[::10]

    lines = ["# Audit adversarial — Tilt sur l'asymétrie (skewness) individuelle", "",
             "## 1. Recalcul indépendant (formule G1 explicite vs pandas.rolling().skew())", "",
             "| Date (indice) | Écart max absolu (titres avec historique complet) |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        s_orig = skew60_orig[t]
        s_indep = independent_skew_at(R, t, n_tickers)
        mask_both = np.isfinite(s_orig) & np.isfinite(s_indep)
        diff = float(np.max(np.abs(s_orig[mask_both] - s_indep[mask_both]))) if mask_both.any() else 0.0
        all_ok &= (diff < 1e-6)
        lines.append(f"| {t} | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — skewness confirmée par recalcul indépendant (formule G1) sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(331)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    R_mut_df = np.log(P_mut / P_mut.shift(1))
    R_mut_df.iloc[0, :] = 0.0
    skew60_mut = R_mut_df.rolling(SKEW_WINDOW).skew().values

    check_i = cut - SKEW_WINDOW - 50
    s_before = skew60_orig[check_i]
    s_after = skew60_mut[check_i]
    s_before_clean = np.nan_to_num(s_before, nan=0.0)
    s_after_clean = np.nan_to_num(s_after, nan=0.0)
    max_diff_lookahead = float(np.max(np.abs(s_before_clean - s_after_clean)))
    lines.append(f"Écart sur la skewness calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    n_listed = np.isfinite(P.values).sum(axis=1)
    lines.append("## 3. Taille de l'univers éligible au fil du temps")
    lines.append("")
    lines.append(f"Min {n_listed.min()}, max {n_listed.max()}, médiane {int(np.median(n_listed))} "
                 f"titres cotés simultanément sur les {T} séances.")

    out = ROOT / "results" / "nonml_skewness_tilt_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
