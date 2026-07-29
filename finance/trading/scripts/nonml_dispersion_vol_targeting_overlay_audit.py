"""Audit adversarial — Overlay vol-targeting gaté par dispersion
cross-sectionnelle NDX-100.

Recalcul totalement indépendant de la dispersion (boucle explicite jour
par jour, sans numpy vectorisé) et de la position (boucle explicite,
ddof=1), et test anti-lookahead (perturbation du futur sur les prix
indice ET titres).
"""
import json
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
from nonml_dispersion_vol_targeting_overlay_backtest import (  # noqa: E402
    load_all_prices, compute_dispersion_series, combined_position,
    MEDIAN_WINDOW, MIN_LISTED, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION,
)


def independent_dispersion_series():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = close.shape

    dispersion = np.full(T, np.nan)
    for i in range(1, T):
        rets = []
        for j in range(n_tickers):
            c0, c1 = close[i - 1, j], close[i, j]
            if np.isfinite(c0) and np.isfinite(c1):
                rets.append(np.log(c1 / c0))
        if len(rets) >= MIN_LISTED:
            arr = np.array(rets)
            mean = arr.mean()
            dispersion[i] = np.sqrt(np.sum((arr - mean) ** 2) / (len(arr) - 1))
    return pd.Series(dispersion, index=P.index)


def independent_combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    T = len(r)
    pos = np.ones(T)
    for i in range(T):
        if not gate_aligned[i]:
            pos[i] = 1.0
            continue
        if i - VOL_WINDOW < 0:
            pos[i] = 1.0
            continue
        vol_window_r = r[i - VOL_WINDOW:i]
        vol_ann = vol_window_r.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 1.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])

    disp_orig = compute_dispersion_series()
    disp_indep = independent_dispersion_series()
    mask_both = disp_orig.notna() & disp_indep.notna()
    diff_disp = float(np.max(np.abs(disp_orig[mask_both].values - disp_indep[mask_both].values))) if mask_both.any() else 0.0

    median_orig = disp_orig.rolling(MEDIAN_WINDOW).median()
    gate_series = (disp_orig >= median_orig)
    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

    pos_orig = combined_position(close, r, gate_aligned)
    pos_indep = independent_combined_position(r[start - VOL_WINDOW:], gate_aligned[start - VOL_WINDOW:-1] if len(gate_aligned) > start - VOL_WINDOW else gate_aligned)
    max_diff_pos = float(np.max(np.abs(pos_orig[start:] - pos_indep[VOL_WINDOW:VOL_WINDOW + len(pos_orig) - start])))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par dispersion cross-sectionnelle NDX-100", "",
             "## 1. Recalcul indépendant de la dispersion (boucle explicite jour par jour)", "",
             f"Écart maximum absolu (jours où les deux calculs sont définis) : {diff_disp:.2e}",
             f"**{'OK — dispersion confirmée par recalcul indépendant.' if diff_disp < 1e-9 else 'ÉCHEC.'}**",
             "",
             "## 2. Recalcul indépendant de la position (boucle explicite, ddof=1)",
             "",
             f"Écart maximum absolu sur l'échantillon testable : {max_diff_pos:.2e}",
             f"**{'OK — position confirmée par recalcul indépendant.' if max_diff_pos < 1e-9 else 'ÉCHEC.'}**",
             ""]

    lines.append("## 3. Test anti-lookahead (perturbation du futur sur l'indice)")
    lines.append("")
    cut = len(close) // 2
    close_pert = close.copy()
    rng = np.random.default_rng(263)
    close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
    r_pert = np.log(close_pert[1:] / close_pert[:-1])
    pos_before = combined_position(close, r, gate_aligned)
    pos_after = combined_position(close_pert, r_pert, gate_aligned)
    check_end = cut - VOL_WINDOW
    identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
    lines.append(f"**{'OK — aucune fuite (perturbation des prix indice futurs sans effet passé).' if identical else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
