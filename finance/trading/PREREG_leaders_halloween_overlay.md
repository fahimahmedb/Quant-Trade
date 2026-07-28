# Pré-enregistrement — Leaders 52-semaines + overlay levé Halloween

**Committé AVANT tout calcul.** Cycle #20 du backlog non-ML. 5e variante
de combinaison avec le cycle #4 (après ToM/#11=PASS, vol-calme/#9=FAIL,
accélération/#16=FAIL) — cette fois avec le déclencheur Halloween
(nov-avril, validé au cycle #17 sur Buy&Hold).

## Hypothèse

Le déclencheur calendaire Halloween (validé au cycle #17 sur Buy&Hold,
4/5 marchés) appliqué au portefeuille "leaders" 52-semaines (#4)
améliore-t-il encore le résultat, comme l'a fait le déclencheur ToM au
cycle #11 ?

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = EXACTEMENT le portefeuille "leaders" du cycle #4
  (tercile supérieur par ratio prix/plus-haut-52sem, NDX-100,
  rebalancement 21j, aucun paramètre changé).
- Exposition = **1.0x en permanence**, SAUF de **novembre à avril**
  (définition identique au cycle #17) où exposition = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel du
  portefeuille leaders + transitions d'exposition saisonnière).
- **Référence** : le portefeuille "leaders" lui-même à 1.0x (résultat du
  cycle #4), comme pour les cycles #11/#16 — pas Buy&Hold classique.

## Univers et période

Identique aux cycles #4/#11/#16 : NDX-100 (99 tickers,
`data/pead/prices/`), 2022-2026.

## Critère de succès RENFORCÉ (pré-enregistré)

La version levée doit battre le portefeuille leaders 1.0x (référence)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2.0 cohérent avec tous les cycles
précédents, pas choisi après résultat).

## Anti-cheat

Ce fichier committé avant `nonml_leaders_halloween_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py leaders_halloween_overlay`.
