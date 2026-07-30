# Pré-enregistrement — Momentum absolu dual (rotation) NDX / proxy obligataire

**Committé AVANT tout calcul.** Cycle #148 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`, et la **Règle 10**
nouvellement adoptée (rémunération explicite de la fraction détenue —
ici toujours 100% investi dans un actif rémunéré, jamais de cash).

## Hypothèse

Rupture avec toute la famille diversification SIMULTANÉE déjà
exhaustivement testée (#134-147, 14 cycles) : au lieu de répartir le
capital entre NDX et obligations en fonction de la volatilité, ce
cycle teste une ROTATION binaire de type "dual momentum" (Antonacci
2014) — être investi à 100% dans l'actif (NDX ou obligations 10 ans)
qui a eu le meilleur rendement sur les 12 derniers mois glissants,
décision prise mensuellement. Motivé par la littérature académique
documentée du momentum cross-asset (pas une construction ad hoc).

## Définition (fixée ici, avant tout résultat)

- Rebalancement MENSUEL (fin de chaque mois calendaire), pas
  quotidien — convention standard de la littérature dual momentum,
  pas choisie après avoir vu un résultat.
- Signal : rendement cumulé glissant sur les 252 dernières séances de
  chaque actif (NDX log-return cumulé ; proxy obligataire DGS10 avec
  la même formule de duration modifiée que le #134/#136/#137/#139/
  #141, cumulé sur 252 séances), calculé à la fin du mois précédent
  (causal, aucun lookahead).
- Position : 100% NDX si momentum NDX > momentum obligataire,
  100% obligataire sinon (JAMAIS de cash, conforme Règle 10 — la
  fraction non-NDX est TOUJOURS le proxy obligataire rémunéré, jamais
  0%).
- Coûts : 5 bps par unité de turnover (basculement complet =
  turnover 2,0 à chaque rotation).
- **Référence** : Buy & Hold 100% NDX.
- Univers : NDX (40 ans), cohérent avec le reste de la famille.

## Critère de succès (pré-enregistré, DEUX volets, cohérence avec la famille)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py
dual_momentum_ndx_bond_rotation`, n_trials=taille totale du backlog
(jamais 1).

## Robustesse prévue (SI PASS niveau 1)

Grille non-tunable : fenêtre de momentum ∈ {126j (~6 mois), 189j
(~9 mois), 252j (~12 mois, pré-enregistré), 378j (~18 mois)} — la
fréquence de rebalancement (mensuelle) n'est PAS retunée.

## Anti-cheat

Ce fichier committé avant
`nonml_dual_momentum_ndx_bond_rotation_backtest.py`, vérification via
`nonml_anti_cheat_check.py dual_momentum_ndx_bond_rotation`. Aucune
nouvelle donnée (NDX et DGS10 déjà en local).
