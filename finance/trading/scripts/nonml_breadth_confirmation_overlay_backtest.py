"""Backtest — Overlay de confirmation multi-marché (breadth), NDX
confirmé par Russell 2000 (spécification pré-enregistrée dans
PREREG_breadth_confirmation_overlay.md, committée avant ce script).
Premier signal du backlog basé sur une confirmation croisée entre deux
marchés. n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
CAP = 2.0
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95


def near_high_series(df) -> pd.Series:
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(near_high, index=dates)


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "russell2000_daily.txt"))
    quality_report(df_confirm)

    signal_a = near_high_series(df_primary)  # NDX
    signal_b = near_high_series(df_confirm)  # Russell 2000

    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned = signal_a.values.astype(bool)

    both = a_aligned & b_aligned

    close = df_primary["close"].values
    bh_full = np.log(close[1:] / close[:-1])

    start = INDEX_LOOKBACK
    bh_t = bh_full[start:]
    mask = both[start:-1]

    pos = np.where(mask, CAP, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Overlay de confirmation multi-marché NDX+Russell2000 (pré-enregistré, règle renforcée)",
        "",
        f"Position sur NDX = 1.0x en permanence, CAP={CAP}x quand NDX ET Russell 2000 sont "
        f"SIMULTANÉMENT ≥{100*INDEX_THRESHOLD:.0f}% de leur plus haut {INDEX_LOOKBACK}j. "
        f"{len(bh_t)} séances testables ({dates_primary.iloc[start].date()} → {dates_primary.iloc[-1].date()}).",
        "",
        f"%j confirmé NDX seul (signal A) : {100*a_aligned[start:-1].mean():.1f}%",
        f"%j confirmé Russell 2000 seul (signal B, aligné ffill) : {100*b_aligned[start:-1].mean():.1f}%",
        f"%j confirmation croisée (A∩B, overlay actif) : {100*mask.mean():.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay confirmation multi-marché x{CAP}** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_breadth_confirmation_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
