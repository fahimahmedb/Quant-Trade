"""Robustesse — Overlay union SMA200∪(ToM∪Halloween). Grille CAP (PAS un
retuning) autour de CAP=2.0x pré-enregistré.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_sma200_tom_halloween_union_overlay_backtest import (  # noqa: E402
    above_sma_mask, tom_mask, halloween_mask, COST_BPS, SMA_WINDOW, MARKETS,
)

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def run_one(df, cap):
    close = df["close"].values
    above = above_sma_mask(close)
    tom = tom_mask(df["date"])
    hall = halloween_mask(df["date"])
    start = SMA_WINDOW
    close_t = close[start:]
    r = np.log(close_t[1:] / close_t[:-1])
    union = above[start:-1] | tom[start:-1] | hall[start:-1]
    pos = np.where(union, cap, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0
    return (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)


def main():
    lines = [
        "# Robustesse — Overlay union SMA200∪(ToM∪Halloween) (grille CAP, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x.",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if path.exists():
            df = load_ohlc(str(path))
            quality_report(df)
            dfs[name] = df

    for cap in CAP_GRID:
        n_pass = sum(run_one(df, cap) for df in dfs.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(dfs)}{marker} |")

    out = ROOT / "results" / "nonml_sma200_tom_halloween_union_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
