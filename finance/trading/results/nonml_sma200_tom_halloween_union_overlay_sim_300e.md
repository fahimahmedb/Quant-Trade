# Simulation — 300 EUR, overlay union SMA200∪(ToM∪Halloween) (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances). CAP=2.0x si tendance haussière OU ToM OU Halloween, 1.0x sinon.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay union SMA200∪ToM∪Halloween** | **414.14 EUR** | **+38.0%** | -13.5% | +2.74 |

**Lecture honnête** : sur cette fenêtre de 63 séances, la position est levée 100.0% du temps (union très large des 3 signaux) — illustration seulement, le verdict statistique reste celui du backtest complet (PASS 5/5 marchés) et de la robustesse (5/5 au CAP pré-enregistré 2.0x et à 1.5x, mais dégradé à 4/5 puis 3/5 aux CAP plus élevés 2.5x/3.0x — contrairement au plateau parfait du #29 seul, l'exposition quasi-permanente de cette union amplifie le risque de volatility drag à fort levier).
