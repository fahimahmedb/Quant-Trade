# Pré-enregistrement — Momentum de constance + overlay levé filtre de tendance SMA200

**Committé AVANT tout calcul.** Cycle #83 du backlog non-ML. Combine le
portefeuille momentum de constance (#82, PASS) avec l'overlay de filtre
de tendance SMA200 indice (#29) — complète le trio des constructions de
momentum combinées au filtre de tendance indiciel (52w-high #4→#38,
12-1 mois #73→#74, constance #82→#83).

## Hypothèse

Les #38 et #74 ont montré que combiner un portefeuille momentum
(52w-high, 12-1 mois) avec un filtre de tendance indice (SMA200)
améliore le couple Sharpe/rendement par rapport au portefeuille
momentum seul, en coupant le levier pendant les régimes baissiers de
l'indice. Le #82 (momentum de constance, PASS) pourrait bénéficier du
même mécanisme.

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base = momentum de constance (#82, BLOCK_LEN=21,
  N_BLOCKS=12, REBAL_EVERY=21, tercile supérieur, aucun paramètre
  modifié).
- Porte tendance = indice NDX-100 au-dessus de sa SMA200 (identique aux
  #29/#33/#74, SMA_WINDOW=200).
- Position = poids du portefeuille momentum de constance **1,0x** en
  permanence, **CAP = 2,0x** les jours où l'indice NDX-100 est
  au-dessus de sa SMA200, **1,0x** sinon. Alignement causal du signal de
  tendance indiciel sur le calendrier du portefeuille par ffill (jamais
  de donnée future), identique au #33/#74.
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement/
  changement d'exposition.
- **Référence** : le portefeuille momentum de constance SEUL à 1,0x
  (résultat du #82), PAS Buy&Hold — identique à la convention du
  #33/#74.

## Univers et période

`data/pead/prices/*.json` (titres NDX-100) et `data/nasdaq100_daily.txt`
(indice, pour le signal de tendance), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre le portefeuille momentum de constance seul
(référence) **simultanément** en Sharpe annualisé net de coûts ET en
rendement total net de coûts. n_trials=1 (CAP=2,0x et SMA_WINDOW=200
identiques aux cycles #29/#33/#74 déjà validés, aucune grille testée
avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_consistency_sma200_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py momentum_consistency_sma200_overlay`.
