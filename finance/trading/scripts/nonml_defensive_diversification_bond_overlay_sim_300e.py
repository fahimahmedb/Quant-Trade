"""Simulation — 300 EUR dans la diversification obligataire du #115
(NDX + proxy DGS10), ~3 derniers mois. Spécification pré-enregistrée
(MATURITY_YEARS=10), aucun paramètre retouché après les résultats
précédents.
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


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_diversification_bond_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full, r_bond_full = d["pos"], d["r_asset"], d["r_alt"]
    dates_full = pd.to_datetime(d["dates"])

    pos_eq = pos_eq_full[-WINDOW_DAYS:]
    r_ndx = r_ndx_full[-WINDOW_DAYS:]
    r_bond = r_bond_full[-WINDOW_DAYS:]
    dates = dates_full[-WINDOW_DAYS:]

    r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
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
        "# Simulation — 300 EUR, diversification obligataire du #115 (NDX + DGS10, ~3 derniers mois)",
        "",
        f"Période : {dates[0].date()} → {dates[-1].date()} ({len(r_ndx)} séances). MATURITY_YEARS=10, "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |",
        "|---|---|---|---|---|---|",
        f"| BuyHold (NDX 100%) | {equity_bh[-1]:.2f} EUR | {ret_bh_pct:+.1f}% | {mdd(equity_bh):.1f}% | "
        f"{me_bh['sharpe_ann']:+.2f} | {calmar_bh:.3f} |",
        f"| **#115 + proxy obligataire** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{ret_ov_pct:+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} | "
        f"**{calmar_ov:.3f}** |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime haussier calme "
        "(peu d'occasions pour la diversification obligataire de faire ses preuves face à un vrai choc "
        "actions) — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard "
        "ET Calmar, meilleur résultat brut du backlog à ce jour : Sharpe +0,53→+0,77, MDD -82,9%→-50,9%, "
        "plateau de robustesse parfait 3/3 sur la grille de maturité). Doit encore passer la batterie "
        "Règle 9 (`nonml_pass_validation_battery.py defensive_diversification_bond_overlay`).",
    ]

    out = ROOT / "results" / "nonml_defensive_diversification_bond_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
