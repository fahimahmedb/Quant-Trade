# Simulation — 300 EUR, correction taux réaliste sur le #44 (#149, NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). MATURITY_YEARS=10, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold (NDX 100%) | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **#44 + correction taux réaliste** | **337.32 EUR** | **+12.4%** | -6.5% | +2.63 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime haussier calme — le verdict statistique réel reste celui du backtest complet (PASS niveau 1, meilleur résultat brut du backlog à ce jour : Sharpe +0,53→+0,84, MDD -82,9%→-37,9%, plateau de robustesse parfait 3/3). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py cash_rate_correction_defensive_vol_targeting_44`).
