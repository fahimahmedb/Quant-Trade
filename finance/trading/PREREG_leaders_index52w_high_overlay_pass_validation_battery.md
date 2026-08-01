# Pré-enregistrement — Batterie Règle 9 sur le #38 (Leaders 52-semaines + overlay 52w-high indice)

**Committé AVANT tout calcul.** Cycle #161 du backlog non-ML.

## Contexte et motivation

Le #38 (`PREREG_leaders_index52w_high_overlay.md`, `results/nonml_leaders_index52w_high_overlay_result.md`)
reste le **meilleur résultat brut de tout le backlog** (Sharpe +0,78→+1,50,
rendement +81,6%→+508,3%, MDD quasi inchangé -25,7%→-25,9%, plateau de
robustesse parfait sur les deux grilles déjà testées) — mais il a été
committé le 28/07/2026, **avant** l'introduction de la Règle 9 (batterie
de validation renforcée, 29/07/2026). Contrairement aux candidats #111 à
#149, il n'a **jamais été soumis** à cette barre. C'est un vrai trou de
couverture, pas une nouvelle hypothèse spéculative : appliquer un outil
déjà committé et déterministe (`nonml_pass_validation_battery.py`) à un
résultat déjà existant, sans aucun nouveau réglage.

## Différence structurelle à documenter avant calcul

Le #38 est une stratégie de PORTEFEUILLE (poids sur ~100 titres NDX-100),
pas un overlay scalaire sur un seul actif (le format `pos × r_asset`
attendu nativement par `nonml_pass_validation_battery.py`). Pour rester
fidèle au mécanisme exact déjà publié (et éviter toute réimplémentation
divergente, Règle 7), ce cycle **réutilise directement les fonctions déjà
committées** de `nonml_leaders_index52w_high_overlay_backtest.py`
(poids Leaders, poids Leaders+overlay, rendements bruts par titre) via un
refactor NON-COMPORTEMENTAL (extraction d'une fonction `build_weights()`
sans changer un seul calcul — vérifié par diff bit-à-bit du résultat
`nonml_leaders_index52w_high_overlay_result.md` avant/après refactor).

La batterie recalcule alors les 5 contrôles a-e directement sur les PnL
de portefeuille (candidat = Leaders+overlay, référence = Leaders 1.0x —
**même référence que le PREREG original du #38**, PAS Buy&Hold), avec
recalcul du turnover à chaque coût/fenêtre/fold exactement comme le fait
le script générique pour les stratégies scalaires (convention identique :
`prepend` = premier poids de la fenêtre, aucun coût artificiel à
l'entrée d'une sous-fenêtre).

## Univers et période

Identiques au #38 : prix NDX-100 déjà récupérés (`data/pead/prices/`),
signal de tendance sur `data/nasdaq100_daily.txt`. Aucune nouvelle donnée.

## Critère de succès (Règle 9, pré-enregistré, identique aux cycles #111-149)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que la référence (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat la référence en Sharpe.
d. SPA de Hansen à 1 candidat contre la référence (p < 0,05).
e. DSR avec **n_trials = 160** (taille du backlog AVANT ce cycle, lue au
   moment de l'exécution — jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1 (aucune grille testée, application
mécanique d'un outil déjà figé).

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_leaders_index52w_high_overlay_pass_validation_battery.py`.
Vérification via `nonml_anti_cheat_check.py leaders_index52w_high_overlay_pass_validation_battery`.
