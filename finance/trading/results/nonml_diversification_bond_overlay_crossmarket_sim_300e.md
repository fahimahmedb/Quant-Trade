# Simulation — 300 EUR, diversification obligataire cross-marché (#136, ~3 derniers mois)

## S&P 500

Période : 2026-04-13 → 2026-07-13 (63 séances).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 329.86 EUR | +10.0% | -4.6% | +2.98 |
| **Diversification obligataire** | **330.02 EUR** | **+10.0%** | -4.6% | +2.99 |

## Russell 2000

Période : 2026-04-13 → 2026-07-13 (63 séances).

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 335.13 EUR | +11.7% | -4.9% | +2.45 |
| **Diversification obligataire** | **329.50 EUR** | **+9.8%** | -4.9% | +2.16 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar sur les 2 marchés, plateau de robustesse parfait 3/3 sur chacun). Doit encore passer la batterie Règle 9 par marché (`nonml_pass_validation_battery.py diversification_bond_overlay_crossmarket_<marché>`).
