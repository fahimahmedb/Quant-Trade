"""Audit adversarial — Double porte AND breadth SMA200 + breadth de
momentum.

1. Recalcul indépendant de la porte combinée (AND) à un échantillon de
   dates, via recalcul indépendant direct des deux breadth (formules
   explicites, sans réutiliser les fonctions vectorisées du backtest).
2. Test anti-lookahead (perturbation du futur).
3. Vérifie la logique AND elle-même (porte combinée ⊆ chaque porte
   individuelle).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_momentum_breadth_vol_targeting_overlay_backtest import load_all_prices, LOOKBACK, SKIP  # noqa: E402
from nonml_sma200_breadth_vol_targeting_overlay_backtest import SMA_WINDOW  # noqa: E402
from nonml_sma200_momentum_breadth_and_overlay_backtest import (  # noqa: E402
    compute_sma200_breadth_series, compute_momentum_breadth_series,
    SMA_BREADTH_THRESHOLD, MOM_BREADTH_THRESHOLD,
)


def independent_sma_breadth_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    n_calc, n_above = 0, 0
    for j in range(n_tickers):
        c = close[t, j]
        if not np.isfinite(c):
            continue
        window = close[t - SMA_WINDOW + 1:t + 1, j]
        if not np.isfinite(window).all():
            continue
        n_calc += 1
        if c > window.mean():
            n_above += 1
    return n_above / n_calc if n_calc > 0 else np.nan


def independent_mom_breadth_at(close: np.ndarray, t: int, n_tickers: int) -> float:
    n_calc, n_pos = 0, 0
    for j in range(n_tickers):
        if t < LOOKBACK:
            continue
        c_skip = close[t - SKIP, j]
        c_lb = close[t - LOOKBACK, j]
        if not (np.isfinite(c_skip) and np.isfinite(c_lb)):
            continue
        n_calc += 1
        if c_skip / c_lb - 1.0 > 0:
            n_pos += 1
    return n_pos / n_calc if n_calc > 0 else np.nan


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

    sma_orig = compute_sma200_breadth_series()
    mom_orig = compute_momentum_breadth_series()

    check_dates = list(range(max(SMA_WINDOW, LOOKBACK), T, 150))
    lines = ["# Audit adversarial — Double porte AND breadth SMA200 + breadth de momentum", "",
             "## 1. Recalcul indépendant des deux breadth (boucle Python explicite)", "",
             "| Date (indice) | Écart SMA200 | Écart momentum | Porte AND concorde |",
             "|---|---|---|---|"]
    all_ok = True
    for t in check_dates:
        indep_sma = independent_sma_breadth_at(close, t, n_tickers)
        indep_mom = independent_mom_breadth_at(close, t, n_tickers)
        orig_sma = sma_orig.values[t]
        orig_mom = mom_orig.values[t]
        diff_sma = abs(orig_sma - indep_sma) if not (np.isnan(orig_sma) or np.isnan(indep_sma)) else 0.0
        diff_mom = abs(orig_mom - indep_mom) if not (np.isnan(orig_mom) or np.isnan(indep_mom)) else 0.0
        gate_orig = (orig_sma >= SMA_BREADTH_THRESHOLD) and (orig_mom >= MOM_BREADTH_THRESHOLD)
        gate_indep = (indep_sma >= SMA_BREADTH_THRESHOLD) and (indep_mom >= MOM_BREADTH_THRESHOLD)
        concord = gate_orig == gate_indep
        all_ok &= (diff_sma < 1e-9) and (diff_mom < 1e-9) and concord
        lines.append(f"| {t} | {diff_sma:.2e} | {diff_mom:.2e} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK — les deux breadth et la porte AND sont confirmées par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = P.copy()
    rng = np.random.default_rng(98)
    P_mut.iloc[cut:] = P_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_mut.iloc[cut:].shape))
    close_mut = P_mut.values

    check_i = cut - max(SMA_WINDOW, LOOKBACK) - 50
    sma_before = independent_sma_breadth_at(close, check_i, n_tickers)
    sma_after = independent_sma_breadth_at(close_mut, check_i, n_tickers)
    mom_before = independent_mom_breadth_at(close, check_i, n_tickers)
    mom_after = independent_mom_breadth_at(close_mut, check_i, n_tickers)
    diff_lookahead = abs(sma_before - sma_after) + abs(mom_before - mom_after)
    lines.append(f"Écart sur les breadth calculées à une date antérieure à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead < 1e-9 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Vérification de la logique AND (porte combinée ⊆ chaque porte individuelle)")
    lines.append("")
    sma_gate_full = (sma_orig.values >= SMA_BREADTH_THRESHOLD)
    mom_gate_full = (mom_orig.values >= MOM_BREADTH_THRESHOLD)
    and_gate_full = sma_gate_full & mom_gate_full
    subset_sma_ok = bool(np.all(~and_gate_full | sma_gate_full))
    subset_mom_ok = bool(np.all(~and_gate_full | mom_gate_full))
    lines.append(f"Porte AND ⊆ porte SMA200 : {'OK' if subset_sma_ok else 'ÉCHEC'}. "
                 f"Porte AND ⊆ porte momentum : {'OK' if subset_mom_ok else 'ÉCHEC'}.")

    out = ROOT / "results" / "nonml_sma200_momentum_breadth_and_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
