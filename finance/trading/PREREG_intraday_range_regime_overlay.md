# Pré-enregistrement — Overlay de régime par le RANGE intra-séance (high-low)/close

**Committé AVANT tout calcul.** Cycle #87 du backlog non-ML.

## Note sur l'adaptation de la donnée (fixée ici, avant tout calcul)

L'idée d'origine du backlog (#87) proposait un signal de SÉLECTION
stock-level basé sur l'amplitude intra-séance relative
(`(high-low)/close`) des titres NDX-100 individuels, en complément du
#15 (vol close-to-close) et du #84 (skewness). Vérification faite avant
d'écrire ce PREREG : `data/pead/prices/*.json` ne contient QUE
`{ts, close}` (pas de high/low par titre) — la sélection stock-level
telle qu'imaginée n'est donc PAS réalisable avec les données déjà en
local. Conformément à la clause de repli explicitement anticipée dans
le libellé du backlog ("sinon fallback sur `nasdaq100_daily.txt` au
niveau indice"), ce cycle teste l'hypothèse au niveau INDICE à la
place : un overlay de RÉGIME (calme vs agité) piloté par le range
intra-séance plutôt que par la vol close-to-close (déjà testée aux
cycles #9/#31, tous deux FAIL), sur la famille des 5 marchés OHLC
disponibles localement (plus large que la seule NDX-100, car les 5
fichiers `data/*.txt` contiennent tous les colonnes high/low).

## Hypothèse

Le #9 (régime calme, vol close-to-close roulante, tercile inférieur)
a échoué (2/5). L'amplitude intra-séance `(high-low)/close` est un
estimateur de la volatilité RÉALISÉE DANS LA SÉANCE (exploite toute la
séance, pas seulement les clôtures successives), conceptuellement
distinct de l'écart-type close-to-close ET de l'estimateur de Parkinson
déjà utilisé au #50 (`ln(high/low)²/(4·ln2)`, testé en DÉNOMINATEUR
continu de vol-targeting, pas en porte de régime binaire). Ici, on
teste directement le RANGE BRUT `(high-low)/close` (formule différente
du Parkinson, pas une simple re-labellisation) comme porte de régime
binaire (mécanisme du #9), pour voir si un estimateur différent change
la conclusion du #9.

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt` : Composite,
  NDX-100, Russell 2000, S&P 500, DAX), identique à la famille #9/#29/
  #31/#43/#46.
- Signal : moyenne roulante `RANGE_WINDOW=20` jours de
  `(high[t]-low[t])/close[t]`, calcul causal (valeur connue à la
  clôture de t, utilisée pour décider la position de t+1 comme au #9 —
  `vol_at_decision = range_moy[t-1]`).
- Régime calme : `range_moy(t-1)` dans le tercile INFÉRIEUR de sa
  distribution causale expansive (percentile calculé uniquement sur
  l'historique disponible jusqu'à t-1, identique à la méthode du #9),
  après une période de warm-up de `WARMUP=252` séances.
- Position : **CAP=2.0x** les jours de régime calme, **1.0x** sinon
  (mécanisme binaire identique au #9, pas de vol-targeting continu).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#43). n_trials=1
(RANGE_WINDOW=20j identique à VOL_WINDOW du #9, WARMUP=252j identique,
CAP=2.0x identique, tercile identique, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant
`nonml_intraday_range_regime_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py intraday_range_regime_overlay`.
