"""Simulation — 300 EUR, intersection Halloween x année pré-électorale
(cycle #182) sur les ~3 derniers mois disponibles (NDX). Aucun paramètre
retouché.

Note : 2026 N'EST PAS une année pré-électorale ((2026+1)%4 != 0, 2026 est
une année de mid-term) -- la fenêtre de simulation sera donc entièrement
en régime 1.0x (aucun jour actif), signalé honnêtement.
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
from nonml_presidential_cycle_overlay_backtest import preelection_mask  # noqa: E402
from nonml_halloween_preelection_and_overlay_backtest import CAP, COST_BPS  # noqa: E402

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
    pre_mask = preelection_mask(df["date"])[1:]
    mask = is_winter & pre_mask
    pos_full = np.where(mask, CAP, 1.0)

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]
    frac_active = float((pos > 1.0).mean())

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    eq_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    eq_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    lines = [
        f"# Simulation — 300 EUR, intersection Halloween x année pré-électorale (cycle #182), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"**2026 N'EST PAS une année pré-électorale** — % de jours actifs sur cette "
        f"fenêtre : {100*frac_active:.0f}% (fenêtre non informative si 0%, signalé "
        "honnêtement plutôt que masqué).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Intersection Halloween x pré-électorale** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (5/5 marchés) "
        "et de la grille de robustesse (15/15).",
    ]

    out = ROOT / "results" / "nonml_halloween_preelection_and_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
