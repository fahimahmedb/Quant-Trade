"""Simulation — 300 EUR, overlay mid-term (cycle #176) sur les ~3 derniers
mois disponibles (NDX). Aucun paramètre retouché.

Note : 2026 EST une année de mid-term ((2026%4)==2) -- la fenêtre des 63
dernières séances est donc majoritairement/entièrement en régime coupé
(0.5x), signalé honnêtement plutôt que présenté comme un contraste.
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
from nonml_midterm_election_overlay_backtest import COST_BPS, CUT, midterm_mask  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
MARKET_FILE = "nasdaq100_daily.txt"
MARKET_NAME = "NDX (40 ans)"


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates = pd.to_datetime(df["date"].values)
    bh_full = np.log(close[1:] / close[:-1])
    mask = midterm_mask(df["date"])[1:]
    pos_full = np.where(mask, CUT, 1.0)
    dates_r = dates[1:]

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    eq_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    eq_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    frac_cut = float(pos.mean() < 1.0) if False else float((pos < 1.0).mean())

    lines = [
        f"# Simulation — 300 EUR, overlay mid-term (cycle #176), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"2026 EST une année de mid-term ((2026%4)==2) : {100*frac_cut:.0f}% de la fenêtre "
        f"est en régime coupé ({CUT}x) -- signalé honnêtement, ce n'est pas une fenêtre "
        f"contrastée entre les deux régimes.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay mid-term** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/4 marchés) "
        "et de la grille de robustesse (12/12).",
    ]

    out = ROOT / "results" / "nonml_midterm_election_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
