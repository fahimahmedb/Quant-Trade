# Pré-enregistrement — Batterie Règle 9 sur le #237 (porte de ν glissant MLE Student-t)

**Committé AVANT tout calcul de la batterie.** Cycle #238 du backlog
non-ML. Backlog "à faire" épuisé après le #237. Le #237 est un PASS
niveau 1 frais (4/5 marchés) jamais soumis à cette barre — continue la
même discipline de validation systématique appliquée à chaque nouvelle
hypothèse PASS de la lignée mécanique (#207-#214, #224-#230, #232, #235).

## Contexte et motivation

Le #237 (`PREREG_student_t_tail_vol_targeting_overlay.md`,
`results/nonml_student_t_tail_vol_targeting_overlay_result.md`) réutilise
`diagnostics.py::fit_student_t` (Étape A) comme porte de queue, distincte
de la kurtosis empirique (#219, PASS 4/5). PASS niveau 1 (Composite/NDX/
Russell 2000/S&P 500 passent, DAX échoue), robustesse correcte mais pas
parfaite (grille CAP 3-4/5, grille fenêtre de vol 2-4/5). **Point
important déclaré au #237** : l'audit dédié a révélé une fragilité
numérique réelle de l'estimateur (non-identifiabilité du MLE de ν sur les
fenêtres proches de la gaussienne, ν original jusqu'à ~1,5e10 sur S&P
500), explicitement non corrigée après résultat (Règle 2). Ce cycle teste
si, MALGRÉ cette fragilité de l'estimateur, le signal qui en résulte
possède un edge journalier statistiquement significatif (SPA/DSR) — un
signal peut être bruité dans son détail tout en restant utile en moyenne,
ou au contraire la fragilité peut se traduire par une absence totale de
significativité, ce que la batterie permettra de trancher indépendamment
de la question philosophique de l'identifiabilité de ν.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-#214,
#224-#232, #235).

## Modification technique requise (déclarée avant calcul)

`nonml_student_t_tail_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_student_t_tail_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur NDX, sans aucun changement de logique
de calcul — vérifié par re-exécution identique du résultat déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#235)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (238, jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La fragilité de l'estimateur documentée au #237 (ν non identifiable
   sur ~0-6,3% des séances selon le marché) pourrait se traduire par un
   bruit résiduel qui dégrade spécifiquement la stabilité temporelle (c)
   et/ou le SPA (d), sans nécessairement invalider les jambes agrégées
   Sharpe/rendement déjà mesurées au #237.
2. Le DSR est hors de portée pour les 238 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_student_t_tail_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Anti-cheat inchangé par rapport au #237 (même pratique qu'aux #232/#235).
