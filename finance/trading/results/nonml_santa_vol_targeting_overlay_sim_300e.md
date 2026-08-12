# Simulation — 300 EUR, overlay vol-targeting gaté par Santa Claus Rally (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Vol cible 20%, fenêtre 20j, CAP=2.0x pendant la fenêtre Santa Claus Rally (cette fenêtre avril-juillet ne contient aucune séance de la fenêtre calendaire — signal constant à 1.0x).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay vol-targeting Santa Claus** | **352.57 EUR** | **+17.5%** | -7.0% | +2.75 |

**Lecture honnête** : sur cette fenêtre de 63 séances (avril-juillet), l'exposition moyenne est de 1.00x — illustration délibérément neutre, la fenêtre calendaire testée ne recoupant jamais cette période. Le verdict statistique reste celui du backtest complet (PASS 4/5 marchés) et de la robustesse (plateau parfait 4/5 sur les grilles CAP 1.5x-3.0x et fenêtre 15-30j).
