"""Robustesse — Overlay filtre de pente SMA200. Grille CAP ET grille de
SLOPE_LAG (PAS un retuning de la fenêtre SMA200 elle-même, identique au
#29), autour des valeurs pré-enregistrées (CAP=2.0x, SLOPE_LAG=20j).
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
from nonml_sma200_slope_overlay_backtest import COST_BPS, SMA_WINDOW, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
SLOPE_LAG_GRID = [15, 20, 25, 30]


def slope_mask_for(close: np.ndarray, slope_lag: int) -> np.ndarray:
    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    sma_lagged = np.roll(sma, slope_lag)
    sma_lagged[:slope_lag] = np.nan
    with np.errstate(invalid="ignore"):
        slope_up = sma > sma_lagged
    return np.nan_to_num(slope_up, nan=0.0).astype(bool)


def run_one(close: np.ndarray, cap: float, slope_lag: int) -> bool:
    slope_up = slope_mask_for(close, slope_lag)
    start = SMA_WINDOW + slope_lag
    close_t = close[start:]
    bh_full = np.log(close_t[1:] / close_t[:-1])
    mask = slope_up[start:-1]
    pos = np.where(mask, cap, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    closes = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            closes[name] = df["close"].values

    lines = [
        "# Robustesse — Overlay filtre de pente SMA200 (grilles CAP et SLOPE_LAG, PAS un retuning de la fenêtre SMA200)",
        "",
        "CAP pré-enregistré = 2.0x, SLOPE_LAG pré-enregistré = 20j.",
        "",
        "## Grille CAP (SLOPE_LAG fixé à 20j)",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(close, cap, 20) for close in closes.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(closes)}{marker} |")

    lines.append("")
    lines.append("## Grille SLOPE_LAG (CAP fixé à 2.0x)")
    lines.append("")
    lines.append("| SLOPE_LAG | Nb marchés PASS /5 |")
    lines.append("|---|---|")
    for slope_lag in SLOPE_LAG_GRID:
        n_pass = sum(run_one(close, 2.0, slope_lag) for close in closes.values())
        marker = " ← SLOPE_LAG pré-enregistré" if slope_lag == 20 else ""
        lines.append(f"| {slope_lag}j | {n_pass}/{len(closes)}{marker} |")

    out = ROOT / "results" / "nonml_sma200_slope_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
