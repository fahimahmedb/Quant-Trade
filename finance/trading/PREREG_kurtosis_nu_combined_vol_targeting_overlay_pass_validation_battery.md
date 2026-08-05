# Pré-enregistrement — Batterie Règle 9 sur le #240 (porte combinée ET kurtosis + ν Student-t)

**Committé AVANT tout calcul de la batterie.** Cycle #241 du backlog
non-ML. Backlog "à faire" épuisé après le #240. Le #240 est un PASS
niveau 1 frais (4/5 marchés) jamais soumis à cette barre — continue la
même discipline de validation systématique appliquée à chaque nouvelle
hypothèse PASS de la lignée mécanique (#207-#214, #224-#230, #232, #235,
#238).

## Contexte et motivation

Le #240 (`PREREG_kurtosis_nu_combined_vol_targeting_overlay.md`,
`results/nonml_kurtosis_nu_combined_vol_targeting_overlay_result.md`)
combine par conjonction ET deux portes de queue déjà validées séparément
(#219 kurtosis, PASS 4/5 ; #237 ν Student-t, PASS 4/5, Règle 9 4/5 —
l'un des meilleurs scores du backlog malgré une fragilité numérique
documentée de l'estimateur). Le #240 a montré que la conjonction
reproduit le même pattern de marchés que chaque composante seule, sans
amélioration qualitative apparente, se contentant de réduire le temps
d'exposition (19,6-35,0% contre 26,8-55,8% pour les composantes
individuelles). Ce cycle teste si cette réduction d'exposition, en
resserrant le signal sur les épisodes où les deux mesures de queue
s'accordent, améliore ou dégrade la significativité statistique par
rapport au #237 seul (Règle 9 4/5, SPA p=0,0022) — la meilleure référence
disponible dans cette sous-famille.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-#214,
#224-#232, #235, #238).

## Modification technique requise (déclarée avant calcul)

`nonml_kurtosis_nu_combined_vol_targeting_overlay_backtest.py` sera
étendu pour sauvegarder
`results/nonml_kurtosis_nu_combined_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur NDX, sans aucun changement de logique de
calcul — vérifié par re-exécution identique du résultat déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#238)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (241, jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Une exposition réduite (moins de séances actives) pourrait dégrader la
   stabilité temporelle (c) si les rares séances actives se concentrent
   dans certains folds seulement.
2. Le signal étant une conjonction de deux signaux corrélés (cf. #240,
   même pattern par marché), le SPA pourrait ne pas s'améliorer par
   rapport au #237 seul (p=0,0022) — un résultat similaire ou légèrement
   pire est plausible plutôt qu'une amélioration nette.
3. Le DSR est hors de portée pour les 241 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_kurtosis_nu_combined_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Anti-cheat inchangé par rapport au #240 (même pratique qu'aux
#232/#235/#238).
