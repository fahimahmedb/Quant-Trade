# Pré-enregistrement — Correction du bug d'exécution « même barre » sur les #33/#41/#48 (jamais audités pour ce bug)

**Committé AVANT tout calcul.** Cycle #253 du backlog non-ML. Suite
directe du #252 : le bug d'exécution "même barre" (#166/#167,
`results/nonml_same_bar_execution_audit.md`) n'a documenté et corrigé
QUE les cycles #38 et #14 (sections A et B de l'audit). Les cycles
#33/#41/#48 — tous construits sur le MÊME portefeuille Leaders (#4) avec
un overlay différent (SMA200 pour #33, union SMA200∪52w-high pour #41,
vol-targeting 20% pour #48) — n'ont **jamais été inclus** dans cet audit
ni recorrigés, contrairement à #39/#42/#51/#82/#86 qui l'ont été le
01/08/2026 (cf. section "Backlog #166").

## Vérification du bug par lecture directe du code (déclarée avant tout calcul)

Inspection de `nonml_sma200_leaders_overlay_backtest.py::main()` (#33) :
même motif EXACT que documenté pour #38/#14 dans
`nonml_same_bar_execution_audit.md` — `ratio[t]` calculé avec `close[t]`,
`weights_leaders[t:end] = w` appliqué DÈS la barre `t`, puis
`pnl = (weights[start:] * R[start:]).sum(...)` où `R[t] =
log(close[t]/close[t-1])` est le rendement DÉJÀ RÉALISÉ à la clôture de
`t`. Inspection de `nonml_leaders_trend_union_overlay_backtest.py`
(#41) et `nonml_leaders_vol_targeting_20_overlay_backtest.py` (#48) :
motif identique (`weights_leaders[t:end] = w` ligne 98/94, suivi de
`pnl_base = (weights_base[start:] * R[start:])...` ligne 108-109/103-104
respectivement). Les trois scripts partagent donc le même défaut,
jamais corrigé.

## Méthode (déclarée avant calcul, réutilisation stricte, Règle 7)

Application EXACTE du patch déjà validé au #166/#167
(`bd5ef75`, `nonml_leaders_index52w_high_overlay_backtest.py`) aux trois
scripts #33/#41/#48 : ajout d'une fonction `lag_one_day(W)` (décale la
matrice de poids d'un jour, `out[1:] = W[:-1]`) et d'un paramètre
`causal=True` par défaut, appliqué à `weights_base`/`weights_lev` juste
après leur construction ; `causal=False` conservé pour reproduire
bit-identique le résultat déjà committé (non-régression). Aucun
paramètre de stratégie (LOOKBACK, REBAL_EVERY, TERCILE, CAP, coût) ne
change.

## Critère de succès (n_trials=1 par candidat, 3 candidats)

Pour chacun des trois : le PASS niveau 1 déjà acquis (Sharpe ET
rendement > référence Leaders 1.0x) survit-il au décalage causal ?

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le précédent #38/#14 (effondrement quasi total du Sharpe candidat) et
   le mécanisme partagé (même fonction `weights_leaders`, même
   dépendance au rendement du jour t dans le signal — SMA200/52w-
   high/vol-targeting utilisent tous `close[t]` dans leur calcul) rendent
   un effondrement similaire pour #33/#41/#48 le scénario le plus
   probable.
2. Contrairement à #14/#38 dont le signal dépend DIRECTEMENT du
   rendement du jour t, l'overlay de #33/#48 (SMA200, vol-targeting) est
   un filtre plus LENT — la fuite pourrait être moins dommageable si
   l'essentiel de l'edge vient de la sélection Leaders elle-même
   (rebalancée tous les 21j, donc fuite sur ~5% des séances seulement,
   comme documenté pour #38) plutôt que du timing fin de l'overlay.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Scripts modifiés :
`nonml_sma200_leaders_overlay_backtest.py`,
`nonml_leaders_trend_union_overlay_backtest.py`,
`nonml_leaders_vol_targeting_20_overlay_backtest.py` (ajout du paramètre
`causal`, réutilisation stricte du patch #166/#167, aucun changement de
logique de stratégie). Non-régression vérifiée pour chacun avant lecture
du résultat causal.
