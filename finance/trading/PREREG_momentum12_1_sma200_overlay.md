# Pré-enregistrement — Momentum 12-1 + overlay levé filtre de tendance SMA200

**Committé AVANT tout calcul.** Cycle #74 du backlog non-ML. Combine le
portefeuille momentum 12-1 (#73, PASS) avec l'overlay de filtre de
tendance SMA200 indice (#29) — mirroir de la combinaison réussie #33
(Leaders 52w-high + SMA200) avec la nouvelle construction de momentum
académique validée au #73.

## Hypothèse

Le #33 a montré que combiner un portefeuille momentum (Leaders 52w-high,
#4) avec un filtre de tendance indice (SMA200, #29) améliore le couple
Sharpe/rendement par rapport au portefeuille momentum seul, en coupant
le levier pendant les régimes baissiers de l'indice. Le #73 (momentum
12-1, construction académique différente) pourrait bénéficier du même
mécanisme.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = momentum 12-1 (#73, LOOKBACK=252, SKIP=21,
  REBAL_EVERY=21, tercile supérieur, aucun paramètre modifié).
- Porte tendance = indice NDX-100 au-dessus de sa SMA200 (identique au
  #29, SMA_WINDOW=200).
- Position = poids du portefeuille momentum 12-1 **1,0x** en permanence,
  **CAP = 2,0x** les jours où l'indice NDX-100 est au-dessus de sa
  SMA200, **1,0x** sinon. Alignement causal du signal de tendance
  indiciel sur le calendrier du portefeuille par ffill (jamais de
  donnée future), identique au #33.
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement/
  changement d'exposition.
- **Référence** : le portefeuille momentum 12-1 SEUL à 1,0x (résultat du
  #73), PAS Buy&Hold — identique à la convention du #33.

## Univers et période

`data/pead/prices/*.json` (titres NDX-100) et `data/nasdaq100_daily.txt`
(indice, pour le signal de tendance), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille momentum 12-1 seul (référence)
**simultanément** en Sharpe annualisé net de coûts ET en rendement total
net de coûts. n_trials=1 (CAP=2,0x et SMA_WINDOW=200 identiques aux
cycles #29/#33 déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_momentum12_1_sma200_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py momentum12_1_sma200_overlay`.
