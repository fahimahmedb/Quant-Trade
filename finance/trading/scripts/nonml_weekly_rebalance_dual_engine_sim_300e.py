"""Simulation — 300 EUR dans le rebalancement hebdomadaire du #121
(NDX), ~3 derniers mois. Spécification pré-enregistrée (REBAL_FREQ=5j),
aucun paramètre retouché après les résultats précédents.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_weekly_rebalance_dual_engine_backtest import COST_BPS, weekly_hold_position  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos_daily_full, r_full, dates_full = d["pos"], d["r_asset"], pd.to_datetime(d["dates"])

    r = r_full[-WINDOW_DAYS:]
    pos_full = weekly_hold_position(pos_daily_full, 5)
    pos = pos_full[-WINDOW_DAYS:]
    dates = dates_full[-WINDOW_DAYS:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    equity_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
    ret_ov_pct = 100 * (equity_ov[-1] / CAPITAL0 - 1)
    ret_bh_pct = 100 * (equity_bh[-1] / CAPITAL0 - 1)
    calmar_ov = (ret_ov_pct / 100) / abs(mdd(equity_ov) / 100) if mdd(equity_ov) != 0 else float("nan")
    calmar_bh = (ret_bh_pct / 100) / abs(mdd(equity_bh) / 100) if mdd(equity_bh) != 0 else float("nan")

    lines = [
        "# Simulation — 300 EUR, rebalancement hebdomadaire du #121 (NDX, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r)} séances). REBAL_FREQ=5j, "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |",
        "|---|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {ret_bh_pct:+.1f}% | {mdd(equity_bh):.1f}% | "
        f"{me_bh['sharpe_ann']:+.2f} | {calmar_bh:.3f} |",
        f"| **Rebalancement hebdomadaire** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{ret_ov_pct:+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} | "
        f"**{calmar_ov:.3f}** |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique "
        "réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar, plateau de robustesse "
        "parfait 5/5 sur la grille de fréquences, turnover réduit de 48% vs le #121 quotidien). Doit "
        "encore passer la batterie Règle 9 "
        "(`nonml_pass_validation_battery.py weekly_rebalance_dual_engine`).",
    ]

    out = ROOT / "results" / "nonml_weekly_rebalance_dual_engine_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
