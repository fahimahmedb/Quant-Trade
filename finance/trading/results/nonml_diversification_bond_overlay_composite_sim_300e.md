# Simulation — 300 EUR, diversification obligataire sur le Composite (#143, ~3 derniers mois)

Période : 2026-04-10 → 2026-07-10 (63 séances).

| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |
|---|---|---|---|---|---|
| BuyHold (Composite 100%) | 345.30 EUR | +15.1% | -7.1% | +2.77 | 2.126 |
| **Diversification obligataire** | **338.65 EUR** | **+12.9%** | -7.1% | +2.63 | **1.815** |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, ET échantillon sous-jacent déjà court (5 ans, contrairement aux 40 ans de NDX) — robustesse partielle seulement (1/3 PASS standard, 2/3 PASS Calmar sur la grille de maturité). Doit encore passer la batterie Règle 9 (`nonml_pass_validation_battery.py diversification_bond_overlay_composite`).
