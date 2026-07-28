# Pré-enregistrement — Effet tournant de mois (Turn-of-Month)

**Committé AVANT tout calcul.** Cycle #2 du backlog non-ML.

## Hypothèse

Anomalie documentée (Ariel 1987, Lakonishok & Smidt 1988) : les rendements
actions sont significativement plus élevés autour du changement de mois
que le reste du mois. Règle déterministe de calendrier, aucun paramètre
appris (hors ML).

## Définition (fixée ici, convention Lakonishok & Smidt 1988, la plus
citée — pas choisie après avoir regardé nos données)

Fenêtre "tournant de mois" (ToM) = les **4 derniers jours de bourse du
mois** + les **3 premiers jours de bourse du mois suivant** (7 séances).
Tous les autres jours = hors-ToM.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée nécessaire.

## Stratégies comparées

- **ToM-only** : position longue uniquement pendant la fenêtre ToM (flat
  le reste du mois). Turnover ≈ 24 transactions/an (2 par mois), coût 5bps
  par transaction (même convention que le reste du projet).
- **Référence** : Buy & Hold classique (1 seul coût d'entrée).

## Critère de succès (pré-enregistré)

ToM-only bat Buy & Hold en Sharpe annualisé net de coûts sur **au moins
4 des 5 marchés**. n_trials=1 (une seule définition testée, pas de grille
sur la largeur de fenêtre).

## Anti-cheat

Même processus que les cycles précédents : ce fichier committé avant
`nonml_turn_of_month_backtest.py`, vérification via
`nonml_anti_cheat_check.py turn_of_month`.
