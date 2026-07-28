# Simulation — 300 EUR, stratégie Tournant-de-mois (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, 63 demandées). Spécification 4j/3j pré-enregistrée, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **ToM-only** | **326.62 EUR** | **+8.9%** | -3.2% | +3.24 |

**Lecture honnête** : fenêtre courte (~3 mois) — un seul cycle mensuel et demi de turn-of-month observé ici, échantillon bien trop petit pour juger quoi que ce soit seul ; à lire uniquement comme illustration, le verdict statistique réel reste celui du backtest complet (`results/nonml_turn_of_month_result.md`, PASS 4/5 marchés) et du test de robustesse (plateau modéré, pas parfaitement stable : 3/5, 4/5, 3/5 selon la largeur de fenêtre).
