# Simulation — 300 EUR, overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Porte kurtosis (252j/252j) ET porte ν Student-t (252j, refit 21j, médiane 252j), vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay conjonction ET gaté** | **356.79 EUR** | **+18.9%** | -8.8% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte ET est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau correct mais pas parfait : grille CAP 3-4/5, grille fenêtre de vol 2-4/5, quasi identique à celui du #237 dont ce candidat hérite l'essentiel de la sensibilité).
