# Pré-enregistrement — Batterie Règle 9 sur le #100 (dispersion du momentum)

**Committé AVANT tout calcul.** Cycle #318 du backlog non-ML.

## Contexte et motivation

Le #100 (dispersion cross-sectionnelle des scores de momentum 12-1
mois comme porte du mécanisme hiérarchique vol-targeting, PASS,
plateau parfait 8/8) n'a **jamais** été soumis à la batterie de
validation renforcée (Règle 9). Même famille mono-actif à signal
title-par-titre que le #99 (concentration HHI, 2/5, cycle #317) —
teste si le profil observé au #99 (crise et stabilité tiennent malgré
l'historique de construction court, coûts/SPA/DSR échouent) se
confirme sur un 2e candidat de cette famille (2/2) ou si le #99 était
un cas isolé.

## Adaptation technique

Comme pour le #99 (#317), le script
`nonml_momentum_dispersion_vol_targeting_overlay_backtest.py` d'origine
ne sauvegarde pas le couple `(pos, r_asset)`. **Correction nécessaire,
déclarée ici avant tout calcul** : ajout d'une sauvegarde `.npz` — AUCUNE
modification de la logique de calcul. Résultat re-exécuté et comparé
(byte-identique attendu) avant tout commit (Règle 4).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #100.

## Critère de succès (Règle 9, identique aux cycles #111-#317)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : étant
donné la proximité structurelle avec le #99 (même mécanisme
hiérarchique vol-targeting, même contrainte d'historique title-par-
titre 2021-2026, plateau de robustesse niveau 1 encore meilleur — 8/8
parfait contre 6/8 pour le #99), un score similaire (2/5, crise et
stabilité OK, coûts/SPA/DSR en échec) est plausible. Si le résultat
diverge notablement, ce sera informatif sur les limites de la
généralisation même au sein de cette famille. Rapporté honnêtement
dans les deux cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #100. Sortie :
`results/nonml_momentum_dispersion_vol_targeting_overlay_pass_validation_battery.md`.
