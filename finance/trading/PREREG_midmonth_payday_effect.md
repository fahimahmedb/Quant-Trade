# Pré-enregistrement — Effet mi-mois / jour de paie (Midmonth Payday Effect)

**Committé AVANT tout calcul.** Cycle #276 du backlog non-ML (correction
de doublons incluse, voir note ci-dessous).

## Correction préalable (détectée avant tout calcul, Règle 1)

Deux des trois idées proposées à la clôture du cycle #275 sont en réalité
des **doublons non détectés** d'hypothèses déjà testées :
- L'ancienne ligne #276 ("asymétrie/skewness glissante pour le
  vol-targeting") est identique au **#218** (déjà testé, **FAIL**, 3/5
  marchés < seuil 4/5) — même construction exacte (skewness de
  Fisher-Pearson, fenêtre glissante 252j, médiane glissante 252j).
- L'ancienne ligne #277 ("proximité du plus bas 52-semaines") est
  identique au **#75** (déjà testé, **FAIL**, tercile le plus proche du
  plus-bas annuel, Sharpe et rendement tous deux dégradés).

Ces deux lignes sont retirées du backlog "à faire" sans nouvelle
exécution (aucune valeur ajoutée à re-calculer un résultat déjà connu).
Seule l'ancienne ligne #278 (effet mi-mois/jour de paie), la seule des
trois idées réellement nouvelle, est traitée dans ce cycle.

## Hypothèse

Anomalie documentée dans la littérature de microstructure de marché :
les flux de liquidité institutionnels et de détail se concentrent autour
des dates de versement de salaire et de cotisation retraite US
(bimensuel/semi-mensuel, typiquement autour du 15 et de la fin de mois —
Ogden 1990 "The end of the month effect in stock returns", Wachtel 1942,
Ariel 1987 pour la littérature générale de saisonnalité intra-mois).
Distincte du turn-of-month déjà testé (#2/#8 : 4 derniers j. + 3 premiers
j. du mois, capture la fin de mois), du jour-de-semaine (#3), du Santa
Claus rally (#6) et de l'effet jour férié (#7, détection de trou
calendaire) : ici la fenêtre visée est le **milieu** du mois calendaire,
motivée par le versement de paie semi-mensuel (15 du mois), pas la
frontière entre deux mois.

## Définition (fixée ici, AVANT tout calcul — pas choisie après avoir
regardé nos données)

Pour chaque mois calendaire, les séances de bourse sont classées par
rang croissant (`rank_asc`, 1 = premier jour de bourse du mois). Soit
`n` le nombre total de séances du mois et `mid = round((n+1)/2)` son rang
médian (milieu du mois EN JOURS DE BOURSE, pas en jours calendaires —
robuste aux week-ends/jours fériés, même logique data-driven que le
ToM #2 qui utilise déjà `rank_asc`/`rank_desc`). Fenêtre "mi-mois" =
les séances dont `|rank_asc - mid| ≤ 2` (5 séances centrées sur le
milieu du mois). Aucun paramètre ajusté après avoir vu un résultat :
la largeur (±2j, 5 séances) est choisie par analogie directe avec la
largeur de la fenêtre ToM déjà validée (7 séances, #2/#8), pas par une
recherche sur nos données.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée nécessaire.

## Stratégies comparées

- **Midmonth-only** : position longue uniquement pendant la fenêtre
  mi-mois (flat le reste du mois), coût 5 bps par transaction (même
  convention que #2/#3/#6/#7).
- **Référence** : Buy & Hold classique.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

Midmonth-only bat Buy & Hold en Sharpe annualisé **ET** en rendement
total net de coûts sur **au moins 4 des 5 marchés**. n_trials=1 (une
seule définition testée, pas de grille sur la largeur de fenêtre à ce
stade — une éventuelle version overlay, par analogie avec #8, serait un
cycle distinct si ce signal est PASS).

## Anti-cheat

Ce fichier committé avant `nonml_midmonth_payday_effect_backtest.py`.
Vérification prévue : recalcul indépendant du masque mi-mois sur un
échantillon de mois, absence de fuite (le masque ne dépend que du rang
calendaire du jour, connu à l'avance, donc pas de risque de lookahead
par construction — vérifié quand même par audit dédié comme pour #7).
Sortie : `results/nonml_midmonth_payday_effect_result.md`.
