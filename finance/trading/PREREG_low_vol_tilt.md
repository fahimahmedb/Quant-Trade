# Pré-enregistrement — Low-Volatility Tilt

**Committé AVANT tout calcul.** Cycle #15 du backlog non-ML. Soumis à la
règle de succès renforcée.

## Hypothèse

Anomalie low-volatility (Ang, Hodrick, Xing & Zhang 2006 et suivants) :
les actions à faible volatilité réalisée offrent un rendement
ajusté-au-risque (voire absolu) supérieur aux actions à forte volatilité,
contredisant le CAPM classique (rendement ∝ risque). Règle déterministe,
aucun paramètre appris.

## Univers et période

NDX-100 (prix déjà récupérés dans `data/pead/prices/`), même construction
d'univers dynamique que les cycles #4/#5/#14 (calendrier union, biais de
survie déjà documenté).

## Définition (fixée ici, avant tout résultat)

- Vol réalisée à la date de rebalancement *t* : écart-type des rendements
  quotidiens sur les 60 séances précédentes (causal, jusqu'à *t*
  inclus).
- **Rebalancement mensuel** (tous les 21 jours de bourse, cohérent avec
  le cycle #4).
- **Portefeuille "low-vol"** : équipondéré sur le TERCILE INFÉRIEUR de
  vol réalisée à chaque rebalancement.
- **Référence** : Buy & Hold équipondéré de l'univers (même construction
  dynamique que #4/#5/#14).
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille low-vol doit battre le Buy & Hold équipondéré
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (fenêtre 60j et rebalancement 21j fixés une
fois, pas de grille).

## Anti-cheat

Ce fichier committé avant `nonml_low_vol_tilt_backtest.py`, vérification
via `nonml_anti_cheat_check.py low_vol_tilt`.
