# Pré-enregistrement — Empiler diversification obligataire (#134) sur l'ensemble à 3 moteurs (#124)

**Committé AVANT tout calcul.** Cycle #139 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Le #137 a montré que combiner la diversification obligataire (#134)
avec le rebalancement hebdomadaire (#131) n'était PAS additif (score
Règle 9 retombé à 3/5, la stabilité temporelle du #131 restant le
facteur limitant). Ce cycle teste une base DIFFÉRENTE : la position
équity du #124 (ensemble à 3 moteurs de volatilité indépendants —
réalisé+GJR-GARCH+EWMA — déjà validée, plus lissée que la vol réalisée
simple du #115 puisqu'elle moyenne 3 estimateurs). Hypothèse a priori :
si la stabilité temporelle du #137 était limitée par le bruit propre au
mécanisme #131 (dual-engine + rebalancement hebdomadaire), une base
PLUS LISSE (#124) pourrait préserver le score 4/5 du #134 tout en
gardant le potentiel d'amélioration du MDD observé aux #134/#137.

## Différence structurelle reconnue AVANT calcul (identique au #137)

La position équity du #124 va jusqu'à 1,17x (légèrement au-dessus de
1,0x), contrairement à celle du #115/#134 strictement bornée à [0,
1,0]. Même convention que le #137 : `r_combiné(t) = pos_eq(t)*r_NDX(t)
+ (1-pos_eq(t))*r_bond(t)`, la fraction `(1-pos_eq)` devient légèrement
négative quand `pos_eq>1` (financement du levier au taux obligataire).
Choix fixé ici, avant tout calcul, cohérent avec le #137.

## Définition (fixée ici)

- Position équity : `pos_eq(t)` = position DÉJÀ COMMITTÉE du #124
  (`results/nonml_ewma_defensive_overlay_and_triple_engine_pnl.npz`),
  strictement inchangée.
- Rendement obligataire : IDENTIQUE au #134/#136/#137 (DGS10, duration
  modifiée 10 ans, formule fermée).
- `r_combiné(t) = pos_eq(t)*r_NDX(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover de `pos_eq` (turnover du #124
  inchangé).
- Fenêtre : intersection #124 (NDX 1988-2026) ∩ DGS10 (1962-2026).
- **Référence** : Buy & Hold 100% NDX, même fenêtre.

## Critère de succès (pré-enregistré, DEUX volets, cohérence avec #134/#137)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py
diversification_bond_triple_engine_stack`, n_trials=taille totale du
backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_triple_engine_stack_backtest.py`,
vérification via `nonml_anti_cheat_check.py
diversification_bond_triple_engine_stack`. Aucune nouvelle donnée
(recalcul sur artefacts déjà committés #124 et DGS10 du #134).
