# Pré-enregistrement — Empiler diversification obligataire (#134) + rebalancement hebdomadaire (#131)

**Committé AVANT tout calcul.** Cycle #137 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Deux améliorations INDÉPENDANTES ont chacune amélioré isolément le
score Règle 9 par rapport au #115 de base (3/5) : la diversification
obligataire (#134, 4/5) et le rebalancement hebdomadaire (#131, 3/5,
mais turnover -48%). Ce cycle teste si les empiler (position équity du
#131 au lieu de celle du #115, MÊME proxy obligataire du #134 pour la
fraction complémentaire) pousse le score au-delà de 4/5, ou si les
gains ne sont pas additifs (plafond commun SPA/DSR déjà documenté).

## Différence structurelle reconnue AVANT calcul (pas après avoir vu un résultat)

La position équity du #131 (`nonml_weekly_rebalance_dual_engine_pnl.npz`)
va jusqu'à 1,25x (levier), contrairement à celle du #115/#134 qui est
strictement bornée à [0, 1,0] (jamais de levier). La formule de
diversification `r_combiné(t) = pos_eq(t)*r_marché(t) +
(1-pos_eq(t))*r_bond(t)` produira donc, aux séances où `pos_eq(t)>1`,
une allocation obligataire NÉGATIVE — interprétée comme un financement
du levier au taux obligataire (approximation standard : le coût de
financement d'une position à effet de levier est proche du taux sans
risque/quasi-sans-risque, ici approché par le même proxy DGS10 déjà
utilisé). Choix fixé ICI, avant tout calcul, pas après avoir vu si cela
améliore ou dégrade le résultat — alternative (plafonner pos_eq à 1,0
avant diversification) délibérément écartée pour tester l'empilement
INTÉGRAL des deux mécanismes tels que committés, sans les modifier.

## Définition (fixée ici)

- Position équity : `pos_eq(t)` = position DÉJÀ COMMITTÉE du #131
  (`results/nonml_weekly_rebalance_dual_engine_pnl.npz`), strictement
  inchangée.
- Rendement obligataire : IDENTIQUE au #134 (DGS10, duration modifiée
  10 ans, formule fermée).
- `r_combiné(t) = pos_eq(t)*r_NDX(t) + (1-pos_eq(t))*r_bond(t)`.
- Coûts : 5 bps par unité de turnover de `pos_eq` (turnover du #131
  déjà réduit, inchangé).
- Fenêtre : intersection #131 (NDX 1988-2026) ∩ DGS10 (1962-2026).
- **Référence** : Buy & Hold 100% NDX, même fenêtre.

## Critère de succès (pré-enregistré, DEUX volets, cohérence avec #131/#134)

1. Critère standard : Sharpe ET rendement net de coûts > BH.
2. Critère Calmar : Calmar > BH.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py
diversification_bond_weekly_rebalance_stack`, n_trials=taille totale du
backlog (jamais 1).

## Anti-cheat

Ce fichier committé avant
`nonml_diversification_bond_weekly_rebalance_stack_backtest.py`,
vérification via `nonml_anti_cheat_check.py
diversification_bond_weekly_rebalance_stack`. Aucune nouvelle donnée
(recalcul sur artefacts déjà committés #131 et DGS10 du #134).
