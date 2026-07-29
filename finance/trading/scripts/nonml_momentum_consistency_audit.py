"""Audit adversarial — Momentum de constance.

1. Recalcul indépendant de la constance à un échantillon de dates de
   rebalancement (boucle Python explicite par titre, sans numpy
   vectorisé) pour vérifier l'absence de bug d'indexation des blocs.
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

from nonml_momentum_consistency_backtest import (  # noqa: E402
    load_all_prices, consistency_at, BLOCK_LEN, N_BLOCKS, LOOKBACK, REBAL_EVERY,
)


def independent_consistency_at(close: np.ndarray, t: int, n_tickers: int) -> np.ndarray:
    cons = np.full(n_tickers, np.nan)
    for j in range(n_tickers):
        n_pos, n_valid = 0, 0
        for b in range(N_BLOCKS):
            end_idx = t - b * BLOCK_LEN
            start_idx = end_idx - BLOCK_LEN
            c_end, c_start = close[end_idx, j], close[start_idx, j]
            if np.isfinite(c_end) and np.isfinite(c_start):
                n_valid += 1
                if c_end > c_start:
                    n_pos += 1
        if n_valid == N_BLOCKS:
            cons[j] = n_pos / N_BLOCKS
    return cons


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

    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    check_dates = rebal_dates[::10]

    lines = ["# Audit adversarial — Momentum de constance", "",
             "## 1. Recalcul indépendant à un échantillon de dates de rebalancement", "",
             "| Date (indice) | Écart max absolu (titres avec historique complet) |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        cons_orig = consistency_at(close, t)
        cons_indep = independent_consistency_at(close, t, n_tickers)
        mask_both = np.isfinite(cons_orig) & np.isfinite(cons_indep)
        diff = float(np.max(np.abs(cons_orig[mask_both] - cons_indep[mask_both]))) if mask_both.any() else 0.0
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — constance confirmée par recalcul indépendant sur toutes les dates échantillonnées.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(307)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - LOOKBACK - 50
    cons_before = consistency_at(close, check_i)
    cons_after = consistency_at(close_mut, check_i)
    cons_before_clean = np.nan_to_num(cons_before, nan=-1.0)
    cons_after_clean = np.nan_to_num(cons_after, nan=-1.0)
    max_diff_lookahead = float(np.max(np.abs(cons_before_clean - cons_after_clean)))
    lines.append(f"Écart sur la constance calculée à une date antérieure à la mutation : {max_diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if max_diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    n_listed = np.isfinite(close).sum(axis=1)
    lines.append("## 3. Taille de l'univers éligible au fil du temps")
    lines.append("")
    lines.append(f"Min {n_listed.min()}, max {n_listed.max()}, médiane {int(np.median(n_listed))} "
                 f"titres cotés simultanément sur les {T} séances.")

    out = ROOT / "results" / "nonml_momentum_consistency_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
