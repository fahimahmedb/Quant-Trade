"""Simulation — 300 EUR dans l'overlay union SMA200∪(ToM∪Halloween) (NDX),
~3 derniers mois. Spécification pré-enregistrée (CAP=2.0x), aucun
paramètre retouché après les résultats précédents.
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
from nonml_sma200_tom_halloween_union_overlay_backtest import (  # noqa: E402
    above_sma_mask, tom_mask, halloween_mask, COST_BPS, CAP, SMA_WINDOW,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    dates_full = df["date"]

    above_full = above_sma_mask(close_full)
    tom_full = tom_mask(dates_full)
    hall_full = halloween_mask(dates_full)

    close = close_full[-(WINDOW_DAYS + 1):]
    above = above_full[-(WINDOW_DAYS + 1):]
    tom = tom_full[-(WINDOW_DAYS + 1):]
    hall = hall_full[-(WINDOW_DAYS + 1):]
    dates = df["date"].values[-(WINDOW_DAYS + 1):]

    bh_full = np.log(close[1:] / close[:-1])
    union = above[:-1] | tom[:-1] | hall[:-1]
    pos = np.where(union, CAP, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    equity_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, overlay union SMA200∪(ToM∪Halloween) (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). CAP={CAP}x si tendance haussière OU ToM OU Halloween, 1.0x sinon.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay union SMA200∪ToM∪Halloween** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"**Lecture honnête** : sur cette fenêtre de {WINDOW_DAYS} séances, la position est "
        f"levée {100*union.mean():.1f}% du temps (union très large des 3 signaux) — illustration "
        "seulement, le verdict statistique reste celui du backtest complet (PASS 5/5 marchés) et "
        "de la robustesse (5/5 au CAP pré-enregistré 2.0x et à 1.5x, mais dégradé à 4/5 puis 3/5 "
        "aux CAP plus élevés 2.5x/3.0x — contrairement au plateau parfait du #29 seul, l'exposition "
        "quasi-permanente de cette union amplifie le risque de volatility drag à fort levier)."
    ]

    out = ROOT / "results" / "nonml_sma200_tom_halloween_union_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
