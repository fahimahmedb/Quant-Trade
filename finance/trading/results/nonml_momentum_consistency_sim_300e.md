# Simulation — 300 EUR, portefeuille Momentum de constance (NDX-100, ~3 derniers mois)

Période : 2026-04-27 → 2026-07-27 (63 séances). Spécification pré-enregistrée (N_BLOCKS=12, BLOCK_LEN=21, REBAL_EVERY=21j, tercile sup.), aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy&Hold équipondéré (univers) | 309.70 EUR | +3.2% | -6.8% | +0.82 |
| **Momentum de constance** | **312.09 EUR** | **+4.0%** | -17.3% | +0.58 |

**Lecture honnête** : fenêtre de 3 mois illustrative uniquement (~3 rebalancements mensuels observés) — le verdict statistique réel reste celui du backtest complet (2022-2026, PASS Sharpe+rendement) et de la robustesse (4/5 variantes voisines de paramètres restent OUI/OUI, N_BLOCKS=14 seul échoue).
