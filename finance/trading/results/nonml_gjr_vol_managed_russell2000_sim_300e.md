# Simulation — 300 EUR, portefeuille volatility-managed GJR-t, Russell 2000 (cycle #166, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). `position = clip(20 % / vol_prévue_GJR-t, 0, 2.0x)`, coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy & Hold | 336.62 EUR | +12.2% | -4.8% | +2.45 |
| **Volatility-managed GJR-t** | **327.72 EUR** | **+9.2%** | -5.6% | +1.75 |

Exposition moyenne sur la fenêtre : 1.06x (min 0.72x, max 1.31x).

**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur statistique — le verdict du cycle reste celui du backtest complet et de la grille de robustesse.
