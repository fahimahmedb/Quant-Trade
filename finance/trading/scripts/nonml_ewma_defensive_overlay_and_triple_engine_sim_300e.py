"""Simulation — 300 EUR dans l'ensemble à 3 moteurs (#115+GARCH+EWMA)/3,
NDX, ~3 derniers mois. Spécification pré-enregistrée, aucun paramètre
retouché après les résultats précédents.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    d3 = np.load(ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_pnl.npz", allow_pickle=True)
    pos_full, r_full = d3["pos"], d3["r_asset"]
    dates_full = pd.to_datetime(d3["dates"])

    pos = pos_full[-WINDOW_DAYS:]
    r = r_full[-WINDOW_DAYS:]
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

    lines = [
        "# Simulation — 300 EUR, ensemble 3 moteurs (#115+GARCH+EWMA)/3 (NDX, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r)} séances). "
        "Aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay 3 moteurs** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement -- le verdict "
        "statistique réel reste celui du backtest complet (PASS standard ET Calmar) et de la "
        "robustesse (plateau parfait 5/5 sur la grille λ). Doit encore passer la batterie Règle 9 "
        "avant toute déclaration finale."
    ]

    out = ROOT / "results" / "nonml_ewma_defensive_overlay_and_triple_engine_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
