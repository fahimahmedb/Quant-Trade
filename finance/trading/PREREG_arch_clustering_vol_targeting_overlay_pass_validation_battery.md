# Pré-enregistrement — Batterie Règle 9 sur le #223 (vol-targeting gaté par le clustering ARCH glissant)

**Committé AVANT tout calcul de la batterie.** Cycle #230 du backlog
non-ML. Dernier des 7 PASS niveau 1 accumulés depuis le #215 sans
couverture Règle 9 (après #215/#217/#219/#220/#221/#222 aux #224-#229) —
complète la couverture systématique de toute la série #215-223.

## Contexte et motivation

Le #223 (`PREREG_arch_clustering_vol_targeting_overlay.md`,
`results/nonml_arch_clustering_vol_targeting_overlay_result.md`) est le
7e et dernier PASS niveau 1 chronologique de la série #215-223. PASS
niveau 1 4/5 (seul Composite échoue), robustesse correcte mais pas
parfaite (dip à 3/5 à CAP=3.0x, 2/5 à fenêtre=15j), **5e audit parfait
consécutif** de la série (0 désaccord de recalcul indépendant).

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224-#229).

## Modification technique requise (déclarée avant calcul)

`nonml_arch_clustering_vol_targeting_overlay_backtest.py` sera étendu
pour sauvegarder `results/nonml_arch_clustering_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#229)

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

1. La robustesse niveau 1 déjà imparfaite (dip sous le seuil PASS à
   fenêtre=15j) laisse présager un risque de fragilité similaire sur le
   contrôle de stabilité temporelle Règle 9, comme observé pour le VR
   (#217, Règle 9 1/5) et la kurtosis (#219, Règle 9 2/5) — les deux
   candidats de la série avec le profil de robustesse le moins net.
2. Le DSR est hors de portée pour les 230 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_arch_clustering_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
arch_clustering_vol_targeting_overlay`.
