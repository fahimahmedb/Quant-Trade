# Simulation — 300 EUR, rebalancement hebdomadaire du #121 (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). REBAL_FREQ=5j, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 | 2.488 |
| **Rebalancement hebdomadaire** | **357.93 EUR** | **+19.3%** | -7.9% | +2.98 | **2.439** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar, plateau de robustesse parfait 5/5 sur la grille de fréquences, turnover réduit de 48% vs le #121 quotidien). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py weekly_rebalance_dual_engine`).
