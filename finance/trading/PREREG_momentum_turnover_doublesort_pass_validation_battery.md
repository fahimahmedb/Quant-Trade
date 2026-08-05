# Pré-enregistrement — Batterie Règle 9 sur le #258 (momentum turnover double-tri)

**Committé AVANT tout calcul de la batterie.** Cycle #259 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#238/
#241/#243 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #258 (`PREREG_momentum_turnover_doublesort.md`,
`results/nonml_momentum_turnover_doublesort_result.md`) est le PASS le
plus net obtenu récemment (Sharpe +0,66→+1,04, MDD amélioré -31,8%→
-26,0%, robustesse 5/5 plateau parfait) et le premier PASS basé sur une
catégorie de données réellement nouvelle (volume/turnover) dans ce
backlog. Jamais soumis à la barre renforcée.

## Adaptation technique nécessaire (déclarée avant tout calcul)

`scripts/nonml_pass_validation_battery.py` (5 contrôles a-e) a été conçu
et utilisé jusqu'ici EXCLUSIVEMENT pour la famille des overlays
vol-targeting mono-actif (une exposition scalaire `pos` sur un seul
rendement d'indice `r`, cf. `pnl_at_cost(pos, r, cost_bps)`). Le #258 est
une stratégie de sélection de PORTEFEUILLE (poids répartis sur ~11
titres parmi 99, rebalancés mensuellement) — le format `.npz`
(pos, r_asset, dates, cost_bps) ne s'applique pas tel quel.

**Décision prise AVANT tout calcul** : plutôt que de forcer une
abstraction artificielle "position scalaire équivalente", ce cycle écrit
un script de batterie DÉDIÉ
(`scripts/nonml_momentum_turnover_doublesort_pass_validation_battery.py`)
qui réimplémente les 5 mêmes contrôles conceptuels, mais à partir de deux
séries de rendement BRUT (avant coûts) + turnover déjà calculées par le
backtest (`pnl_double_brut`, `turn_double`, `pnl_mom_brut`, `turn_mom`,
`dates`) au lieu de la paire `(pos, r)`. C'est la première fois que la
batterie Règle 9 est appliquée à un candidat stock-selection multi-actifs
plutôt qu'à un overlay mono-actif — précédent explicitement déclaré ici,
pas découvert a posteriori.

Les 5 contrôles restent conceptuellement identiques :
a. Stress de coûts (candidat vs référence, 1x/3x/5x le coût
   pré-enregistré de 5 bps, appliqué au même profil de turnover déjà
   mesuré — le turnover ne change pas avec le coût, seule la ponction
   change).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que la référence sur les fenêtres couvertes par l'historique
   disponible. **Limite déclarée à l'avance** : l'univers de prix/volume
   NDX-100 ne couvre que 2022-2026 (`data/pead/prices|volume/*.json`) —
   SEULE la fenêtre "Resserrement 2022" sera couverte, les trois autres
   seront explicitement PENDING (hors couverture), comme pour tout
   candidat récent de ce backlog (cf. #200/#201).
c. Stabilité temporelle (4 folds non chevauchants + embargo 5j).
d. SPA à 1 candidat contre la référence (`spa_test`).
e. DSR avec n_trials = taille totale du backlog à cette date (265, cf.
   tracker après le #258).

## Référence

Momentum 12-1 seul (#73), PAS Buy&Hold — identique à la référence déjà
utilisée dans le backtest du #258 (cohérence de la comparaison).

## Critère de succès (Règle 9, identique aux cycles #111-#258)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ. Sinon, le
score partiel (X/5) est rapporté tel quel, sans retuning.

## Anti-cheat

Ce fichier committé et poussé AVANT toute exécution de la batterie.
Aucune nouvelle donnée, aucun nouveau réglage de #258 — application
(adaptée mécaniquement au format portefeuille) de l'outil déjà figé.
Sortie : `results/nonml_momentum_turnover_doublesort_pass_validation_battery.md`.
