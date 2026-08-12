"""Robustesse — Overlay vol-targeting gaté par double porte
dispersion+tendance. Grille CAP ET grille de fenêtre de vol (PAS un
retuning des portes), autour des valeurs pré-enregistrées (CAP=2.0x,
fenêtre=20j).
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
from prediction import trading_metrics  # noqa: E402
from nonml_dispersion_trend_vol_targeting_overlay_backtest import (  # noqa: E402
    near_high_mask, INDEX_LOOKBACK, COST_BPS, TARGET_VOL_ANNUAL, ANNUALIZATION,
)
from nonml_dispersion_vol_targeting_overlay_backtest import compute_dispersion_series, MEDIAN_WINDOW  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def position_for(r: np.ndarray, gate_combined: np.ndarray, cap: float, vol_window: int) -> np.ndarray:
    gate_r = gate_combined[:-1]
    vol_ann = pd.Series(r).rolling(vol_window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.where(gate_r, vt, 1.0)


def run_one(r: np.ndarray, gate_combined: np.ndarray, start: int, cap: float, vol_window: int) -> bool:
    pos_full = position_for(r, gate_combined, cap, vol_window)
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


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

    valid_mask = disp_gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)

    lines = [
        "# Robustesse — Overlay vol-targeting gaté par double porte dispersion+tendance (grilles CAP et fenêtre, PAS un retuning des portes)",
        "",
        "CAP pré-enregistré = 2.0x, fenêtre pré-enregistrée = 20j.",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | PASS (Sharpe ET rendement > BH) |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        start = max(first_valid, INDEX_LOOKBACK, 20)
        ok = run_one(r, gate_combined, start, cap, 20)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if ok else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | PASS (Sharpe ET rendement > BH) |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        start = max(first_valid, INDEX_LOOKBACK, window)
        ok = run_one(r, gate_combined, start, 2.0, window)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {'OUI' if ok else 'non'}{marker} |")

    out = ROOT / "results" / "nonml_dispersion_trend_vol_targeting_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
