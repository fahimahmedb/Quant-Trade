"""Robustesse — Porte breadth de momentum, univers point-in-time (cycle
#274). Grille CAP et grille de fenêtre de vol (PAS un retuning de la
porte BREADTH_THRESHOLD=50%/LOOKBACK=252/SKIP=21), grille réutilisée
telle quelle du #94 original.
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
from nonml_momentum_breadth_vol_targeting_overlay_pit_universe_backtest import (  # noqa: E402
    compute_momentum_breadth_series_pit, BREADTH_THRESHOLD, COST_BPS, TARGET_VOL_ANNUAL,
    ANNUALIZATION, LOOKBACK,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
WINDOW_GRID = [15, 20, 25, 30]


def position_for(r, gate_aligned, cap, vol_window):
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(vol_window).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt = TARGET_VOL_ANNUAL / vol_lagged
    vt = np.clip(vt, 1.0, cap)
    vt = np.nan_to_num(vt, nan=1.0)
    return np.where(gate_r, vt, 1.0)


def run_one(r, gate_aligned, start, cap, vol_window):
    pos_full = position_for(r, gate_aligned, cap, vol_window)
    r_t = r[start:]
    pos = pos_full[start:]
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r_t - turn * (COST_BPS / 1e4)
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])

    breadth = compute_momentum_breadth_series_pit()
    both_finite = np.isfinite(breadth.values)
    gate_values = np.where(both_finite, breadth.values >= BREADTH_THRESHOLD, np.nan)
    gate_series = pd.Series(gate_values, index=breadth.index)
    gate_series_filled = gate_series.fillna(False).astype(bool)
    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)

    lines = [
        "# Robustesse — Porte breadth de momentum, univers point-in-time (grilles CAP et fenêtre, PAS un retuning de la porte)",
        "",
        "Grille réutilisée telle quelle du #94 original. CAP pré-enregistré = 2.0x, "
        "fenêtre pré-enregistrée = 20j.",
        "",
        "## Grille CAP (fenêtre fixée à 20j)",
        "",
        "| CAP | PASS (Sharpe ET rendement > BH) |",
        "|---|---|",
    ]
    results = []
    for cap in CAP_GRID:
        start = max(first_valid, 20)
        ok = run_one(r, gate_aligned, start, cap, 20)
        results.append(ok)
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if ok else 'non'}{marker} |")

    lines.append("")
    lines.append("## Grille fenêtre de vol (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| Fenêtre | PASS (Sharpe ET rendement > BH) |")
    lines.append("|---|---|")
    for window in WINDOW_GRID:
        start = max(first_valid, window)
        ok = run_one(r, gate_aligned, start, 2.0, window)
        results.append(ok)
        marker = " ← fenêtre pré-enregistrée" if window == 20 else ""
        lines.append(f"| {window}j | {'OUI' if ok else 'non'}{marker} |")

    n_pass = sum(results)
    lines.append("")
    lines.append(f"**{n_pass}/{len(results)} variantes OUI.**")

    out = ROOT / "results" / "nonml_momentum_breadth_vol_targeting_overlay_pit_universe_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
