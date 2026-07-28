# Pré-enregistrement — Effet jour-de-semaine (effet lundi)

**Committé AVANT tout calcul.** Cycle #3 du backlog non-ML.

## Hypothèse

Anomalie documentée (French 1980, "weekend effect") : le rendement moyen
du lundi (clôture vendredi → clôture lundi) est historiquement inférieur
aux autres jours de la semaine, parfois négatif. Règle déterministe de
calendrier, aucun paramètre appris (hors ML).

## Définition (fixée ici, avant tout résultat)

**Stratégie Skip-Monday** : position longue tous les jours de bourse SAUF
le lundi (flat le lundi — pas de position pendant le rendement
vendredi-clôture → lundi-clôture). Turnover ≈ 2 transactions/semaine
(sortie avant lundi, entrée après), coût 5 bps/transaction (même
convention que le reste du projet).

**Référence** : Buy & Hold classique (1 seul coût d'entrée).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), aucune nouvelle
donnée nécessaire. Le jour de semaine est dérivé directement de la colonne
date déjà présente.

## Critère de succès (pré-enregistré)

Skip-Monday bat Buy & Hold en Sharpe annualisé net de coûts sur **au
moins 4 des 5 marchés**. n_trials=1 (une seule règle testée — pas de
recherche parmi "éviter lundi" / "éviter mardi" / etc., qui serait une
grille de 5 hypothèses et changerait le n_trials).

## Anti-cheat

Même processus que les cycles précédents : ce fichier committé avant
`nonml_day_of_week_backtest.py`, vérification via
`nonml_anti_cheat_check.py day_of_week`.
