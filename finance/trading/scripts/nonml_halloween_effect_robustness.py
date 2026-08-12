"""Robustesse — Effet Halloween. Grille CAP (PAS un retuning) autour de
CAP=2.0x pré-enregistré.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}
CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def run_one(df, cap):
    close = df["close"].values
    dates = pd.to_datetime(df["date"])
    r = np.log(close[1:] / close[:-1])
    month = dates.dt.month.values[1:]
    is_winter = (month >= 11) | (month <= 4)
    pos = np.where(is_winter, cap, 1.0)
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
        "# Robustesse — Effet Halloween (grille CAP, PAS un retuning)",
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

    out = ROOT / "results" / "nonml_halloween_effect_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
