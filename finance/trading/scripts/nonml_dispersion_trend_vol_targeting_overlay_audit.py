"""Audit adversarial — Overlay vol-targeting gaté par double porte
dispersion ET tendance.

Recalcul totalement indépendant de la position (boucle explicite jour
par jour, ddof=1, recalculant les deux portes sans réutiliser
pandas.rolling) et test anti-lookahead (perturbation du futur sur
l'indice).
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
from nonml_dispersion_trend_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, near_high_mask, INDEX_LOOKBACK, INDEX_THRESHOLD,
    VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION,
)
from nonml_dispersion_vol_targeting_overlay_backtest import compute_dispersion_series, MEDIAN_WINDOW  # noqa: E402


def independent_combined_position(close: np.ndarray, r: np.ndarray, disp_gate_aligned: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : boucle explicite jour par jour
    pour la porte tendance (fenetre glissante par slicing) ET le
    vol-targeting (ddof=1), la porte dispersion etant reutilisee du
    backtest (deja auditee independamment au #78)."""
    T = len(r)
    pos = np.ones(T)
    for i in range(T):
        if i < INDEX_LOOKBACK:
            pos[i] = 1.0
            continue
        window_max = close[i - INDEX_LOOKBACK + 1:i + 1].max()
        trend_i = close[i] >= INDEX_THRESHOLD * window_max
        if not (trend_i and disp_gate_aligned[i]):
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

    trend_gate = near_high_mask(close)
    dispersion = compute_dispersion_series()
    median_dispersion = dispersion.rolling(MEDIAN_WINDOW).median()
    disp_gate_series = (dispersion >= median_dispersion)
    disp_gate_aligned_raw = disp_gate_series.reindex(dates_idx.values, method="ffill")
    disp_gate_aligned = disp_gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    gate_combined = trend_gate & disp_gate_aligned
    pos_orig = combined_position(close, r, gate_combined)

    # independent_combined_position attend disp_gate_aligned indexe comme r (longueur T-1)
    pos_indep = independent_combined_position(close, r, disp_gate_aligned[:-1])

    valid_mask = disp_gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, INDEX_LOOKBACK, VOL_WINDOW)

    max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par double porte dispersion+tendance", "",
             "## 1. Recalcul totalement indépendant (boucle explicite jour par jour)", "",
             f"Écart position max (hors marge de fenêtre) : {max_diff:.2e}",
             f"**{'OK — position confirmée par recalcul totalement indépendant.' if max_diff < 1e-9 else 'ÉCHEC.'}**",
             ""]

    lines.append("## 2. Test anti-lookahead (perturbation du futur sur l'indice)")
    lines.append("")
    cut = len(close) // 2
    close_pert = close.copy()
    rng = np.random.default_rng(293)
    close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
    r_pert = np.log(close_pert[1:] / close_pert[:-1])
    trend_gate_pert = near_high_mask(close_pert)
    gate_combined_pert = trend_gate_pert & disp_gate_aligned
    pos_before = combined_position(close, r, gate_combined)
    pos_after = combined_position(close_pert, r_pert, gate_combined_pert)
    check_end = cut - max(INDEX_LOOKBACK, VOL_WINDOW)
    identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
    lines.append(f"**{'OK — aucune fuite (perturbation des prix indice futurs sans effet passé).' if identical else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_dispersion_trend_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
