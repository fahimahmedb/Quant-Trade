# Simulation — 300 EUR, overlay vol-targeting gaté vote majoritaire (NDX, ~3 derniers mois)

Période : 2026-04-13 → 2026-07-13 (63 séances, dont 28 avec porte active). CAP=2.0x, seuil de vote 3/5, aucun paramètre retouché après les résultats précédents.

| | Capital final | Rendement période | MDD | Sharpe ann. |
|---|---|---|---|---|
| BuyHold | 349.93 EUR | +16.6% | -7.2% | +2.74 |
| **Overlay vote majoritaire** | **353.65 EUR** | **+17.9%** | -9.0% | +2.63 |

**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict statistique réel n'est PAS encore établi à ce stade (Règle 9) : ce PASS niveau 1 (plateau de robustesse parfait 12/12 sur 3 grilles, meilleur delta Sharpe testé jusqu'ici) doit encore passer la batterie de validation renforcée (`nonml_pass_validation_battery.py ensemble_vote_vol_targeting_overlay`, n_trials=taille du backlog) avant toute déclaration finale — ET reste construit à partir de 5 gates choisies APRÈS avoir vu qu'elles étaient déjà PASS niveau 1 (biais de sélection assumé).
