# Pré-enregistrement — Correction du bug d'exécution « même barre » sur les #11/#23 (jamais audités)

**Committé AVANT tout calcul.** Cycle #254 du backlog non-ML. Suite
directe du #253 : deux autres candidats bâtis sur le portefeuille
Leaders (#4) — #11 (overlay ToM) et #23 (overlay union ToM∪Halloween) —
identifiés comme jamais inclus dans l'audit "même barre" (#166/#167) ni
recorrigés, contrairement à #39/#42/#51/#82/#86.

## Vérification du bug par lecture directe du code (déclarée avant tout calcul)

`nonml_leaders_tom_overlay_backtest.py` (#11) et
`nonml_leaders_tom_halloween_union_overlay_backtest.py` (#23) :
motif identique déjà documenté et corrigé pour #38/#14/#33/#41/#48 —
`weights_leaders[t:end] = w` (ligne 88/94) appliqué DÈS la barre `t`,
suivi de `pnl_base = (weights_base[start:] * R[start:])...` (ligne
97-98/103-104) où `R[t]` est le rendement DÉJÀ RÉALISÉ à la clôture de
`t`. Ni l'un ni l'autre script n'a de paramètre `causal`.

## Méthode (déclarée avant calcul, réutilisation stricte, Règle 7)

Application EXACTE du patch déjà validé au #166/#167 et réappliqué au
#253 (`lag_one_day(W)`, `causal=True` par défaut sur `weights_base`/
`weights_lev`, `causal=False` conservé pour non-régression). Aucun
paramètre de stratégie ne change.

## Critère de succès (n_trials=1 par candidat, 2 candidats)

Le PASS niveau 1 déjà acquis par #11 et #23 (Sharpe ET rendement >
référence Leaders 1.0x) survit-il au décalage causal ?

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour #33/#41/#48 (survivent) plutôt que #14/#38 (effondrement),
   le signal calendaire (ToM/Halloween) ne dépend PAS du rendement du
   jour t lui-même (contrairement au ranking momentum de #14/#38) — un
   résultat qui survit à la correction, comme #33/#41/#48, est donc le
   scénario le plus probable.
2. La marge pourrait néanmoins se réduire significativement, comme
   observé pour #33/#41/#48 (Sharpe divisé par ~3 dans certains cas).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts modifiés :
`nonml_leaders_tom_overlay_backtest.py`,
`nonml_leaders_tom_halloween_union_overlay_backtest.py` (ajout du
paramètre `causal`, réutilisation stricte, aucun changement de logique
de stratégie). Non-régression vérifiée pour chacun avant lecture du
résultat causal.
