# Pré-enregistrement — Overlay levé "turn-of-quarter"

**Committé AVANT tout calcul.** Cycle #65 du backlog non-ML. Variante
TRIMESTRIELLE du turn-of-month (#8, PASS mais reclassé FAIL sous la
règle renforcée du 28/07 — voir backlog ligne #2/#8) : teste si l'effet
de rebalancement institutionnel (fonds indiciels, gestion trimestrielle)
est plus marqué aux changements de trimestre qu'aux changements de mois
ordinaires.

## Hypothèse

Le rebalancement institutionnel (fonds indiciels, mandats trimestriels,
clôtures comptables) est structurellement plus actif aux changements de
TRIMESTRE (fin mars, juin, septembre, décembre) qu'aux changements de
mois ordinaires — un sous-ensemble des 12 changements de mois testés au
#8. Restreindre la fenêtre ToM aux 4 changements de trimestre seulement
pourrait capter un effet plus concentré et donc plus robuste que le ToM
mensuel généralisé, qui a échoué au test renforcé (#2/#8).

## Définition (fixée ici, avant tout résultat, réutilise exactement la
même fenêtre que #8 — PAS un ajustement sur les données du projet)

- Fenêtre = mêmes paramètres que le #8 (LAST_N_DAYS=4 dernières séances
  du mois, FIRST_N_DAYS=3 premières séances du mois suivant), mais
  appliquée UNIQUEMENT aux changements de trimestre : mars→avril,
  juin→juillet, septembre→octobre, décembre→janvier (4 occurrences/an au
  lieu de 12 pour le #8).
- Position = **1,0x** en permanence, **CAP = 2,0x** pendant ces fenêtres
  de changement de trimestre, **1,0x** sinon (y compris pendant les 8
  autres changements de mois ordinaires, contrairement au #8).
- Le calendrier est une information connue à l'avance (pas une donnée de
  marché) — même traitement que ToM/Halloween/Santa Claus Rally dans ce
  backlog, même convention d'alignement `[1:]` que #8/#17/#21/#54/#56/#64.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (fenêtre LAST_N_DAYS=4/FIRST_N_DAYS=3 et CAP=2,0x
repris à l'identique du #8, seuls les mois retenus changent — fixés a
priori sur la définition des changements de trimestre calendaires,
aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_turn_of_quarter_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py turn_of_quarter_overlay`.
