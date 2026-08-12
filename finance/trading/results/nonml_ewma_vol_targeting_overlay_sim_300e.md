# Simulation — 300 EUR, overlay vol-targeting estimateur EWMA (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). λ=0.94, fenêtre d'amorçage 20j, vol cible 20%, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay vol-targeting EWMA** | **347.85 EUR** | **+16.0%** | -8.1% | +2.67 |

**Lecture honnête** : sur cette fenêtre de 63 séances, l'exposition moyenne est de 0.92x — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul Composite échoue) et de la robustesse (plateau solide, 4/5-5/5 sur la grille CAP, 4/5 parfaitement stable sur la grille fenêtre d'amorçage).
