# Simulation — 300 EUR, overlay vol-targeting gaté par dispersion cross-sectionnelle NDX-100 (~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Vol cible 20%, fenêtre 20j, CAP=2.0x quand la dispersion cross-sectionnelle est au-dessus de sa médiane 252j.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay vol-targeting dispersion** | **356.40 EUR** | **+18.8%** | -8.8% | +2.62 |

**Lecture honnête** : sur cette fenêtre de 63 séances, l'exposition moyenne est de 1.10x — illustration seulement, le verdict statistique reste celui du backtest complet (PASS sur NDX, MDD exactement préservé) et de la robustesse (plateau parfait 8/8 sur les grilles CAP 1.5x-3.0x et fenêtre 15-30j).
