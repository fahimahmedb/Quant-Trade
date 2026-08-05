# Pré-enregistrement — Batterie Règle 9 sur le #265 (momentum 12-1, univers point-in-time)

**Committé AVANT tout calcul de la batterie.** Cycle #268 du backlog
non-ML.

## Contexte et motivation

Le #265 (momentum 12-1, univers point-in-time réel, PREREG
`PREREG_momentum_12_1_pit_universe.md`) est un PASS net (Sharpe
+0,39→+0,44, robustesse 4/5) qui a survécu à la correction du
survivant — contrairement aux candidats volume (#258/#261). Jamais
soumis à la barre renforcée. Le #73 (spécification originale, univers
2026) n'a lui non plus jamais été soumis à cette barre — ce cycle
comble les deux lacunes en une seule batterie sur la version PIT, la
plus rigoureuse des deux.

## Adaptation technique (réutilisation stricte, Règle 7)

Comme pour #258→#259 et #261→#262, le #265 est une stratégie de
PORTEFEUILLE (poids sur un tercile de titres), pas un overlay
mono-actif — le format `.npz` de `nonml_pass_validation_battery.py` ne
s'applique pas. Ce cycle réutilise STRICTEMENT le patron déjà écrit et
validé au #259
(`nonml_momentum_turnover_doublesort_pass_validation_battery.py`,
fonctions `check_a_cost_stress`/`check_b_crisis_stress`/
`check_c_temporal_stability`/`check_d_spa`/`check_e_dsr`, génériques sur
des paires rendement-brut/turnover) — seule la reconstruction des
séries change (momentum 12-1 univers PIT vs Buy&Hold équipondéré univers
PIT, au lieu du double-tri momentum+turnover univers 2026).

## Référence

Buy&Hold équipondéré de l'univers PIT réel — identique à la référence
déjà utilisée dans le backtest du #265.

## Fenêtre de crise (différence attendue par rapport à #259/#262)

Contrairement aux candidats volume (univers 2021-2027, seule la fenêtre
« resserrement 2022 » couverte), l'univers PIT du #265 remonte à 2015 —
toujours pas assez pour dot-com (2000-2002) ou 2008, mais **le
resserrement 2022 reste la seule fenêtre couverte** (2015-2026 ne
couvre ni dot-com ni 2008). Déclaré à l'avance pour ne pas être surpris
par un contrôle PENDING.

## Critère de succès (Règle 9, identique aux cycles #111-#262)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials=274) doivent TOUS passer pour un PASS
RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel, sans
retuning.

## Risque déclaré à l'avance

Aucune attente de score particulier — le #265 a un Sharpe/rendement
plus modeste que le #258 original (avant sa propre correction) et
l'échantillon plus long (2015-2026 vs 2021-2027) pourrait jouer dans un
sens ou dans l'autre sur la stabilité temporelle et le SPA.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #265. Sortie :
`results/nonml_momentum_12_1_pit_universe_pass_validation_battery.md`.
