# Simulation — 300 EUR, overlay vol-targeting gaté par la vol-de-la-vol glissante (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre vol-de-la-vol/médiane 252j/252j, vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay vol-targeting vol-de-la-vol gaté** | **356.79 EUR** | **+18.9%** | -8.8% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul Russell 2000 échoue) et de la robustesse (plateau correct, CAP stable à excellent 4/5-5/5, fenêtre de vol un peu plus sensible 3/5-4/5).
