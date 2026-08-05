# Simulation — 300 EUR, overlay vol-targeting gaté par le clustering ARCH glissant (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). Fenêtre ARCH/médiane 252j/252j, vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting clustering ARCH gaté** | **350.11 EUR** | **+16.7%** | -7.2% | +2.75 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 0.0% du temps (position moyenne 1.00x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul Composite échoue) et de la robustesse (plateau correct mais pas parfait, dip à 2/5 marchés à fenêtre=15j et 3/5 à CAP=3.0x).
