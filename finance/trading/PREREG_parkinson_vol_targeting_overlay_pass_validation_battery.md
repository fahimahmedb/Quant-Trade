# Pré-enregistrement — Batterie Règle 9 sur le #50 (vol-targeting Parkinson)

**Committé AVANT tout calcul de la batterie.** Cycle #209 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207/
#208 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #50 (`PREREG_parkinson_vol_targeting_overlay.md`,
`results/nonml_parkinson_vol_targeting_overlay_result.md`) remplace
l'estimateur de volatilité close-to-close du #46 (validé Règle 9 au
#207, 3/5) par l'estimateur range-based de Parkinson (haut/bas
intra-séance). **PASS niveau 1 net sur les 5 marchés**, plateau de
robustesse parfait sur les deux grilles (CAP et fenêtre) — le profil
brut le plus propre de toute la lignée vol-targeting testée à ce jour
(supérieur au #46 3/5 net et au #47 3/5 avec compromis coûts/stabilité).
Continue le même fil de couverture Règle 9 de cette lignée mécanique,
un cycle à la fois. Aucune nouvelle donnée, aucun nouveau réglage.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats précédents.

## Modification technique requise (déclarée avant calcul)

`nonml_parkinson_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_parkinson_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#208)

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

1. Le #50 a une exposition moyenne nettement plus élevée que le #46
   (1,31x-1,54x contre ~1,10x-1,51x), un biais déjà anticipé et
   documenté au PREREG d'origine (Parkinson sous-estime la vol réelle
   car ignore le gap d'ouverture) — cette exposition plus élevée
   pourrait dégrader le contrôle de crise (b) par rapport au #46/#47.
2. Le PASS niveau 1 le plus propre (5/5, plateau parfait) ne garantit
   pas le meilleur score Règle 9 — le #47 a montré qu'un edge brut plus
   net (SPA) peut coexister avec une fragilité sur d'autres contrôles.
3. Le DSR est hors de portée pour les 209 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_parkinson_vol_targeting_overlay_backtest.py` (modifié
pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
parkinson_vol_targeting_overlay`.
