"""Simulation — 300 EUR, overlay corrélation cross-marché NDX-DAX
(cycle #193) sur les ~3 derniers mois disponibles (NDX). Aucun paramètre
retouché.
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
from nonml_cross_market_correlation_ndx_dax_overlay_backtest import (  # noqa: E402
    COST_BPS, build_corr_series, load_corr_lag, expanding_tercile_cut_high,
)

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
    dates = pd.DatetimeIndex(df["date"].values)
    bh_full = np.log(close[1:] / close[:-1])

    corr_series = build_corr_series()
    corr_lag_full = load_corr_lag(dates, corr_series)[1:]
    pos_full = expanding_tercile_cut_high(corr_lag_full)
    dates_r = dates[1:]

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]
    assert np.isfinite(pos).all(), "fenêtre récente doit être entièrement dans la zone de données valides"

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    # Equite composee en LOG : les series pnl_* sont des rendements log,

    # donc equity = CAPITAL0 * exp(cumsum(pnl)), pas cumprod(1+pnl).

    # Voir results/nonml_log_return_compounding_audit.md.

    eq_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    eq_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    frac_cut = float((pos < 1.0).mean())

    lines = [
        f"# Simulation — 300 EUR, overlay corrélation cross-marché NDX-DAX (cycle #193), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"{100*frac_cut:.0f}% de la fenêtre est en régime coupé (corrélation NDX-DAX élevée).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay corrélation NDX-DAX** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/5 marchés) "
        "et de la grille de robustesse (27/45).",
    ]

    out = ROOT / "results" / "nonml_cross_market_correlation_ndx_dax_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
