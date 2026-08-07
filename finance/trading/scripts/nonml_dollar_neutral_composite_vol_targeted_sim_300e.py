"""Simulation — 300 EUR, sleeve dollar-neutre composite redimensionné
par sa vol (cycle #350), sur les ~3 derniers mois disponibles.
Aucun paramètre retouché.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    data = np.load(ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_pnl.npz", allow_pickle=True)
    r_vt = data["pnl_candidate"].astype(float)
    r_ref = data["pnl_ref"].astype(float)
    dates = data["dates"]

    r_vt_w = r_vt[-WINDOW_DAYS:]
    r_ref_w = r_ref[-WINDOW_DAYS:]
    dates_w = dates[-WINDOW_DAYS:]

    eq_vt = CAPITAL0 * np.cumprod(1.0 + r_vt_w)
    eq_ref = CAPITAL0 * np.cumprod(1.0 + r_ref_w)
    me_vt = trading_metrics(r_vt_w)
    me_ref = trading_metrics(r_ref_w)

    lines = [
        "# Simulation — 300 EUR, sleeve dollar-neutre redimensionné par sa vol (cycle #350), ~3 derniers mois",
        "",
        f"Période : {str(dates_w[0])[:10]} → {str(dates_w[-1])[:10]} ({len(r_vt_w)} séances). "
        "Sleeve autofinancé (dollar-neutre) : le capital simulé représente le CAPITAL DE MARGE alloué "
        "au sleeve, pas une position directionnelle sur un indice.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold PIT (contexte, hérité du #349) | {eq_ref[-1]:.2f} EUR | "
        f"{100 * (eq_ref[-1] / CAPITAL0 - 1):+.1f}% | {mdd_pct(eq_ref):.1f}% | {me_ref['sharpe_ann']:+.2f} |",
        f"| **Sleeve redimensionné par sa vol** | **{eq_vt[-1]:.2f} EUR** | "
        f"**{100 * (eq_vt[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_vt):.1f}% | {me_vt['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (Sharpe>0 ET "
        "t-stat>2, atteint sur 2907 séances) et de la grille de robustesse (8/9 cellules). "
        "Un sleeve dollar-neutre n'a pas d'exposition directionnelle au marché : sa "
        "performance sur une fenêtre courte de 3 mois est peu informative en soi (le "
        "signal a besoin de nombreux cycles de rebalancement/régimes de vol pour "
        "s'exprimer), rapportée ici uniquement par souci de cohérence avec le protocole.",
    ]

    out = ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
