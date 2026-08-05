# Pré-enregistrement — Batterie Règle 9 sur le #261 (tilt Amihud illiquidité)

**Committé AVANT tout calcul de la batterie.** Cycle #262 du backlog
non-ML. Applique la même discipline que les #194/#201/#238/#241/#243/
#259 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #261 (`PREREG_amihud_illiquidity_tilt.md`,
`results/nonml_amihud_illiquidity_tilt_result.md`) est un PASS net
(Sharpe +0,59→+0,84, rendement +70,0%→+142,8%, MDD quasi inchangé,
robustesse 5/5 plateau parfait) — la seconde hypothèse construite sur la
catégorie volume, jamais soumise à la barre renforcée.

## Adaptation technique (réutilisation, pas une nouvelle conception)

Le #261 est, comme le #258, une stratégie de PORTEFEUILLE (poids sur un
tercile de titres, rebalancés mensuellement) — le format `.npz`
(pos, r_asset, dates, cost_bps) de `nonml_pass_validation_battery.py`
(conçu pour un overlay mono-actif) ne s'applique pas plus ici qu'au
#258. Ce cycle **réutilise strictement le patron déjà écrit et validé au
#259** (`nonml_momentum_turnover_doublesort_pass_validation_battery.py`)
— même structure des 5 contrôles a-e reconstruits à partir de paires
(rendement brut, turnover) candidat/référence — adapté uniquement pour
charger les poids et données du #261 (tilt illiquidité vs Buy&Hold
équipondéré) au lieu du double-tri momentum+turnover. Aucune nouvelle
conception de méthode, Règle 7 (réutilisation stricte).

## Référence

Buy&Hold équipondéré de l'univers éligible — identique à la référence
déjà utilisée dans le backtest du #261.

## Critère de succès (Règle 9, identique aux cycles #111-#259)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=268) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Par précédent direct (#258→#259 : PASS le plus net du backlog en score
brut, mais 3/5 seulement à la batterie, SPA et DSR restant hors
d'atteinte), aucune attente de PASS RENFORCÉ n'est formulée ici — le
#261 a un Sharpe/rendement plus modeste que le #258, un score de
batterie égal ou inférieur est plausible.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #261. Sortie :
`results/nonml_amihud_illiquidity_tilt_pass_validation_battery.md`.
