# Simulation — 300 EUR, overlay vol-targeting gaté pente courbe des taux US (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 3 avec porte active). CAP=2.0x, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay pente courbe des taux** | **351.09 EUR** | **+17.0%** | -7.2% | +2.79 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel n'est PAS encore établi à ce stade (Règle 9) : ce PASS niveau 1 (plateau de robustesse parfait 8/8, testé sur 40 ans d'historique complet couvrant les crises 2000-02/2008) doit encore passer la batterie de validation renforcée (`nonml_pass_validation_battery.py yield_curve_slope_vol_targeting_overlay`) avant toute déclaration finale.
