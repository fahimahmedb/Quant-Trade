"""Simulation — 300 EUR dans la correction taux réaliste sur le #44
cross-marché (#151, S&P 500 et Russell 2000), ~3 derniers mois. Aucun
paramètre retouché après les résultats précédents.
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

CAPITAL0 = 300.0
WINDOW_DAYS = 63
COST_BPS = 5.0
MARKETS = {"S&P 500": "sp500", "Russell 2000": "russell2000"}


def mdd(equity):
    running_max = np.maximum.accumulate(equity)
    return (equity / running_max - 1.0).min() * 100


def main():
    lines = ["# Simulation — 300 EUR, correction taux réaliste sur le #44 cross-marché (#151, ~3 derniers mois)", ""]
    for name, slug in MARKETS.items():
        d = np.load(ROOT / "results" / f"nonml_cash_rate_correction_44_crossmarket_{slug}_pnl.npz", allow_pickle=True)
        pos_eq_full, r_mkt_full, r_bond_full = d["pos"], d["r_asset"], d["r_alt"]
        dates_full = pd.to_datetime(d["dates"])

        pos_eq = pos_eq_full[-WINDOW_DAYS:]
        r_mkt = r_mkt_full[-WINDOW_DAYS:]
        r_bond = r_bond_full[-WINDOW_DAYS:]
        dates = dates_full[-WINDOW_DAYS:]

        r_combined = pos_eq * r_mkt + (1.0 - pos_eq) * r_bond
        turn = np.abs(np.diff(pos_eq, prepend=1.0))
        pnl_ov = r_combined - turn * (COST_BPS / 1e4)
        pnl_bh = r_mkt.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        # Equite composee en LOG : les series pnl_* sont des rendements log,

        # donc equity = CAPITAL0 * exp(cumsum(pnl)), pas cumprod(1+pnl).

        # Voir results/nonml_log_return_compounding_audit.md.

        equity_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
        equity_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))
        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r_mkt)} séances).")
        lines.append("")
        lines.append("| | Capital final | Rendement période | MDD | Sharpe ann. |")
        lines.append("|---|---|---|---|---|")
        lines.append(
            f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
            f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |"
        )
        lines.append(
            f"| **Correction taux réaliste** | **{equity_ov[-1]:.2f} EUR** | "
            f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |"
        )
        lines.append("")

    lines.append(
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique "
        "réel reste celui du backtest complet (PASS niveau 1 sur les 2 marchés, plateau de robustesse "
        "parfait 3/3 sur chacun). Doit encore passer la batterie Règle 9 par marché "
        "(`nonml_pass_validation_battery.py cash_rate_correction_44_crossmarket_<marché>`)."
    )

    out = ROOT / "results" / "nonml_cash_rate_correction_44_crossmarket_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
