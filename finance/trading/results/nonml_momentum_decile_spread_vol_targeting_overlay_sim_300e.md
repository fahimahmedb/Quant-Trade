# Simulation — 300 EUR, overlay vol-targeting gaté spread décile de momentum (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 28 avec porte active). CAP=2.0x, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 352.39 EUR | +17.5% | -7.0% | +2.74 |
| **Overlay spread décile** | **356.79 EUR** | **+18.9%** | -8.8% | +2.63 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel n'est PAS encore établi à ce stade (Règle 9) : ce PASS niveau 1 (plateau de robustesse parfait 8/8) doit encore passer la batterie de validation renforcée (`nonml_pass_validation_battery.py momentum_decile_spread_vol_targeting_overlay`) avant toute déclaration finale.
