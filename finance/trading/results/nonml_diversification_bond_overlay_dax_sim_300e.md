# Simulation — 300 EUR, diversification obligataire sur DAX (#140, ~3 derniers mois)

Période : 2026-04-14 → 2026-07-10 (63 séances). MATURITY_YEARS=10, aucun paramètre retouché. Limite données (taux allemand mensuel) rappelée.

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold (DAX 100%) | 316.58 EUR | +5.5% | -4.7% | +1.27 | 1.175 |
| **Diversification obligataire** | **314.44 EUR** | **+4.8%** | -4.7% | +1.17 | **1.032** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, ET limite déjà reconnue (taux allemand mensuel forward-fillé, moins probant que DGS10 quotidien) — le verdict statistique réel reste celui du backtest complet (PASS niveau 1 standard ET Calmar, plateau de robustesse parfait 3/3). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py diversification_bond_overlay_dax`).
