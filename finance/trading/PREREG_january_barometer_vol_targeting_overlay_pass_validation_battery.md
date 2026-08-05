# Pré-enregistrement — Batterie Règle 9 sur le #80 (vol-targeting gaté par le January Barometer)

**Committé AVANT tout calcul de la batterie.** Cycle #213 du backlog
non-ML. Applique la même discipline que les #189/#190/#194/#201/#207-
#212 (PREREG dédié avant toute exécution de la batterie).

## Contexte et motivation

Le #80 (`PREREG_january_barometer_vol_targeting_overlay.md`,
`results/nonml_january_barometer_vol_targeting_overlay_result.md`)
remplace les portes récurrentes déjà testées (tendance #47/#68,
calendrier #54, breadth #57) par une porte de décision ANNUELLE (January
Barometer, #59) — teste si le principe de gating hiérarchique se
généralise à une fréquence de décision radicalement plus lente (une seule
décision par an, contre quotidienne/mensuelle pour les autres portes).
PASS niveau 1 4/5 (seul DAX échoue, de justesse), plateau robuste 4-5/5,
MDD exactement préservé sur Composite et NDX. #78 (dispersion
cross-sectionnelle) est écarté ce cycle car son échantillon testable est
restreint à ~2021-2026 (leçon du #77 déjà appliquée à sa construction) —
la batterie Règle 9 (fenêtres de crise dot-com/2008/2022, folds
temporels) serait peu informative sur un historique aussi court, à la
différence du #80 qui dispose du même historique complet (40 ans NDX) que
tous les candidats déjà couverts (#207-#212). Continue le même fil de
couverture Règle 9, un cycle à la fois. Aucune nouvelle donnée, aucun
nouveau réglage.

## Marché de référence pour la batterie

NDX (40 ans) — cohérent avec tous les candidats précédents.

## Modification technique requise (déclarée avant calcul)

`nonml_january_barometer_vol_targeting_overlay_backtest.py` sera étendu
pour sauvegarder `results/nonml_january_barometer_vol_targeting_overlay_pnl.npz`
(pos, r_asset, dates, cost_bps) sur le marché NDX, sans aucun changement
de logique de calcul — vérifié par re-exécution identique du résultat
déjà committé.

## Critère de succès (Règle 9, identique aux cycles #111-#212)

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

1. La porte annuelle change de valeur une seule fois par an — la
   stabilité temporelle (contrôle c, 4 folds) pourrait être sensible au
   petit nombre d'"essais" de janvier disponibles par fold (environ 10
   décisions annuelles par fold de 10 ans), un régime d'échantillonnage
   très différent des portes récurrentes déjà testées (#46/#47/#50/#54/
   #57/#68).
2. Le #68 (porte lente, fenêtre 200j+20j) a obtenu le score le plus
   faible de la lignée (2/5, stabilité 2/4) — une porte encore plus lente
   (annuelle) pourrait accentuer ce même risque, ou au contraire s'en
   affranchir si le manque de sur-réactivité au bruit court terme est
   justement la source du problème du #68.
3. Le DSR est hors de portée pour les 213 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul de la batterie. Script :
`scripts/nonml_january_barometer_vol_targeting_overlay_backtest.py`
(modifié pour sauvegarder le `_pnl.npz`, aucun changement de logique).
Vérification via `nonml_anti_cheat_check.py
january_barometer_vol_targeting_overlay`.
