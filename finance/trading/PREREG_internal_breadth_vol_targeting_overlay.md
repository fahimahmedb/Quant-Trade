# Pré-enregistrement — Overlay vol-targeting gaté par la breadth INTERNE NDX-100

**Committé AVANT tout calcul.** Cycle #77 du backlog non-ML. Nouvelle
construction de breadth, distincte de la confirmation cross-index déjà
testée (#52/#57/#63, qui compare DEUX INDICES entre eux) : ici la
breadth mesure la dispersion INTERNE d'un seul panier — la fraction des
99 titres NDX-100 proches de leur propre plus haut 52-semaines à chaque
instant. Combinée au mécanisme hiérarchique vol-targeting déjà validé
sur 5 autres types de porte (tendance #47/#68, calendrier #54/#72,
breadth cross-index #57).

## Hypothèse

Une large majorité de titres proches de leur plus haut annuel signale un
marché haussier LARGE (pas porté par quelques titres seulement) —
régime potentiellement plus sain/durable qu'un marché haussier étroit.
Gater le vol-targeting de l'indice NDX-100 par cette breadth interne
pourrait produire un edge comparable aux autres portes de tendance déjà
validées, avec une information distincte (dispersion interne, pas
niveau de prix de l'indice lui-même).

## Définition (fixée ici, avant tout résultat)

- Pour chaque titre NDX-100 (`data/pead/prices/*.json`), signal
  individuel = proximité ≥95% du plus haut glissant 252j (identique au
  #37/#52, `INDEX_LOOKBACK=252`, `INDEX_THRESHOLD=0.95`).
- Breadth(t) = fraction des titres listés au jour t qui sont "proches de
  leur haut" (numérateur = titres proches de leur haut ET cotés,
  dénominateur = titres cotés).
- Porte = Breadth(t) ≥ `BREADTH_THRESHOLD=0.50` (majorité des titres
  cotés proches de leur haut — seuil naturel de majorité, fixé a priori,
  pas calibré sur les données).
- Quand la porte est active : position sur l'INDICE NDX-100 = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques au
  #46/#47/#57, aucun retuning).
- Quand la porte est inactive : position = **1,0x**.
- Alignement causal : breadth(t) calculée sur le calendrier des tickers
  (UNION), alignée sur le calendrier de l'indice NDX-100 par ffill
  (jamais de donnée future), même convention que #52/#57.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/pead/prices/*.json` (titres NDX-100, pour la breadth) et
`data/nasdaq100_daily.txt` (indice, pour le rendement testé), déjà en
local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Un seul
marché testé (NDX), car la breadth interne nécessite les constituants
NDX-100 déjà récupérés (identique au format mono-marché des #52/#57).
n_trials=1 (BREADTH_THRESHOLD=0,50, seuil 95%/252j et paramètres
vol-targeting repris à l'identique des cycles validés, aucune grille
testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_internal_breadth_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py internal_breadth_vol_targeting_overlay`.
