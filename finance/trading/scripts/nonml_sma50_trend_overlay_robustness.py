"""Robustesse — Overlay filtre de tendance SMA50. Grille CAP uniquement
(PAS un retuning de la fenêtre SMA50), autour de la valeur
pré-enregistrée (CAP=2.0x).
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
from nonml_sma50_trend_overlay_backtest import above_sma_mask, COST_BPS, SMA_WINDOW, MARKETS  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def run_one(close: np.ndarray, cap: float) -> bool:
    above = above_sma_mask(close)
    start = SMA_WINDOW
    close_t = close[start:]
    bh_full = np.log(close_t[1:] / close_t[:-1])
    mask = above[start:-1]
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
        "# Robustesse — Overlay filtre de tendance SMA50 (grille CAP, PAS un retuning de la fenêtre)",
        "",
        "CAP pré-enregistré = 2.0x.",
        "",
        "| CAP | Nb marchés PASS /5 |",
        "|---|---|",
    ]
    for cap in CAP_GRID:
        n_pass = sum(run_one(close, cap) for close in closes.values())
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {n_pass}/{len(closes)}{marker} |")

    out = ROOT / "results" / "nonml_sma50_trend_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
