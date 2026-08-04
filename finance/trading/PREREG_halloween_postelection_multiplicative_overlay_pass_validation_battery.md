# Pré-enregistrement — Batterie Règle 9 sur le #185 (Halloween x post-électorale, multiplicatif)

**Committé AVANT tout calcul de la batterie.** Cycle #190 du backlog
non-ML. Suite directe du #189 (même discipline : PREREG dédié avant
toute exécution de la batterie, corrigeant l'écart de procédure signalé
au #188).

## Contexte et motivation

Le #185 (`PREREG_halloween_postelection_multiplicative_overlay.md`,
`results/nonml_halloween_postelection_multiplicative_overlay_result.md`)
est le dernier PASS niveau 1 calendaire encore non soumis à la batterie
renforcée — explicitement identifié dans le « Bilan pour la suite » du
#188 comme candidat restant, avec la remarque qu'il est **le plus
fragile des 5 PASS calendaires** (PASS marginal 3/4, robustesse 26/36 —
pas de plateau parfait, contrairement aux #182/#184 à 15/15 et 36/36).
Aucune nouvelle donnée, aucun nouveau réglage : application mécanique de
l'outil déjà figé `nonml_pass_validation_battery.py` à un résultat déjà
committé.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec le choix déjà fait pour tous les candidats
calendaires précédents (#176/#179/#182/#184/#30 aux #188/#189). Note :
le #185 lui-même a marginalement ÉCHOUÉ la jambe Sharpe sur NDX
spécifiquement (+0,52 vs BH +0,53, seul échec parmi les 4 marchés
testés au #185) — ce choix de marché de référence n'est donc PAS
favorable au candidat, il est simplement gardé pour cohérence avec tous
les cycles précédents (aucun choix a posteriori favorable au résultat).

## Modification technique requise (déclarée avant calcul)

`nonml_halloween_postelection_multiplicative_overlay_backtest.py` sera
étendu pour sauvegarder
`results/nonml_halloween_postelection_multiplicative_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#189)

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

1. Le #185 est déjà le PASS le plus fragile testé au niveau 1 (marge
   Sharpe la plus étroite, robustesse jointe non parfaite) — attente
   raisonnable que son score Règle 9 soit AU PLUS aussi bon que celui du
   #184 (2/5, le plus faible des 4 déjà testés au #188), possiblement
   pire étant donné le résultat marginal déjà observé sur NDX.
2. Le DSR est hors de portée pour les 189 hypothèses testées jusqu'ici
   sans exception — aucune raison structurelle d'attendre que le #185 y
   échappe.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_halloween_postelection_multiplicative_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
halloween_postelection_multiplicative_overlay`.
