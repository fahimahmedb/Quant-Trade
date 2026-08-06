# Pré-enregistrement — Batterie Règle 9 sur le #48 (vol-targeting 20% + portefeuille Leaders)

**Committé AVANT tout calcul.** Cycle #316 du backlog non-ML.

## Contexte et motivation

Le #48 (vol-targeting continu cible 20% sur le portefeuille Leaders
52-semaines, PASS, déjà confirmé causal au #253) n'a **jamais** été
soumis à la batterie de validation renforcée (Règle 9). 5e candidat de
la revue de conformité initiée au #312. Ce cycle teste si le profil
faible du #33 (1/5, cycle #315 — SMA200 + Leaders, mécanisme CAP
binaire) est spécifique à ce mécanisme précis ou s'il s'agit d'un
effet de l'univers stock-picking court (2021-2026) lui-même : le #48
partage exactement le même univers de titres et la même référence
(Leaders 1.0x) que le #33, mais avec un mécanisme d'exposition
CONTINU (vol-targeting, cible 20%) au lieu d'un CAP binaire sur seuil
SMA200.

## Adaptation technique (Règle 7)

Identique au #33 (#315) : script dédié réutilisant STRICTEMENT le
patron déjà établi au #259/#315 (portefeuille multi-actifs, mêmes 5
fonctions de contrôle importées directement, aucune logique dupliquée)
— seule la construction du signal `weights_lev` change (vol-targeting
continu au lieu de la porte SMA200 binaire), en réutilisant
`vol_target_exposure()` et `lag_one_day()` du #48.

## Référence

Portefeuille Leaders 1.0x (cycle #4) — identique à la référence déjà
utilisée dans le backtest d'origine du #48, PAS Buy&Hold.

## Critère de succès (Règle 9, identique aux cycles #111-#315)

Les 5 contrôles (coûts ×3/×5, crise, stabilité temporelle 4 folds +
embargo 5j, SPA, DSR à n_trials mis à jour) doivent TOUS passer pour un
PASS RENFORCÉ. Sinon, le score partiel (X/5) est rapporté tel quel,
sans retuning.

## Risque déclaré à l'avance

**Prédiction explicite** (déclarée avant calcul, testable) : étant
donné que le #48 partage EXACTEMENT le même univers de titres, la
même fenêtre temporelle (2021-2026, ~5 ans) et la même référence que
le #33, un score globalement FAIBLE et une fenêtre de crise limitée
(seul le resserrement 2022 couvert) sont attendus pour la MÊME raison
structurelle (historique court) — indépendamment du mécanisme
d'exposition (continu vs binaire). Si le score diverge notablement du
#33 (1/5), ce sera la preuve que le mécanisme d'exposition compte
davantage que l'univers/historique — rapporté honnêtement dans les
deux cas.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage du #48. Sortie :
`results/nonml_leaders_vol_targeting_20_overlay_pass_validation_battery.md`.
