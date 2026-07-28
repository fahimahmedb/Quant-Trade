# Pré-enregistrement — Rallye de fin d'année (Santa Claus Rally)

**Committé AVANT tout calcul.** Cycle #6 du backlog non-ML. Soumis à la
règle de succès renforcée (Sharpe ET rendement absolu).

## Hypothèse

Anomalie documentée (Yale Hirsch, "Stock Trader's Almanac") : rendements
historiquement plus élevés durant les 5 derniers jours de bourse de
décembre + les 2 premiers jours de bourse de janvier. Règle déterministe
de calendrier, aucun paramètre appris.

## Définition (fixée ici, avant tout résultat)

Fenêtre = 5 derniers jours de bourse de décembre + 2 premiers jours de
bourse de janvier (7 séances), calculée à partir du calendrier de séances
déjà présent dans les données (même méthode que le cycle #2, rank
ascendant/descendant par groupby mensuel).

- **Stratégie Santa-only** : position longue uniquement pendant cette
  fenêtre, flat le reste de l'année. ~2 transactions/an (turnover très
  faible), coût 5 bps/transaction.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), aucune nouvelle
donnée nécessaire.

## Critère de succès RENFORCÉ (pré-enregistré)

Santa-only bat Buy & Hold **simultanément** en Sharpe annualisé net de
coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_santa_claus_rally_backtest.py`,
vérification via `nonml_anti_cheat_check.py santa_claus_rally`.
