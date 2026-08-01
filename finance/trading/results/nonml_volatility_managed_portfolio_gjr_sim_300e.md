# Simulation — 300 EUR, portefeuille volatility-managed GJR-t (~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). `position = clip(20 % / vol_prévue_GJR-t, 0, 2.0x)`, coûts 5 bps.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| Buy & Hold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Volatility-managed GJR-t** | **349.86 EUR** | **+16.6%** | -9.6% | +2.63 |

Exposition moyenne sur la fenêtre : 1.03x (min 0.58x, max 1.53x).

**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur statistique — le verdict du cycle reste celui du backtest complet (9522 séances, PASS de niveau 1) et de la batterie Règle 9 (2/5, PAS de PASS renforcé).
