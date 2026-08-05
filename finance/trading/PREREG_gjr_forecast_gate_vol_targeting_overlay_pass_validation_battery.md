# Pré-enregistrement — Batterie Règle 9 sur le #234 (porte GJR-t walk-forward sur le mécanisme #46)

**Committé AVANT tout calcul de la batterie.** Cycle #235 du backlog
non-ML. Backlog "à faire" épuisé après le #234. Le #234 est un PASS
niveau 1 frais (marché unique NDX) jamais soumis à cette barre — continue
la même discipline de validation systématique appliquée à chaque nouvelle
hypothèse PASS de la lignée mécanique (#207-#214, #224-#230, #232).

## Contexte et motivation

Le #234 (`PREREG_gjr_forecast_gate_vol_targeting_overlay.md`,
`results/nonml_gjr_forecast_gate_vol_targeting_overlay_result.md`)
réutilise `overlay.py::walk_forward_vol_forecast` (GJR-t, Étape C) comme
PORTE (pas comme estimateur, distinct du #165) du mécanisme #46 standard.
PASS niveau 1 sur NDX, mais marge de Sharpe la plus faible de toute la
lignée de portes (+0,00089), et robustesse fragile sur l'axe fenêtre de
vol réalisée (1/4, seul le point pré-enregistré 20j passe) — signaux qui
suggèrent un edge probablement trop marginal pour survenir à la Règle 9,
mais déclarés à l'avance ici plutôt que jugés a posteriori.

## Marché de référence pour la batterie

NDX (40 ans) uniquement — c'est le seul marché testé au #234 (le GJR-t
n'est validé au SPA qu'sur ce marché à l'Étape C), cohérent avec la
pratique déjà établie pour le #165 (`volatility_managed_portfolio_gjr`).

## Modification technique requise (déclarée avant calcul)

`nonml_gjr_forecast_gate_vol_targeting_overlay_backtest.py` sera étendu
pour sauvegarder `results/nonml_gjr_forecast_gate_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur NDX, sans aucun changement de logique
de calcul — vérifié par re-exécution identique du résultat déjà committé
(mêmes Sharpe/rendement/MDD que le #234).

## Critère de succès (Règle 9, identique aux cycles #111-#232)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (235, jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La marge de Sharpe du #234 (+0,00089) est la plus petite de toute la
   lignée de portes testées — un edge journalier moyen probablement très
   proche de zéro, cohérent avec un échec attendu du SPA (comme le #231
   à p=0,2568, ou le #165 lui-même à p=1,0000 pour le même signal GJR-t
   utilisé en estimateur).
2. Le MDD est identique aux deux jambes au #234 (-82,9%) — le contrôle de
   crise (b) pourrait échouer de justesse si l'overlay n'apporte aucune
   protection mesurable sur les fenêtres de crise spécifiques, contrairement
   aux autres portes de la lignée qui améliorent souvent le MDD.
3. Le DSR est hors de portée pour les 235 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_gjr_forecast_gate_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
gjr_forecast_gate_vol_targeting_overlay_pass_validation_battery`.
