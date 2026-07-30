# Simulation — 300 EUR, pente courbe des taux US sur S&P 500 (~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 4 avec porte active). CAP=2.0x, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 329.86 EUR | +10.0% | -4.6% | +2.98 |
| **Overlay pente courbe des taux** | **332.57 EUR** | **+10.9%** | -4.6% | +3.15 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel n'est PAS encore établi à ce stade (Règle 9) : ce PASS niveau 1 a une robustesse FAIBLE (2/4 sur les deux grilles, pas un plateau) et un MDD dégradé par rapport à Buy&Hold sur l'historique complet — signaux d'alerte déjà notables avant même la batterie. Doit encore passer `nonml_pass_validation_battery.py yield_curve_slope_sp500_vol_targeting_overlay`.
