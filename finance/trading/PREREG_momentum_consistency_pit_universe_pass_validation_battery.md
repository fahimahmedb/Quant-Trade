# Pré-enregistrement — Batterie Règle 9 sur le #266 (momentum de constance, univers point-in-time)

**Committé AVANT tout calcul de la batterie.** Cycle #269 du backlog
non-ML.

## Contexte et motivation

Le #266 (momentum de constance, univers point-in-time réel, PREREG
`PREREG_momentum_consistency_pit_universe.md`) est un PASS net (Sharpe
+0,39→+0,45, robustesse 5/5 plateau parfait — la meilleure robustesse
du trio momentum PIT) qui a survécu à la correction du survivant.
Jamais soumis à la barre renforcée. Complète la couverture Règle 9 du
trio momentum PIT : #4/#38 (Règle 9 déjà appliquée historiquement,
#161/#163, aujourd'hui 1/5 et 0/5 après correction du #260), #73/#265
(2/5, cycle #268), #82/#266 (ce cycle).

## Adaptation technique (réutilisation stricte, Règle 7)

Identique aux #259/#262/#268 : le #266 est une stratégie de PORTEFEUILLE
— réutilise STRICTEMENT le patron déjà écrit et validé au #259, seule
la reconstruction des séries change (momentum de constance univers PIT
vs Buy&Hold équipondéré univers PIT).

## Référence

Buy&Hold équipondéré de l'univers PIT réel — identique à la référence
déjà utilisée dans le backtest du #266.

## Critère de succès (Règle 9, identique aux cycles #111-#268)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=275) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Le #268 (momentum 12-1 PIT, robustesse 4/5) a obtenu 2/5 à cette
batterie — la crise (fenêtre COVID désormais couverte par l'historique
PIT 2015-2026) y a échoué contrairement à l'attente initiale. Le #266 a
une robustesse supérieure (5/5 plateau parfait) mais aucune garantie
que cela se traduise par un meilleur score Règle 9 — rapporté tel quel.
Ce cycle complète la couverture Règle 9 du trio et n'est PAS le début
d'une recherche systématique sur d'autres combinaisons.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #266. Sortie :
`results/nonml_momentum_consistency_pit_universe_pass_validation_battery.md`.
