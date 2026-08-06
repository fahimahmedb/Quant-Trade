# Pré-enregistrement — Batterie Règle 9 sur le #274 (breadth de momentum, univers point-in-time)

**Committé AVANT tout calcul de la batterie.** Cycle #275 du backlog
non-ML.

## Contexte et motivation

Le #274 (breadth de momentum, univers point-in-time réel, PREREG
`PREREG_momentum_breadth_vol_targeting_overlay_pit_universe.md`) est un
PASS net (Sharpe +0,76→+0,79, robustesse 7/8) qui a confirmé
l'hypothèse vitesse-du-signal (survit au PIT, comme le #96). Explicitement
noté au #274 comme « à faire séparément si repris » — ce cycle comble
cette lacune, complétant la couverture Règle 9 des deux signaux LENTS
validés sous PIT (#96/#272 déjà fait, #94/ce cycle).

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Identique au #271→#272 : le #274 est un overlay MONO-ACTIF sur l'indice
NDX-100 — le `.npz` déjà sauvegardé par son backtest
(`results/nonml_momentum_breadth_vol_targeting_overlay_pit_universe_pnl.npz`)
correspond exactement au format attendu par l'outil déjà figé
`scripts/nonml_pass_validation_battery.py`. Aucun script dédié
nécessaire, aucune modification de code.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #274.

## Critère de succès (Règle 9, identique aux cycles #111-#274)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=281) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Par précédent direct (#272, breadth SMA200 PIT : 2/5, crise et SPA OK,
coûts et stabilité et DSR en échec), un score similaire est plausible
mais non garanti — rapporté tel quel.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #274. Sortie :
`results/nonml_momentum_breadth_vol_targeting_overlay_pit_universe_pass_validation_battery.md`.
