# Pré-enregistrement — Overlay de tendance par la longueur de série directionnelle

**Committé AVANT tout calcul.** Cycle #108 du backlog non-ML.

## Hypothèse

Le #95 (autocorrélation lag-1 continue, FAIL) mesure la persistance
directionnelle de façon CONTINUE sur une fenêtre glissante longue
(60j). Ce cycle teste une mesure DISCRÈTE et à très court terme : la
longueur de la série ("streak") de jours consécutifs dans le même
sens. Un streak haussier suffisamment long pourrait signaler une
dynamique de continuation exploitable, distincte de l'estimateur
continu du #95 et des chocs ponctuels déjà testés (#13/#22/#24).

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #3/#9/#29/#95.
- Direction quotidienne : `up(t) = close(t) > close(t-1)`.
- Streak(t) = longueur de la série de jours consécutifs (y compris t)
  dans la MÊME direction que le jour t (compteur qui repart à 1 à
  chaque changement de direction, incrémente sinon).
- Porte active si Streak(t-1) ≥ `STREAK_THRESHOLD=3` séances
  consécutives à la HAUSSE (ordre de grandeur des fenêtres courtes déjà
  utilisées pour les chocs de prix #13/#22 dans ce backlog, fixé ici
  a priori, pas une grille testée).
- Position : **CAP=2.0x** les jours de porte active, **1.0x** sinon
  (mécanisme binaire simple, identique au #9/#31/#87/#92/#93/#95/#107).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #3/#9/#29/#95). n_trials=1
(STREAK_THRESHOLD=3j fixé ici a priori, CAP=2.0x identique à la
famille, aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant `nonml_streak_length_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py streak_length_overlay`.
