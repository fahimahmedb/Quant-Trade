"""Simulation — 300 EUR, intersection Halloween x mid-term multiplicative
(cycle #184) sur les ~3 derniers mois disponibles (NDX). Aucun paramètre
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
from nonml_midterm_election_overlay_backtest import CUT, midterm_mask  # noqa: E402
from nonml_halloween_midterm_multiplicative_overlay_backtest import CAP, COST_BPS  # noqa: E402

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
    dates_r = dates[1:]

    month = dates.month.values[1:]
    is_winter = (month >= 11) | (month <= 4)
    mid_mask = midterm_mask(df["date"])[1:]
    halloween_only = is_winter & ~mid_mask
    midterm_only = mid_mask & ~is_winter
    overlap = is_winter & mid_mask

    pos_full = np.ones_like(bh_full)
    pos_full[halloween_only] = CAP
    pos_full[midterm_only] = CUT
    pos_full[overlap] = CAP * CUT

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]

    n_hall = int(halloween_only[-WINDOW_DAYS:].sum())
    n_mid = int(midterm_only[-WINDOW_DAYS:].sum())
    n_over = int(overlap[-WINDOW_DAYS:].sum())

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

    lines = [
        f"# Simulation — 300 EUR, intersection Halloween x mid-term multiplicative (cycle #184), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"Composition de la fenêtre : {n_hall} jours Halloween seul (2.0x), "
        f"{n_mid} jours mid-term seul (0.5x), {n_over} jours de chevauchement (1.0x).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Intersection Halloween x mid-term** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/4 marchés) "
        "et de la grille de robustesse (36/36).",
    ]

    out = ROOT / "results" / "nonml_halloween_midterm_multiplicative_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
