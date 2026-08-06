# Pré-enregistrement — Batterie Règle 9 sur le #104 (position dans le range annuel)

**Committé AVANT tout calcul.** Cycle #319 du backlog non-ML.

## Contexte et motivation

Le #104 (position moyenne cross-sectionnelle dans le range annuel
NDX-100 comme porte du mécanisme hiérarchique vol-targeting, PASS,
robustesse 7/8, "10e type de porte") n'a **jamais** été soumis à la
batterie de validation renforcée (Règle 9) — jamais couvert par le
balayage systématique des 7 dérivés du #46 (#207-214, qui s'arrêtait
au 7e type de porte) ni par les cycles récents. 3e candidat de la même
famille mono-actif à signal title-par-titre que #99 (2/5) et #100
(3/5) — teste si le motif observé sur ces deux cas (crise et
stabilité tiennent systématiquement, malgré l'historique de
construction du signal limité à 2021-2026) se confirme sur un 3e cas
(3/3) ou si un contre-exemple apparaît.

## Adaptation technique

Comme pour le #99/#100, le script
`nonml_range_position_vol_targeting_overlay_backtest.py` d'origine ne
sauvegarde pas le couple `(pos, r_asset)`. **Correction nécessaire,
déclarée ici avant tout calcul** : ajout d'une sauvegarde `.npz` — AUCUNE
modification de la logique de calcul. Résultat re-exécuté et comparé
(byte-identique attendu) avant tout commit (Règle 4).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #104.

## Critère de succès (Règle 9, identique aux cycles #111-#318)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : étant
donné la proximité structurelle avec #99/#100 (même mécanisme
hiérarchique, même contrainte d'historique title-par-titre, robustesse
niveau 1 intermédiaire — 7/8, entre le 6/8 du #99 et le 8/8 du #100),
un score intermédiaire (2-3/5, crise et stabilité OK, coûts/SPA/DSR
en échec ou proches) est plausible, avec le score exact peut-être
corrélé au niveau de robustesse (comme observé au #100 vs #99).
Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #104. Sortie :
`results/nonml_range_position_vol_targeting_overlay_pass_validation_battery.md`.
