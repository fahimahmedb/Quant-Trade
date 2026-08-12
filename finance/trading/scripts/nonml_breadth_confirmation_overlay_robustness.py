"""Robustesse — Overlay de confirmation multi-marché NDX+Russell2000.
Grille CAP (PAS un retuning du seuil de tendance ni du choix des deux
marchés), autour du CAP pré-enregistré (2.0x).
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
from nonml_breadth_confirmation_overlay_backtest import near_high_series, COST_BPS, INDEX_LOOKBACK  # noqa: E402

CAP_GRID = [1.5, 2.0, 2.5, 3.0]


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "russell2000_daily.txt"))
    quality_report(df_confirm)

    signal_a = near_high_series(df_primary)
    signal_b = near_high_series(df_confirm)
    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned = signal_a.values.astype(bool)
    both = a_aligned & b_aligned

    close = df_primary["close"].values
    bh_full = np.log(close[1:] / close[:-1])
    start = INDEX_LOOKBACK
    bh_t = bh_full[start:]
    mask = both[start:-1]

    lines = [
        "# Robustesse — Overlay confirmation multi-marché NDX+Russell2000 (grille CAP, PAS un retuning)",
        "",
        "CAP pré-enregistré = 2.0x.",
        "",
        "| CAP | Sharpe>BH | Rdt>BH | Sharpe | Rendement total | MDD |",
        "|---|---|---|---|---|---|",
    ]
    for cap in CAP_GRID:
        pos = np.where(mask, cap, 1.0)
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4
        me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0
        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        marker = " ← CAP pré-enregistré" if cap == 2.0 else ""
        lines.append(f"| {cap}x | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                     f"{me_ov['sharpe_ann']:+.3f} | {100*ret_ov:+.1f}% | {me_ov['max_drawdown_pct']:.1f}%{marker} |")

    out = ROOT / "results" / "nonml_breadth_confirmation_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
