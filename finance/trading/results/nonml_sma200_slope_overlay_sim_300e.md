# Simulation — 300 EUR, overlay filtre de pente SMA200 (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x quand SMA200(t) > SMA200(t-20).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay pente SMA200** | **402.66 EUR** | **+34.2%** | -14.1% | +2.74 |

**Lecture honnête** : sur cette fenêtre de 63 séances, l'exposition moyenne est de 2.00x — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 5/5 marchés) et de la robustesse (plateau parfait 5/5 sur les deux grilles CAP 1.5x-3.0x et SLOPE_LAG 15j-30j).
