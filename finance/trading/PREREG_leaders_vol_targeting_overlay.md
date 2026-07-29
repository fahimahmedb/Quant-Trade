# Pré-enregistrement — Leaders 52-semaines + overlay de vol-targeting continu

**Committé AVANT tout calcul.** Cycle #45 du backlog non-ML. Applique le
mécanisme de vol-targeting continu du #43 (FAIL sur Buy&Hold, critère
renforcé non atteint sur le rendement) au portefeuille Leaders (#4, edge
positif documenté) plutôt qu'à un indice sans edge propre — teste si
scaler l'exposition d'un portefeuille qui bat déjà Buy&Hold change la
conclusion.

## Hypothèse

Le #43 a échoué à battre Buy&Hold en rendement car la position moyenne
du vol-targeting descend souvent sous 1.0x, ce qui pénalise un actif
sans edge propre (l'indice). Appliqué à un portefeuille qui a DÉJÀ un
edge de rendement documenté (Leaders, #4), le même mécanisme de
réduction du risque pourrait préserver suffisamment de rendement pour
battre la référence Leaders 1.0x tout en réduisant son MDD.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = Leaders 52-semaines, IDENTIQUE au cycle #4
  (tercile supérieur par ratio prix/plus-haut-annuel, rebalancement
  21j, univers NDX-100 dynamique).
- Vol réalisée = écart-type des rendements log QUOTIDIENS DU
  PORTEFEUILLE LEADERS lui-même (pas de l'indice), fenêtre roulante de
  **20 séances**, annualisée (× √252), calcul causal (vol connue à
  t-1, position décidée pour t) — même mécanisme que le #43, appliqué
  au portefeuille plutôt qu'à l'indice.
- Vol cible = **15% annualisé**, identique au #43.
- Exposition globale(t) = **clip(vol_cible / vol_réalisée_leaders(t-1),
  0.0, CAP=2.0)**, appliquée comme multiplicateur sur les poids du
  portefeuille Leaders (poids_finaux = poids_leaders × exposition).
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel ET
  changements quotidiens de l'exposition).
- **Référence** : portefeuille Leaders 1.0x (cycle #4), PAS Buy&Hold —
  même convention que #11/#23/#33/#38/#39/#42.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille Leaders de référence
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (vol cible 15%, fenêtre 20j et CAP=2.0x
identiques au #43, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_leaders_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py leaders_vol_targeting_overlay`.
