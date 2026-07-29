# Pré-enregistrement — Overlay vol-targeting gaté par la breadth de MOMENTUM

**Committé AVANT tout calcul.** Cycle #94 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

Distincte des breadth de NIVEAU déjà testées (#77 : proximité au plus
haut, #89 : proximité au plus bas) et de la dispersion/corrélation
cross-sectionnelles (#78/#90 : mesurées sur les rendements du jour, pas
sur une fenêtre longue de momentum), ce cycle mesure la largeur du
marché en termes de DIRECTION du momentum à moyen terme : la fraction
des titres NDX-100 ayant un momentum 12-1 mois POSITIF (construction
académique du #73, Jegadeesh & Titman, déjà validée comme signal de
sélection PASS). Une large majorité de titres en momentum positif
signale une tendance haussière large et saine (contrairement à une
hausse portée par quelques titres seulement), motivant une
amplification de l'exposition via le mécanisme hiérarchique déjà
validé sur 4 autres types de porte (tendance #47, calendrier #54,
breadth de niveau #57, dispersion #78).

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #73/#77/#78/#89.
- Momentum 12-1 mois par titre : IDENTIQUE au #73
  (`LOOKBACK=252, SKIP=21`, `momentum = close(t-SKIP)/close(t-LOOKBACK) - 1`),
  nécessite l'historique complet de 252j.
- Breadth de momentum(t) = fraction des titres COTÉS ce jour-là (avec
  momentum calculable) ayant un momentum POSITIF (dénominateur = titres
  cotés avec momentum calculable, même convention que #77/#78/#89).
- Porte active si Breadth de momentum(t) ≥ `BREADTH_THRESHOLD=0.50`
  (majorité du panier en momentum positif — même seuil que le #77/#89,
  aucun retuning, juste appliqué à une breadth différente).
- Échantillon restreint à la période où la breadth est réellement
  disponible (leçon du #77, appliquée dès le départ comme aux
  #78/#89/#90).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (tous les
paramètres repris identiques au #46/#47/#57/#73/#77/#89/#90, aucune
grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78.

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
momentum_breadth_vol_targeting_overlay`.
