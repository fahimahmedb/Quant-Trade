# Pré-enregistrement — Re-lecture Sortino de la stabilité temporelle du #121

**Committé AVANT tout calcul.** Cycle #129 du backlog non-ML. Analyse
méthodologique sur le pnl DÉJÀ committé du #121 (meilleur candidat),
pas un nouveau backtest.

## Question posée (fixée ici, avant tout calcul)

Le #121 est un overlay défensif dont l'edge est concentré en période de
crise (profil de couverture déjà établi au #117 : ratio gain-crise/
coût-calme). Le Sharpe pénalise TOUTE volatilité (haussière et
baissière) ; le Sortino (déjà calculé par `trading_metrics()` sous
`sortino_ann`, jamais utilisé comme critère de lecture dans ce backlog)
ne pénalise que la volatilité À LA BAISSE — plus cohérent avec un
mécanisme qui vise explicitement à réduire les pertes, pas la
variance totale. Hypothèse : la stabilité temporelle du #121 (Règle 9c,
3/4 folds sous Sharpe) et le comportement en crise sont-ils LUS
différemment sous Sortino ?

## Méthode (fixée ici)

Sur le pnl déjà committé du #121
(`nonml_dual_engine_defensive_overlay_pnl.npz`) :
1. Recalcule les 4 folds de la Règle 9c (mêmes découpages exacts,
   embargo 5j) en comparant Sortino_overlay vs Sortino_BH au lieu de
   Sharpe_overlay vs Sharpe_BH.
2. Recalcule les 4 fenêtres de crise de la Règle 9b en comparant
   Sortino au lieu de MDD (MDD reste la métrique officielle du stress
   de crise — le Sortino est une lecture COMPLÉMENTAIRE, pas un
   remplacement).
3. Compare le nombre de folds/fenêtres favorables sous Sharpe vs sous
   Sortino.

## Ce que cette analyse NE fait PAS

Ne change PAS le verdict Règle 9 officiel du #121 (basé sur Sharpe/MDD/
SPA/DSR, déjà tranché : FAIL). N'invente pas un nouveau seuil de succès
Sortino après avoir vu le résultat. Documente une lecture alternative,
utile pour juger si le Sharpe est la métrique la plus adaptée à ce
type de mécanisme (question déjà effleurée au #117), sans rouvrir le
verdict.

## Anti-cheat

Analyse committée en un seul passage, sans itération sur le résultat.
