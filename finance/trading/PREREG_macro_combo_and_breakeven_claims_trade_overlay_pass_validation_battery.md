# Pré-enregistrement — Batterie Règle 9 sur le #335 (combinaison ET breakeven+CCSA+trade)

**Committé AVANT tout calcul.** Cycle #334 du backlog non-ML.

## Contexte et motivation

Le #335 (combinaison ET de 3 signaux macro-externes : breakeven
inflation #200, demandes continues de chômage #322, balance
commerciale #327 — PASS niveau 1, 4/5 marchés, robustesse plateau
parfait 12/15) n'a **jamais** été soumis à la batterie de validation
renforcée (Règle 9). Suite directe et naturelle du cycle précédent,
dans la continuité de la pratique déjà établie (#200 PASS suivi
immédiatement de sa propre batterie au #201).

## Adaptation technique

Le script `nonml_macro_combo_and_breakeven_claims_trade_overlay_backtest.py`
sauvegarde déjà le couple `(pos, r_asset, dates, cost_bps)` au format
attendu par le script générique `nonml_pass_validation_battery.py`
(convention `.npz`, marché de référence NDX, comme tous les cycles
récents) — **aucune modification nécessaire**, contrairement aux
cycles où une sauvegarde rétroactive était requise.

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #335.

## Critère de succès (Règle 9, identique aux cycles #111-#333)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : le
candidat réutilise directement la porte du #200 (déjà passée en Règle
9 au #201 avec le meilleur score de la famille macro-externe à
l'époque, 3/5 : coûts/crise/stabilité OK, SPA/DSR en échec), combinée
en ET avec 2 signaux supplémentaires qui RÉDUISENT le taux
d'activation (6-11% contre 24% environ pour le #200 seul). Une porte
moins souvent active tend à réduire le nombre d'observations
exploitables pour les tests SPA/DSR (perte de puissance statistique),
ce qui pourrait soit améliorer la stabilité/les coûts (moins de
turnover), soit dégrader le SPA/DSR par manque d'échantillon — un
score proche ou légèrement inférieur au 3/5 du #200/#201 est
plausible. Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #335. Sortie :
`results/nonml_macro_combo_and_breakeven_claims_trade_overlay_pass_validation_battery.md`.
