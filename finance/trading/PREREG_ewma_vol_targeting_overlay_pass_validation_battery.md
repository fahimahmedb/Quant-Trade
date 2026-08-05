# Pré-enregistrement — Batterie Règle 9 sur le #231 (vol-targeting estimateur EWMA)

**Committé AVANT tout calcul de la batterie.** Cycle #232 du backlog
non-ML. Backlog "à faire" épuisé après la clôture complète de la
couverture Règle 9 de la série #215-223 (#224-#230, 0/7 PASS RENFORCÉ).
Le #231 (EWMA) est un PASS niveau 1 frais jamais soumis à cette barre —
continue la même discipline de validation systématique appliquée à
chaque nouvelle hypothèse PASS de cette lignée mécanique.

## Contexte et motivation

Le #231 (`PREREG_ewma_vol_targeting_overlay.md`,
`results/nonml_ewma_vol_targeting_overlay_result.md`) réutilise la
récursion `ewma_path` de l'Étape C (adaptée pour être causale) comme 6e
estimateur du mécanisme #46. PASS niveau 1 4/5 (seul Composite échoue
sur le rendement), **meilleur MDD de tous les estimateurs testés** (NDX
-82,9%→-56,8%), robustesse solide (plateau CAP 4/5-5/5, fenêtre
d'amorçage parfaitement stable à 4/5), audit parfait (écarts <5e-16).

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224-#231).

## Modification technique requise (déclarée avant calcul)

`nonml_ewma_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_ewma_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#230)

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

1. Le meilleur MDD de la lignée d'estimateurs (-56,8% sur NDX, encore
   meilleur que le #222 Yang-Zhang qui avait passé le contrôle de crise
   2022 grâce à une exposition moyenne plus faible) suggère un profil de
   crise potentiellement favorable — mais aucune garantie : le #215
   (meilleur plateau brut) a tout de même échoué sur 2022 en Règle 9.
2. La mémoire exponentielle de l'EWMA (réactivité accrue aux chocs
   récents) pourrait produire un turnover plus élevé qu'une fenêtre
   tronquée simple, fragilisant le contrôle de coûts, comme observé pour
   d'autres candidats plus réactifs de ce backlog.
3. Le DSR est hors de portée pour les 232 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_ewma_vol_targeting_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification
via `nonml_anti_cheat_check.py ewma_vol_targeting_overlay`.
