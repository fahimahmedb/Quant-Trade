"""Simulation — 300 EUR dans le portefeuille volatility-managed GJR-t sur les
~3 derniers mois du NDX (fenêtre illustrative usuelle du backlog, 63 séances).

Aucun paramètre retouché : positions reprises telles quelles de l'artefact
`results/nonml_volatility_managed_portfolio_gjr_pnl.npz` produit par le
backtest pré-enregistré. Cette fenêtre est **illustrative** : 63 séances ne
tranchent rien statistiquement, le verdict reste celui du backtest complet
(9522 séances) et de la batterie Règle 9.
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
from nonml_volatility_managed_portfolio_gjr_backtest import (  # noqa: E402
    CAP, COST_BPS, TARGET_VOL_ANNUAL_PCT,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    d = np.load(ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_pnl.npz",
                allow_pickle=True)
    pos = d["pos"][-WINDOW_DAYS:]
    r = d["r_asset"][-WINDOW_DAYS:]
    dates = pd.to_datetime(d["dates"])[-WINDOW_DAYS:]

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
        "# Simulation — 300 EUR, portefeuille volatility-managed GJR-t (~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r)} séances). "
        f"`position = clip({TARGET_VOL_ANNUAL_PCT:.0f} % / vol_prévue_GJR-t, 0, {CAP}x)`, "
        f"coûts {COST_BPS:.0f} bps.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Volatility-managed GJR-t** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        f"Exposition moyenne sur la fenêtre : {pos.mean():.2f}x "
        f"(min {pos.min():.2f}x, max {pos.max():.2f}x).",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (9522 séances, "
        "PASS de niveau 1) et de la batterie Règle 9 (2/5, PAS de PASS renforcé).",
    ]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
