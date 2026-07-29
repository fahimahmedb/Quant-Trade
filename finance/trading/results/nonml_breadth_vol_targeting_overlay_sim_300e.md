# Simulation — 300 EUR, overlay vol-targeting gaté par breadth NDX+Russell2000 (~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Vol cible 20%, fenêtre 20j, CAP=2.0x quand NDX ET Russell 2000 sont simultanément proches de leur plus haut annuel.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting gaté breadth** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, l'exposition moyenne est de 1.11x — illustration seulement, le verdict statistique reste celui du backtest complet (PASS sur NDX, MDD exactement préservé -82,9%→-82,9%) et de la robustesse (plateau parfait 8/8 sur les grilles CAP 1.5x-3.0x et fenêtre 15-30j).
