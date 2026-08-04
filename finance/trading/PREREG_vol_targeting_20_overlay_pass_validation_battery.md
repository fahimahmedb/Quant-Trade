# Pré-enregistrement — Batterie Règle 9 sur le #46 (vol-targeting continu, cible 20%)

**Committé AVANT tout calcul de la batterie.** Cycle #207 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201 (PREREG
dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #46 (`PREREG_vol_targeting_20_overlay.md`,
`results/nonml_vol_targeting_20_overlay_result.md`) est le mécanisme de
vol-targeting continu (cible 20% annualisée, cap 2.0x) qui sert de
FONDATION à toute une famille de dérivés testés plus tard dans ce
backlog — #47 (gaté par tendance), #50 (estimateur Parkinson), #54
(gaté par calendrier), #57 (gaté par breadth), #68, #78, #80 (gaté par
January Barometer) le citent tous explicitement par son nom. Aucun de
ces cycles n'a cependant validé le MÉCANISME DE BASE lui-même à la
barre Règle 9 — chaque dérivé a été évalué sur son propre critère PASS
niveau 1 (Sharpe/rendement vs Buy&Hold), jamais sur les 5 contrôles
renforcés. Ce trou de couverture est un candidat naturel et bien
justifié pour cette batterie (le mécanisme historique le plus souvent
réutilisé du backlog, jamais soumis à la barre la plus stricte).
Aucune nouvelle donnée, aucun nouveau réglage : application mécanique
de l'outil déjà figé `nonml_pass_validation_battery.py`.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec le choix déjà fait pour tous les candidats
précédents (#38/#134/#149/#165/#176/#179/#182/#184/#30/#185/#193/#200).

## Modification technique requise (déclarée avant calcul)

`nonml_vol_targeting_20_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_vol_targeting_20_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement de
logique de calcul — vérifié par re-exécution identique du résultat déjà
committé.

## Critère de succès (Règle 9, identique aux cycles #111-#206)

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

1. Le mécanisme de vol-targeting réalisée (par opposition à la vol
   PRÉVUE GJR-t du #165, déjà testée à 2/5 au #167) n'a jamais été
   soumis à cette barre — sa robustesse brute (plateau 4-5/5 sur les
   grilles CAP/fenêtre) suggère un profil correct, mais aucune garantie
   face aux contrôles les plus stricts (SPA, DSR).
2. Le DSR est hors de portée pour les 207 hypothèses testées jusqu'ici
   sans aucune exception — aucune raison structurelle d'attendre que le
   #46 y échappe.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_vol_targeting_20_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification
via `nonml_anti_cheat_check.py vol_targeting_20_overlay`.
