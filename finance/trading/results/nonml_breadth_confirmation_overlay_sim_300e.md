# Simulation — 300 EUR, overlay confirmation multi-marché NDX+Russell2000 (~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x si NDX ET Russell 2000 ≥95% de leur plus haut 252j, 1.0x sinon.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold (NDX) | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay confirmation multi-marché** | **392.65 EUR** | **+30.9%** | -14.2% | +2.43 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la position est levée 93.7% du temps — illustration seulement, le verdict statistique reste celui du backtest complet (PASS marginal, marge de Sharpe très fine +0,01) et de la robustesse (échoue déjà à CAP=3.0x sur le Sharpe — résultat fragile, à nuancer fortement par rapport aux plateaux parfaits d'autres cycles comme #37/#38).
