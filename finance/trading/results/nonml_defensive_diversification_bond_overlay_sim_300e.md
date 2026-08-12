# Simulation — 300 EUR, diversification obligataire du #115 (NDX + DGS10, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). MATURITY_YEARS=10, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold (NDX 100%) | 352.39 EUR | +17.5% | -7.0% | +2.74 | 2.488 |
| **#115 + proxy obligataire** | **347.13 EUR** | **+15.7%** | -6.9% | +2.90 | **2.289** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime haussier calme (peu d'occasions pour la diversification obligataire de faire ses preuves face à un vrai choc actions) — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar, meilleur résultat brut du backlog à ce jour : Sharpe +0,53→+0,77, MDD -82,9%→-50,9%, plateau de robustesse parfait 3/3 sur la grille de maturité). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py defensive_diversification_bond_overlay`).
