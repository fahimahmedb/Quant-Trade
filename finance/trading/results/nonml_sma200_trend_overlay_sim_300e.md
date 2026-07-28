# Simulation — 300 EUR, overlay filtre de tendance SMA200 (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x si prix > SMA200j, 1.0x sinon.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay SMA200** | **402.66 EUR** | **+34.2%** | -14.1% | +2.74 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la position est levée 100.0% du temps (marché en tendance haussière selon le filtre) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 5/5 marchés, sur 40 ans pour NDX) et de la robustesse (plateau 5/5 constant sur la grille CAP 1.5x-3.0x).
