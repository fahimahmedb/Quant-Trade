"""Simulation — 300 EUR dans l'overlay Turn-of-Month levé (NDX), ~3
derniers mois. Spécification pré-enregistrée (CAP=2.0x), aucun paramètre
retouché après les résultats de backtest/robustesse.
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
from nonml_tom_overlay_backtest import tom_mask, CAP, COST_BPS  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    mask_full = tom_mask(df["date"])

    close = close_full[-(WINDOW_DAYS + 1):]
    mask = mask_full[-(WINDOW_DAYS + 1):]
    dates = df["date"].values[-(WINDOW_DAYS + 1):]

    bh_full = np.log(close[1:] / close[:-1])
    m = mask[1:]
    pos = np.where(m, CAP, 1.0)
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    # Equite composee en LOG : les series pnl_* sont des rendements log,

    # donc equity = CAPITAL0 * exp(cumsum(pnl)), pas cumprod(1+pnl).

    # Voir results/nonml_log_return_compounding_audit.md.

    equity_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    equity_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_ov = trading_metrics(pnl_ov)
    me_bh = trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, overlay Turn-of-Month levé (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). Spécification pré-enregistrée (CAP=2.0x pendant la "
        "fenêtre ToM, 1.0x sinon), aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay ToM x2** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois, 1-2 cycles ToM observés) — "
        "illustration uniquement, le verdict statistique réel reste celui du backtest "
        "complet (PASS 4/5 marchés) et de la robustesse (plateau stable 4/5 sur CAP "
        "1.5x-3.0x). Le MDD de l'overlay levé doit être comparé à celui du Buy&Hold : le "
        "levier amplifie aussi les pertes, pas seulement les gains."
    ]

    out = ROOT / "results" / "nonml_tom_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
