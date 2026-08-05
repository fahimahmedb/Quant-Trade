# Pré-enregistrement — Batterie Règle 9 sur le #221 (vol-targeting estimateur Rogers-Satchell)

**Committé AVANT tout calcul de la batterie.** Cycle #228 du backlog
non-ML. Continue le pivot Règle 9 (5e candidat après #215/#217/#219/#220
aux #224-#227).

## Contexte et motivation

Le #221 (`PREREG_rogers_satchell_vol_targeting_overlay.md`,
`results/nonml_rogers_satchell_vol_targeting_overlay_result.md`) est le
5e PASS niveau 1 chronologique de la série #215-223. PASS net sur les 5
marchés, **plateau de robustesse parfait 8/8** (comme le #215 Garman-
Klass, déjà validé 4/5 au #224). Résultats bruts très proches du #215
(même risque documenté au #221 lui-même : robustesse au drift a un effet
marginal sur données quotidiennes). Continue la couverture Règle 9 un
candidat à la fois.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats déjà couverts (#207-
#214, #224-#227).

## Modification technique requise (déclarée avant calcul)

`nonml_rogers_satchell_vol_targeting_overlay_backtest.py` sera étendu
pour sauvegarder `results/nonml_rogers_satchell_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#227)

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

1. Le #215 (Garman-Klass, plateau parfait 8/8 également, exposition
   moyenne quasi identique) a obtenu 4/5 au #224, échouant uniquement
   sur le stress de crise 2022 (biais d'exposition plus élevée que le
   #46/#50) — le #221, dont les résultats bruts sont quasi identiques
   au #215, pourrait reproduire exactement ce même profil (4/5, échec
   sur 2022).
2. Le DSR est hors de portée pour les 228 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_rogers_satchell_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
rogers_satchell_vol_targeting_overlay`.
