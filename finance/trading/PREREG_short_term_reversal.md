# Pré-enregistrement — Reversal court terme (1 semaine, niveau titre)

**Committé AVANT tout calcul.** Cycle #5 du backlog non-ML. Soumis à la
**règle de succès renforcée** (Sharpe ET rendement absolu).

## Hypothèse

Jegadeesh (1990), Lehmann (1990) : à très court terme (~1 semaine), les
actions qui ont le plus baissé ont tendance à rebondir davantage que
celles qui ont le plus monté (reversal, effet inverse du momentum
classique à moyen terme). Règle déterministe, aucun paramètre appris.

## Univers et période

Constituants ACTUELS du NASDAQ-100 (prix déjà récupérés dans
`data/pead/prices/`), même limite de biais de survie déjà documentée
(PEAD, cycle #4). Univers dynamique (chaque titre pondéré seulement
depuis sa 1ère cotation dans l'échantillon), même construction que le
cycle #4 (calendrier union, pas intersection stricte — bug déjà trouvé et
corrigé sur ce point au cycle #4).

## Définition (fixée ici, avant tout résultat)

- Signal à la date de rebalancement *t* : rendement des 5 dernières
  séances (`close_t / close_{t-5} - 1`).
- **Rebalancement hebdomadaire** (tous les 5 jours de bourse).
- **Portefeuille "losers"** : équipondéré sur le TERCILE INFÉRIEUR de
  l'univers par ce signal à chaque rebalancement (long-only, pari sur le
  rebond — pas long-short, pour rester comparable en exposition de marché
  à Buy & Hold, cohérent avec la règle renforcée).
- **Référence** : Buy & Hold équipondéré de l'univers (titres cotés à
  chaque date, même construction dynamique que cycle #4).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "losers" doit battre le Buy & Hold équipondéré
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (une seule définition — pas de grille sur
l'horizon du signal ni la fréquence de rebalancement).

## Anti-cheat

Même processus que les cycles précédents : ce fichier committé avant
`nonml_short_term_reversal_backtest.py`, vérification via
`nonml_anti_cheat_check.py short_term_reversal`.
