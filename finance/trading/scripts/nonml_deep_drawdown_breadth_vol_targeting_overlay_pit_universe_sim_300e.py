"""Simulation 300 EUR — breadth de drawdown profond, univers POINT-IN-TIME.

Illustration sur les ~3 derniers mois de données disponibles (63 séances).
**Aucune valeur statistique** : le verdict du cycle reste celui du backtest
complet (2645 séances) et de la grille de robustesse. Une fenêtre de 63 séances
ne permet de conclure sur rien — elle sert uniquement à donner un ordre de
grandeur concret.

Composition en LOG (`exp(cumsum)`), convention corrigée du dépôt.

Usage : python3 scripts/nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_sim_300e.py
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
import nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
OUT = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pit_universe_sim_300e.md"


def mdd_pct(equity):
    return float((equity / np.maximum.accumulate(equity) - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    r_full = np.log(close[1:] / close[:-1])
    dates_r = dates_idx.values[1:]

    breadth_dd, _, _ = bt.compute_deep_drawdown_breadth_series_pit()
    median_dd = breadth_dd.rolling(bt.MEDIAN_WINDOW).median()
    signal_defined = breadth_dd.notna() & median_dd.notna()
    gate_series = (breadth_dd >= median_dd).where(signal_defined)
    gate_aligned = gate_series.fillna(False).reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)
    pos_full = bt.combined_position(r_full, gate_aligned)

    r = r_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (bt.COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= bt.COST_BPS / 1e4

    # Series en rendements LOG : equite = CAPITAL0 * exp(cumsum).
    eq_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    eq_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    L = [
        "# Simulation 300 EUR — breadth de drawdown profond, univers POINT-IN-TIME",
        "",
        f"Période : {pd.Timestamp(dates_w[0]).date()} → {pd.Timestamp(dates_w[-1]).date()} "
        f"({WINDOW_DAYS} séances). Coûts {bt.COST_BPS:.0f} bps.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold (NDX) | {eq_bh[-1]:.2f} EUR | {100*(eq_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay gaté breadth DD (PIT)** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100*(eq_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"Exposition moyenne sur la fenêtre : {pos.mean():.2f}x "
        f"(porte active {100*(pos > 1.0).mean():.1f}% du temps).",
        "",
        "**Lecture honnête** : 63 séances n'ont **aucune valeur statistique**. Le verdict "
        "du cycle reste celui du backtest complet (2645 séances, 2016-2026, PASS) et de la "
        "grille de robustesse (8/8). Cette simulation illustre un ordre de grandeur, rien "
        "de plus — et une fenêtre courte peut aussi bien flatter que pénaliser la stratégie.",
        "",
    ]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
