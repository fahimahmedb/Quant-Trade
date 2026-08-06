# Pré-enregistrement — Batterie Règle 9 sur le #99 (concentration de marché HHI)

**Committé AVANT tout calcul.** Cycle #317 du backlog non-ML.

## Contexte et motivation

Le #99 (indice de Herfindahl-Hirschman des contributions au rendement
NDX-100 comme porte du mécanisme hiérarchique vol-targeting, PASS,
robustesse partielle 6/8) n'a **jamais** été soumis à la batterie de
validation renforcée (Règle 9). Identifié lors d'une vérification de
conformité élargie (au-delà de la liste initiale du #312) : la lignée
complète des estimateurs de volatilité (#215-223, #231) est déjà
intégralement couverte (cycles #224-232), de même que les breadth
PIT-corrigées (#94/#96/#272/#274) — le #99 est un candidat MONO-ACTIF
(overlay sur l'indice NDX-100 seul, PAS un portefeuille multi-titres
comme #33/#48) distinct des deux motifs déjà établis par la revue de
conformité (#312-316) : indice pur amplificateur (3/5 systématique) et
portefeuille stock-picking court (1/5 systématique).

## Adaptation technique

Comme pour le #29/#59/#66, le script
`nonml_market_concentration_vol_targeting_overlay_backtest.py`
d'origine ne sauvegarde pas le couple `(pos, r_asset)`. **Correction
nécessaire, déclarée ici avant tout calcul** : ajout d'une sauvegarde
`.npz` à la fin du script — AUCUNE modification de la logique de
calcul. Résultat re-exécuté et comparé (byte-identique attendu) avant
tout commit (Règle 4).

## Référence

Buy&Hold NDX-100 — identique à la référence déjà utilisée dans le
backtest du #99.

## Critère de succès (Règle 9, identique aux cycles #111-#316)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

Le #99 est construit sur le même mécanisme hiérarchique vol-targeting
que la famille d'estimateurs #46/#78/#90/#94 déjà couverte en partie
(#46 lui-même a obtenu 3/5, stabilité parfaite 4/4). Le signal sous-
jacent (concentration HHI) est calculé à partir de données title-par-
titre (2021-2026), limitant l'échantillon testable (contrairement à
l'estimateur de volatilité pur qui peut remonter à 40 ans sur
l'indice) — un profil de stabilité fragile est donc possible malgré
le caractère mono-actif de l'overlay final, pour une raison
DIFFÉRENTE de celle du #33/#48 (ici c'est la CONSTRUCTION DU SIGNAL,
pas le portefeuille lui-même, qui est limitée en historique).
Robustesse niveau 1 déjà partielle (6/8, pas un plateau parfait) —
signal potentiellement fragile. Rapporté honnêtement, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie et
avant toute modification du script de backtest. Aucune nouvelle
donnée, aucun nouveau réglage du #99. Sortie :
`results/nonml_market_concentration_vol_targeting_overlay_pass_validation_battery.md`.
