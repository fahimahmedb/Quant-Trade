# Pré-enregistrement — Overlay vol-targeting gaté par la confirmation multi-marché élargie

**Committé AVANT tout calcul.** Cycle #103 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

Le #52/#57 testaient une confirmation croisée entre SEULEMENT DEUX
marchés (NDX et Russell 2000). Ce cycle élargit à l'ensemble des 5
marchés OHLC déjà en local (Composite, NDX, Russell 2000, S&P 500,
DAX) : la fraction de ces 5 marchés simultanément en tendance haussière
SMA200 (signal identique au #29) comme porte du mécanisme hiérarchique
appliqué à NDX. Granularité de breadth INTER-MARCHÉS (mondiale/multi-
indices) plutôt qu'intra-marché (stock-level, comme la majorité des
breadth déjà testées #77/#89/#94/#96/#97/#98/#100/#101). Une large
majorité de marchés mondiaux en tendance haussière simultanée pourrait
signaler un régime macro plus robuste qu'une confirmation à seulement
deux marchés (marginal/fragile au #52).

## Définition (fixée ici, avant tout résultat)

- Marchés composant la breadth : les 5 marchés OHLC déjà en local
  (`data/*.txt` : Composite, NDX, Russell 2000, S&P 500, DAX).
- Marché de base testé (celui dont l'exposition est pilotée) : NDX
  (`nasdaq100_daily.txt`), pour comparabilité avec la majorité des
  autres cycles de la famille vol-targeting (#46/#47/#57/#78/etc.).
- Tendance par marché : `close(t) > SMA200(t)` (IDENTIQUE au #29).
- Breadth multi-marché(t) = fraction des 5 marchés en tendance
  haussière SIMULTANÉMENT au jour t (alignement causal par `ffill` sur
  le calendrier NDX, chaque marché contribue dès que sa propre SMA200
  est calculable).
- Porte active si Breadth multi-marché(t) ≥ `BREADTH_THRESHOLD=0.6`
  (majorité stricte, au moins 3 des 5 marchés — seuil naturel de
  majorité, pas un retuning).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96/#97/#98/#99/#100.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

`data/*.txt` (5 marchés OHLC), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. n_trials=1
(SMA_WINDOW=200j identique au #29, BREADTH_THRESHOLD=0.6 (majorité
naturelle sur 5 marchés) fixé ici a priori, CAP=2.0x et vol
cible/fenêtre identiques à la famille, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94/#96/#98/#99/#100.

## Anti-cheat

Ce fichier committé avant
`nonml_multimarket_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
multimarket_breadth_vol_targeting_overlay`.
