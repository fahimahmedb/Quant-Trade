# Simulation — 300 EUR, portefeuille volatility-managed GJR-t, DAX (cycle #166, ~3 derniers mois)

Période : 2026-04-14 → 2026-07-10 (63 séances). `position = clip(20 % / vol_prévue_GJR-t, 0, 2.0x)`, coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy & Hold | 316.58 EUR | +5.5% | -4.7% | +1.27 |
| **Volatility-managed GJR-t** | **312.68 EUR** | **+4.2%** | -5.8% | +0.80 |

Exposition moyenne sur la fenêtre : 1.21x (min 0.90x, max 1.54x).

**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur statistique — le verdict du cycle reste celui du backtest complet et de la grille de robustesse.
