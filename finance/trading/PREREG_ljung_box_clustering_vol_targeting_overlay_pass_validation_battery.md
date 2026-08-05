# Pré-enregistrement — Batterie Règle 9 sur le #242 (porte de clustering ARCH par Ljung-Box)

**Committé AVANT tout calcul de la batterie.** Cycle #243 du backlog
non-ML. Backlog "à faire" épuisé après le #242. Le #242 est un PASS
niveau 1 frais (4/5 marchés) jamais soumis à cette barre — continue la
même discipline de validation systématique appliquée à chaque nouvelle
hypothèse PASS de la lignée mécanique (#207-#214, #224-#230, #232, #235,
#238, #241).

## Contexte et motivation

Le #242 (`PREREG_ljung_box_clustering_vol_targeting_overlay.md`,
`results/nonml_ljung_box_clustering_vol_targeting_overlay_result.md`)
réutilise la statistique de Ljung-Box (Étape A, lags jusqu'à 22j) comme
porte de clustering ARCH multi-retards, distincte du lag-1 déjà testé
(#223, PASS 4/5, Règle 9 jamais exécutée — voir note ci-dessous). PASS
niveau 1 4/5 (Composite/NDX/Russell 2000/S&P 500 passent, DAX échoue),
mais robustesse plus fragile qu'un plateau (grille CAP 3-4/5 avec un
seul point à 4/5, grille fenêtre de vol 2-4/5 idem). Ce cycle teste si,
malgré cette fragilité de robustesse (distincte de la fragilité
d'ESTIMATEUR documentée au #237, ici c'est une sensibilité aux
paramètres non-testés plutôt qu'une non-identifiabilité numérique), le
signal possède un edge journalier statistiquement significatif.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-#214,
#224-#232, #235, #238, #241).

## Modification technique requise (déclarée avant calcul)

`nonml_ljung_box_clustering_vol_targeting_overlay_backtest.py` sera
étendu pour sauvegarder
`results/nonml_ljung_box_clustering_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur NDX, sans aucun changement de logique de
calcul — vérifié par re-exécution identique du résultat déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#241)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ :
a. Stress de coûts (×3, ×5 le coût pré-enregistré de 5 bps).
b. Stress de crise (dot-com, 2008, COVID, 2022) — MDD candidat pas pire
   que Buy&Hold (tolérance 1 pt).
c. Stabilité temporelle (4 folds non chevauchants, embargo 5j) — majorité
   de folds où le candidat bat Buy&Hold en Sharpe.
d. SPA de Hansen à 1 candidat contre Buy&Hold (p < 0,05).
e. DSR avec **n_trials = taille totale du backlog au moment de
   l'exécution** (243, jamais 1), seuil DSR > 0,95.

n_trials pour ce cycle lui-même = 1.

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La robustesse fragile documentée au #242 (point isolé sur les deux
   grilles) pourrait se traduire par une stabilité temporelle (c) ou un
   SPA (d) plus faibles que les candidats à plateau solide (ex. #219
   kurtosis, plateau parfait 8/8).
2. Le DSR est hors de portée pour les 243 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_ljung_box_clustering_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Anti-cheat inchangé par rapport au #242 (même pratique qu'aux
#232/#235/#238/#241).
