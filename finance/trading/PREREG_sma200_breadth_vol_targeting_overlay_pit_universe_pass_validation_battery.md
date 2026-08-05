# Pré-enregistrement — Batterie Règle 9 sur le #271 (breadth SMA200, univers point-in-time)

**Committé AVANT tout calcul de la batterie.** Cycle #272 du backlog
non-ML.

## Contexte et motivation

Le #271 (breadth SMA200, univers point-in-time réel, PREREG
`PREREG_sma200_breadth_vol_targeting_overlay_pit_universe.md`) est un
PASS net (Sharpe +0,76→+0,78, robustesse 7/8) qui a survécu à la
correction du survivant — contrairement à la dispersion cross-
sectionnelle (#78/#270, FAIL). Ni le #96 original ni sa version PIT
n'ont jamais été soumis à la barre renforcée.

## Adaptation technique : AUCUNE (réutilisation directe, Règle 7)

Contrairement aux candidats stock-selection (#258/#261/#265/#266), le
#271 est un overlay MONO-ACTIF sur l'indice NDX-100 (position scalaire
0-2x sur un seul actif) — exactement le format attendu par l'outil déjà
figé `scripts/nonml_pass_validation_battery.py` (`pos, r_asset, dates,
cost_bps`). Le backtest du #271 sauvegarde déjà
`results/nonml_sma200_breadth_vol_targeting_overlay_pit_universe_pnl.npz`
dans ce format exact — **aucun script dédié n'est nécessaire**, ce
cycle applique directement l'outil existant, sans aucune modification
de code (Règle 7, réutilisation maximale).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #271.

## Critère de succès (Règle 9, identique aux cycles #111-#271)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=278) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

L'univers PIT (2015-2026, 2896 séances) couvre désormais le krach COVID
(comme découvert aux #268/#269) mais toujours pas dot-com ni 2008 —
aucune garantie que ce contrôle passe. Aucune attente de score
particulier formulée par ailleurs.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #271. Sortie :
`results/nonml_sma200_breadth_vol_targeting_overlay_pit_universe_pass_validation_battery.md`.
