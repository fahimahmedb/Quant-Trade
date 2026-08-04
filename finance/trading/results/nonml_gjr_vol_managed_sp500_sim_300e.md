# Simulation — 300 EUR, portefeuille volatility-managed GJR-t, S&P 500 (cycle #166, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). `position = clip(20 % / vol_prévue_GJR-t, 0, 2.0x)`, coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy & Hold | 329.86 EUR | +10.0% | -4.6% | +2.98 |
| **Volatility-managed GJR-t** | **340.99 EUR** | **+13.7%** | -7.8% | +2.61 |

Exposition moyenne sur la fenêtre : 1.55x (min 1.04x, max 2.00x).

**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur statistique — le verdict du cycle reste celui du backtest complet et de la grille de robustesse.
