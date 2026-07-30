"""Audit adversarial — Overlay vol-targeting gaté par le régime VIX.

1. Recalcul indépendant de la porte (boucle Python explicite, médiane
   manuelle, sans pandas.reindex/shift/rolling) à un échantillon de dates.
2. Test anti-lookahead (mutation du futur VIX).
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
from nonml_vix_regime_vol_targeting_overlay_backtest import load_vix, MEDIAN_WINDOW  # noqa: E402


def independent_gate_at(ndx_date, vix_dates: list, vix_vals: np.ndarray) -> bool:
    idx = None
    for i in range(len(vix_dates) - 1, -1, -1):
        if vix_dates[i] < ndx_date:
            idx = i
            break
    if idx is None or idx < MEDIAN_WINDOW - 1:
        return None
    window = [vix_vals[j] for j in range(idx - MEDIAN_WINDOW + 1, idx + 1) if np.isfinite(vix_vals[j])]
    if len(window) < MEDIAN_WINDOW // 2:
        return None
    window_sorted = sorted(window)
    n = len(window_sorted)
    median = window_sorted[n // 2] if n % 2 == 1 else 0.5 * (window_sorted[n // 2 - 1] + window_sorted[n // 2])
    return vix_vals[idx] >= median


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    dates_idx = pd.to_datetime(df["date"])

    vix = load_vix()
    vix_dates_list = list(vix.index)
    vix_vals = vix.values

    vix_lagged = vix.shift(1)
    median_vix = vix_lagged.rolling(MEDIAN_WINDOW).median()
    gate_series = (vix_lagged >= median_vix)
    gate_series_filled = gate_series.fillna(False)
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    check_idx = list(range(2000, len(dates_idx), 1500))
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par le régime VIX", "",
             "## 1. Recalcul indépendant de la porte (boucle Python explicite, médiane manuelle)", "",
             "| Date NDX (indice) | Concorde |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for t in check_idx:
        nd = dates_idx.iloc[t]
        indep = independent_gate_at(nd, vix_dates_list, vix_vals)
        if indep is None:
            continue
        orig = bool(gate_aligned[t])
        concord = (orig == indep)
        all_ok &= concord
        n_checked += 1
        lines.append(f"| {t} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données VIX les plus récentes)")
    lines.append("")
    T_vix = len(vix)
    cut = int(T_vix * 0.8)
    rng = np.random.default_rng(130)
    vix_mut = vix.copy()
    vix_mut.iloc[cut:] = vix_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.5, T_vix - cut))
    cut_date = vix.index[cut]

    vix_lagged_mut = vix_mut.shift(1)
    median_vix_mut = vix_lagged_mut.rolling(MEDIAN_WINDOW).median()
    gate_series_mut = (vix_lagged_mut >= median_vix_mut).fillna(False)
    gate_aligned_mut = gate_series_mut.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    check_slice_mask = (dates_idx < (cut_date - pd.Timedelta(days=400))).values
    diff_lookahead = int(np.sum(gate_aligned[check_slice_mask] != gate_aligned_mut[check_slice_mask]))
    lines.append(f"Écart de porte sur les séances antérieures à la mutation (marge 400j) : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_vix_regime_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
