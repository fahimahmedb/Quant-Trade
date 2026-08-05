# Simulation — 300 EUR, overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). VR(q=5) sur fenêtre 252j, vol cible 20%, fenêtre vol 20j, CAP=2.0x.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vol-targeting VR gaté** | **350.11 EUR** | **+16.7%** | -7.2% | +2.75 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la porte est active 0.0% du temps (position moyenne 1.00x) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul DAX échoue) et de la robustesse (plateau correct mais pas parfait sur les grilles CAP et fenêtre de vol, notamment 2/5 à fenêtre=15j).
