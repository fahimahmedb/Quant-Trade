# Pré-enregistrement — Correction du bug d'exécution « même barre » sur le #53 (jamais audité)

**Committé AVANT tout calcul.** Cycle #255 du backlog non-ML. Suite du
#254 : un troisième portefeuille stock-selection (après Leaders #4 et
Winners #14), Low-Volatility tilt (#15), avec son overlay hiérarchique
#53, jamais inclus dans l'audit "même barre" (#166/#167) ni recorrigé.

## Vérification du bug par lecture directe du code (déclarée avant tout calcul)

`nonml_lowvol_trend_vol_targeting_overlay_backtest.py::main()` : motif
identique à #38/#14/#33/#41/#48/#11/#23 — `weights_lowvol[t:end] = w`
(sélection des titres à plus faible volatilité, décidée avec des données
connues à la clôture de `t`) appliqué DÈS la barre `t`, puis
`pnl_base = (weights_base[start2:] * R[start2:])...` où `R[t]` est le
rendement DÉJÀ RÉALISÉ à la clôture de `t`. Aucun paramètre `causal`
dans le script.

## Méthode (déclarée avant calcul, réutilisation stricte, Règle 7)

Application EXACTE du patch déjà validé au #166/#167/#253/#254
(`lag_one_day(W)`, `causal=True` par défaut sur `weights_base`/
`weights_lev`, `causal=False` conservé pour non-régression). Aucun
paramètre de stratégie ne change.

## Critère de succès (n_trials=1)

Le PASS niveau 1 déjà acquis par #53 (Sharpe ET rendement > référence
Low-Vol 1.0x) survit-il au décalage causal ?

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le signal de sélection (volatilité réalisée sur `LOWVOL_WINDOW`) est
   un filtre plus lent que le ranking momentum direct de #14/#38 —
   comme #33/#41/#48/#23, un résultat qui survit est plausible.
2. Contrairement à #33/#41/#48 (rebalancement 21j) et plus proche de la
   divergence observée entre #11/#23, aucune règle simple ne prédit le
   résultat par analogie — à mesurer directement.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script modifié :
`nonml_lowvol_trend_vol_targeting_overlay_backtest.py` (ajout du
paramètre `causal`, réutilisation stricte, aucun changement de logique
de stratégie). Non-régression vérifiée avant lecture du résultat causal.
