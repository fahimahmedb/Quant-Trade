"""Simulation — 300 EUR, position graduée par nombre de votes (défaut
carte + NFCI + BAA10Y, cycle #301) sur les ~3 derniers mois
disponibles (NDX). Aucun paramètre retouché. Gabarit repris tel quel
du #289/#286/#296/#299 (Règle 7).
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
from nonml_delinquency_nfci_combined_overlay_backtest import (  # noqa: E402
    COST_BPS, build_delinquency_series, build_nfci_series,
    expanding_tercile_gate_high,
)
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    load_delinquency_lag,
)
from nonml_financial_conditions_overlay_backtest import (  # noqa: E402
    load_nfci_lag,
)
from nonml_credit_spread_overlay_backtest import load_baa10y_lag  # noqa: E402
from nonml_delinquency_nfci_baa10y_graduated_overlay_backtest import (  # noqa: E402
    position_from_votes,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63
MARKET_FILE = "nasdaq100_daily.txt"
MARKET_NAME = "NDX (40 ans)"


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    delinq_series = build_delinquency_series()
    nfci_series = build_nfci_series()

    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    bh_full = np.log(close[1:] / close[:-1])

    delinq_lag_full = load_delinquency_lag(dates, delinq_series)[1:]
    nfci_lag_full = load_nfci_lag(dates, nfci_series)[1:]
    baa10y_lag_full = load_baa10y_lag(dates)[1:]
    votes_full = (expanding_tercile_gate_high(delinq_lag_full).astype(int)
                  + expanding_tercile_gate_high(nfci_lag_full).astype(int)
                  + expanding_tercile_gate_high(baa10y_lag_full).astype(int))
    pos_full = position_from_votes(votes_full)
    dates_r = dates[1:]

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    votes_w = votes_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]
    assert (np.isfinite(delinq_lag_full[-WINDOW_DAYS:]).all()
            and np.isfinite(nfci_lag_full[-WINDOW_DAYS:]).all()
            and np.isfinite(baa10y_lag_full[-WINDOW_DAYS:]).all()), \
        "fenêtre récente doit être entièrement dans la zone de données valides"

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    eq_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    eq_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    votes_dist = [float((votes_w == k).mean()) for k in range(4)]

    lines = [
        f"# Simulation — 300 EUR, position graduée défaut carte+NFCI+BAA10Y (cycle #301), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"Répartition des votes sur la fenêtre : 0 vote {100*votes_dist[0]:.0f}%, "
        f"1 vote {100*votes_dist[1]:.0f}%, 2 votes {100*votes_dist[2]:.0f}%, "
        f"3 votes {100*votes_dist[3]:.0f}%.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay position graduée** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/5 marchés) "
        "et de la grille de robustesse (12/15, plateau cohérent).",
    ]

    out = ROOT / "results" / "nonml_delinquency_nfci_baa10y_graduated_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
