# Simulation — 300 EUR, empilement diversification obligataire + rebalancement hebdomadaire (#137, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). MATURITY_YEARS=10, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold (NDX 100%) | 352.39 EUR | +17.5% | -7.0% | +2.74 | 2.488 |
| **#131 + diversification obligataire** | **358.60 EUR** | **+19.5%** | -7.8% | +3.06 | **2.493** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar, MDD -46,5% le meilleur jamais obtenu dans ce backlog, plateau de robustesse parfait 3/3 sur la grille de maturité). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py diversification_bond_weekly_rebalance_stack`).
