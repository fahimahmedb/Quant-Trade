# Pré-enregistrement — Batterie Règle 9 sur le #47 (tendance + vol-targeting)

**Committé AVANT tout calcul de la batterie.** Cycle #208 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207
(PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #47 (`PREREG_trend_vol_targeting_overlay.md`,
`results/nonml_trend_vol_targeting_overlay_result.md`) est le premier
dérivé majeur du #46 (vol-targeting continu 20%, validé au Règle 9 au
#207, score 3/5) — il ajoute une porte directionnelle (tendance 52w-high,
#37) au mécanisme de base. PASS niveau 1 4/5, cité à son tour par
plusieurs dérivés ultérieurs (#51/#53/#68 etc.). Continue le même fil
que le #207 : combler les trous de couverture Règle 9 de la lignée
mécanique la plus réutilisée du backlog, un cycle à la fois (pas un
balayage groupé). Aucune nouvelle donnée, aucun nouveau réglage.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats précédents.

## Modification technique requise (déclarée avant calcul)

`nonml_trend_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_trend_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#207)

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

1. Le #46 (base) a obtenu 3/5 avec une stabilité parfaite (4/4 folds) —
   ajouter la porte de tendance pourrait soit préserver ce profil, soit
   le dégrader (la porte introduit un régime supplémentaire qui peut
   réduire la stabilité si elle est mal alignée sur certains folds,
   comme observé pour d'autres portes dans ce backlog, ex. #131/#137).
2. Le DSR est hors de portée pour les 208 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_trend_vol_targeting_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification
via `nonml_anti_cheat_check.py trend_vol_targeting_overlay`.
