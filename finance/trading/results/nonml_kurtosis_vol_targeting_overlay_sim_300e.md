# Simulation — 300 EUR, overlay vol-targeting gaté par la kurtosis glissante (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre kurtosis/médiane 252j/252j, vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting kurtosis gaté** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 45.2% du temps (position moyenne 1.11x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau parfait 8/8 sur les deux grilles CAP 1.5x-3.0x et fenêtre 15j-30j).
