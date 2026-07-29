# Pré-enregistrement — Overlay vol-targeting gaté par la position moyenne dans le range annuel

**Committé AVANT tout calcul.** Cycle #104 du backlog non-ML.

## Hypothèse

Les breadth de niveau déjà testées (#77 proximité au plus haut, #89
proximité au plus bas, #97 nette) sont toutes des comptages BINAIRES à
un seuil fixe (proche/pas proche). Ce cycle teste une mesure CONTINUE :
pour chaque titre, la position exacte du prix dans son range glissant
52-semaines (indicateur `%K` de type stochastique,
`(close-min)/(max-min)`, borné [0,1]), moyennée cross-sectionnellement
sur tous les titres NDX-100. Une moyenne élevée (marché largement dans
la moitié supérieure de son range annuel) signale un régime plus sain
qu'une simple comptabilisation à un seuil extrême, et pourrait capter
une information plus fine que les breadth binaires.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #77/#78/#89/#94/#97.
- Pour chaque titre à historique complet sur `RANGE_LOOKBACK=252` jours :
  `position_i(t) = (close_i(t) - min_glissant_252j) / (max_glissant_252j
  - min_glissant_252j)` (indéfini si max=min, exclu de la moyenne ce
  jour-là).
- Position moyenne du marché(t) = moyenne cross-sectionnelle de
  `position_i(t)` sur les titres éligibles (`MIN_LISTED=10`, identique
  au #78).
- Porte active si Position moyenne(t) ≥ sa médiane glissante causale
  `MEDIAN_WINDOW=252` jours (au-dessus de la médiane = marché dans la
  moitié supérieure de son range habituel, même mécanisme de comparaison
  à une médiane que le #78/#90/#99/#100).
- Échantillon restreint à la période où le signal est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) [exposition] = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1),
  1.0, CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96/#97/#98/#99/#100/#103.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1
(RANGE_LOOKBACK=252j identique au #37/#77/#89, MEDIAN_WINDOW=252j et
MIN_LISTED=10 identiques au #78, CAP=2.0x et vol cible/fenêtre
identiques à la famille, aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94/#96/#98/#99/#100/#103.

## Anti-cheat

Ce fichier committé avant
`nonml_range_position_vol_targeting_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py range_position_vol_targeting_overlay`.
