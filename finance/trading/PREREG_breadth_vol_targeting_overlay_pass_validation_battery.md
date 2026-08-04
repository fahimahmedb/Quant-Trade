# Pré-enregistrement — Batterie Règle 9 sur le #57 (vol-targeting gaté par la confirmation multi-marché breadth)

**Committé AVANT tout calcul de la batterie.** Cycle #211 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207/
#208/#209/#210 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #57 (`PREREG_breadth_vol_targeting_overlay.md`,
`results/nonml_breadth_vol_targeting_overlay_result.md`) remplace la
porte de tendance du #47 (validée Règle 9 au #208, 3/5) par une porte de
confirmation multi-marché (breadth NDX+Russell 2000 simultanément proches
de leur plus haut 252j, #52) — teste si le principe de gating
hiérarchique se généralise à une porte construite à partir d'un second
marché plutôt que du seul actif tradé. PASS niveau 1 net, plateau parfait
8/8 sur les deux grilles, MDD exactement préservé. Continue le même fil
de couverture Règle 9 de la lignée vol-targeting, un cycle à la fois
(#207, #208, #209, #210). Aucune nouvelle donnée, aucun nouveau réglage.

## Marché de référence pour la batterie

NDX (40 ans) — le script `nonml_breadth_vol_targeting_overlay_backtest.py`
ne teste déjà que ce seul marché comme actif tradé (le Russell 2000 n'est
utilisé que comme signal de confirmation, pas comme actif alternatif) —
cohérent avec le marché de référence des #207-#210.

## Modification technique requise (déclarée avant calcul)

`nonml_breadth_vol_targeting_overlay_backtest.py` sera étendu pour
sauvegarder `results/nonml_breadth_vol_targeting_overlay_pnl.npz` (pos,
r_asset, dates, cost_bps) directement après le calcul unique déjà présent
(pas de boucle multi-marché à modifier ici, à la différence des #207-#210),
sans aucun changement de logique de calcul — vérifié par re-exécution
identique du résultat déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#210)

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

1. La porte breadth (signal ET entre deux marchés) est probablement plus
   restrictive dans le temps que les portes univariées déjà testées
   (#47/#54/#68/#78/#80) — un pourcentage d'activation plus faible
   pourrait dégrader la stabilité temporelle (moins d'observations
   actives par fold) même si le profil brut est net.
2. Le DSR est hors de portée pour les 211 hypothèses testées jusqu'ici
   sans aucune exception.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_breadth_vol_targeting_overlay_backtest.py` (modifié pour
sauvegarder le `_pnl.npz`, aucun changement de logique). Vérification via
`nonml_anti_cheat_check.py breadth_vol_targeting_overlay`.
