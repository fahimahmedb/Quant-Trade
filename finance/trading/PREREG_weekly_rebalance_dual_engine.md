# Pré-enregistrement — Rebalancement HEBDOMADAIRE du mécanisme #121 (dual-engine)

**Committé AVANT tout calcul.** Cycle #131 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Les meilleurs candidats à ce jour (#115, #121, #124, tous à 3/5 sur la
batterie Règle 9) échouent systématiquement sur le stress de coûts
(volet a) car le rebalancement quotidien génère un turnover élevé.
Hypothèse : passer d'un rebalancement quotidien à un rebalancement
HEBDOMADAIRE sur le mécanisme le plus abouti (#121, moyenne de deux
moteurs de volatilité indépendants) réduit mécaniquement le turnover et
donc la sensibilité aux coûts, au prix d'un délai de réaction plus lent
aux changements de régime de volatilité. Direction choisie AVANT tout
calcul : on s'attend à une amélioration du volet (a) coûts, sans
préjuger de son effet sur les volets (b) crise, (c) stabilité, (d) SPA,
(e) DSR.

## Définition (fixée ici, avant tout résultat)

- Point de départ : la position quotidienne déjà committée du #121
  (`results/nonml_dual_engine_defensive_overlay_pnl.npz`, `pos`, `r_asset`,
  `dates`, `cost_bps` — aucun paramètre des moteurs sous-jacents ne
  change).
- **Rebalancement hebdomadaire** : `REBAL_FREQ = 5` séances (convention
  "semaine boursière" déjà utilisée dans tout le repo, ex. horizon
  triple-barrière Étape B). Aux séances `t = 0, 5, 10, 15, ...`, la
  position prend la valeur DÉJÀ CAUSALE calculée par le #121 à cette
  date (`pos_daily[t]`) ; entre deux rebalancements, la position reste
  figée à sa dernière valeur (pas de recalcul, pas de moyenne — simple
  échantillonnage-et-maintien du signal quotidien déjà validé).
- Turnover recalculé sur la position hebdomadaire résultante (donc
  mécaniquement plus faible que la version quotidienne).
- **Coûts** : 5 bps par unité de turnover (identique).
- **Référence** : Buy & Hold sur NDX, même fenêtre que #121
  (20/09/1988 → 13/07/2026, 9522 séances communes).
- `REBAL_FREQ = 5` n'est PAS tuné après résultat — seule valeur testée
  dans ce cycle (la grille de robustesse ci-dessous, SI PASS, explore
  d'autres fréquences mais ne remplace pas ce choix pré-enregistré).

## Critère de succès (pré-enregistré, DEUX volets rapportés séparément)

1. Critère standard : Sharpe ET rendement net de coûts > BH (n_trials=1
   pour cette construction précise).
2. Critère Calmar (cohérence avec #115/#121) : Calmar > BH.
Les deux sont rapportés, aucun n'est privilégié après coup.

## Batterie de validation renforcée (Règle 9, SI PASS sur au moins un critère)

`scripts/nonml_pass_validation_battery.py weekly_rebalance_dual_engine`,
n_trials=taille totale du backlog (jamais 1).

## Robustesse prévue (SI PASS niveau 1)

Grille non-tunable : `REBAL_FREQ ∈ {3, 5, 10, 15, 20}` séances (autour
du choix hebdomadaire pré-enregistré de 5).

## Anti-cheat

Ce fichier committé avant
`nonml_weekly_rebalance_dual_engine_backtest.py`, vérification via
`nonml_anti_cheat_check.py weekly_rebalance_dual_engine`. Aucune
nouvelle donnée (recalcul sur artefact déjà committé du #121).
