# Simulation — 300 EUR, correction taux réaliste sur le #44 cross-marché (#151, ~3 derniers mois)

## S&P 500

Période : 2026-04-13 → 2026-07-13 (63 séances).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 330.57 EUR | +10.2% | -4.5% | +2.98 |
| **Correction taux réaliste** | **326.35 EUR** | **+8.8%** | -4.5% | +2.69 |

## Russell 2000

Période : 2026-04-13 → 2026-07-13 (63 séances).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 336.62 EUR | +12.2% | -4.8% | +2.45 |
| **Correction taux réaliste** | **322.44 EUR** | **+7.5%** | -4.6% | +1.87 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 sur les 2 marchés, plateau de robustesse parfait 3/3 sur chacun). Doit encore passer la batterie Règle 9 par marché (`nonml_pass_validation_battery.py cash_rate_correction_44_crossmarket_<marché>`).
