# Pré-enregistrement — Momentum court terme (1 semaine, niveau titre)

**Committé AVANT tout calcul.** Cycle #14 du backlog non-ML. Soumis à la
règle de succès renforcée. Hypothèse INVERSE du cycle #5 (reversal,
FAIL catastrophique -83,6%) — motivée par la découverte empirique de ce
cycle : sur cet univers/période (NDX-100, 2021-2026, tech/croissance),
les plus mauvais performeurs hebdomadaires ont continué de sous-performer
(momentum domine, pas reversal). Ce cycle teste directement l'implication
symétrique : les meilleurs performeurs hebdomadaires devraient continuer
à surperformer.

## Hypothèse

Momentum à très court terme (1 semaine) : les actions qui ont le plus
monté récemment continuent de surperformer sur l'horizon suivant, sur cet
univers particulier (tech/croissance très volatile 2021-2026) où le
cycle #5 a déjà mis en évidence l'absence de reversal.

## Univers et période

Identique aux cycles #4/#5/#11 : NDX-100 (prix déjà récupérés dans
`data/pead/prices/`), univers dynamique (calendrier union, corrigé au
cycle #4), même limite de biais de survie déjà documentée.

## Définition (fixée ici, avant tout résultat)

- Signal à la date de rebalancement *t* : rendement des 5 dernières
  séances (`close_t / close_{t-5} - 1`) — IDENTIQUE au cycle #5.
- **Rebalancement hebdomadaire** (tous les 5 jours de bourse) — identique
  au cycle #5.
- **Portefeuille "winners"** : équipondéré sur le TERCILE SUPÉRIEUR
  (au lieu du tercile inférieur au cycle #5) — seul changement vs #5.
- **Référence** : Buy & Hold équipondéré de l'univers (même construction
  dynamique que #4/#5).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "winners" doit battre le Buy & Hold équipondéré
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (seul le sens du tri change vs #5, pas une
grille — c'est la contrepartie logique directe d'un résultat déjà
observé, pas un nouveau tuning).

## Anti-cheat

Ce fichier committé avant `nonml_short_term_momentum_backtest.py`,
vérification via `nonml_anti_cheat_check.py short_term_momentum`.
