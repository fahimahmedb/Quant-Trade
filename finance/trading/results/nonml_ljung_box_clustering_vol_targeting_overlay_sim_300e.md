# Simulation — 300 EUR, overlay vol-targeting gaté par la statistique de Ljung-Box glissante (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre Q/médiane 252j/252j (Q(maxlag=22)), vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay Ljung-Box gaté** | **356.79 EUR** | **+18.9%** | -8.8% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau relativement fragile : grille CAP 3-4/5 avec un seul point à 4/5, grille fenêtre de vol 2-4/5 avec la valeur pré-enregistrée isolée).
