# Pré-enregistrement — Batterie Règle 9 sur le #217 (vol-targeting gaté par le VR de Lo-MacKinlay glissant)

**Committé AVANT tout calcul de la batterie.** Cycle #225 du backlog
non-ML. Continue le pivot commencé au #224 : validation Règle 9
systématique des 7 PASS niveau 1 accumulés depuis le #215 (aucun encore
couvert), un candidat à la fois, par ordre chronologique.

## Contexte et motivation

Le #217 (`PREREG_variance_ratio_vol_targeting_overlay.md`,
`results/nonml_variance_ratio_vol_targeting_overlay_result.md`) est le
2e PASS niveau 1 chronologique de la série #215-223 (après le #215,
couvert au #224, score 4/5). PASS niveau 1 4/5 (seul DAX échoue), porte
la plus rarement active de toute la famille de portes (7,8%-38,2% du
temps). Continue la couverture Règle 9 un candidat à la fois.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224).

## Modification technique requise (déclarée avant calcul)

`nonml_variance_ratio_vol_targeting_overlay_backtest.py` sera étendu
pour sauvegarder `results/nonml_variance_ratio_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#224)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le PREREG d'origine du #217 notait déjà un risque de robustesse
   limitée sur la grille de perturbation (2/5 à fenêtre=15j) — la
   batterie Règle 9, plus stricte, pourrait révéler une fragilité
   similaire sur la stabilité temporelle ou le stress de coûts.
2. La porte étant active seulement 7,8%-38,2% du temps sur NDX, le
   contrôle de stabilité (4 folds) pourrait être sensible au faible
   nombre de séances actives par fold, comme déjà observé pour d'autres
   portes rares (#68/#80, Règle 9 2/5).
3. Le DSR est hors de portée pour les 225 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_variance_ratio_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
variance_ratio_vol_targeting_overlay`.
