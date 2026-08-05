# Pré-enregistrement — Batterie Règle 9 sur le #215 (vol-targeting estimateur Garman-Klass)

**Committé AVANT tout calcul de la batterie.** Cycle #224 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207-
#214 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Depuis la clôture de la couverture Règle 9 des 7 dérivés originaux du
#46 (#207-#214), la lignée vol-targeting s'est enrichie de 9 nouvelles
hypothèses (#215-#223 : 2 nouveaux estimateurs à ce moment-là, 6 nouvelles
portes, 7 PASS niveau 1 au total) — AUCUNE n'a encore été soumise à la
batterie Règle 9. Plutôt que de continuer à générer des hypothèses
marginales supplémentaires dans la même famille (risque de dilution du
signal, cf. discipline anti-snooping), ce cycle reprend la validation
Règle 9 systématique de ces PASS accumulés, un candidat à la fois — même
logique que le pivot du #207 après saturation initiale des nouvelles
idées.

Le #215 (`PREREG_garman_klass_vol_targeting_overlay.md`,
`results/nonml_garman_klass_vol_targeting_overlay_result.md`) est choisi
en premier : PASS net sur les 5 marchés, **plateau de robustesse parfait
8/8** (le plus propre de la lignée d'estimateurs avec le #221
Rogers-Satchell), meilleur MDD amélioré sur NDX de toute la lignée avant
l'arrivée du #222 Yang-Zhang. Premier de la série #215-223 par ordre
chronologique.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts par la
Règle 9 (#207-#214).

## Modification technique requise (déclarée avant calcul)

`nonml_garman_klass_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_garman_klass_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#214)

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

1. L'exposition moyenne du #215 (1,35x-1,59x) est plus élevée que celle
   du #46 (validé 3/5 au #207) — un biais déjà documenté au #215 lui-même
   (dégradation du MDD sur Composite et S&P 500) pourrait se traduire par
   un échec du contrôle de crise (b), comme observé pour le #50
   (Parkinson) au #209.
2. Le DSR est hors de portée pour les 224 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_garman_klass_vol_targeting_overlay_backtest.py` (modifié
pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
garman_klass_vol_targeting_overlay`.
