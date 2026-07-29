# Pré-enregistrement — Double porte AND : dispersion du momentum ET tendance 52w-high

**Committé AVANT tout calcul.** Cycle #106 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

3e test de la généralisation du schéma déjà validé aux #81 (dispersion
cross-sectionnelle #78 ET tendance #47) et #98 (breadth SMA200 #96 ET
breadth de momentum #94) : combiner DEUX portes qui fonctionnent
CHACUNE séparément (dispersion du momentum #100, PASS ; tendance
52w-high indicielle #47, PASS) préserve-t-il l'edge net malgré la
fenêtre plus restrictive de l'intersection ?

## Définition (fixée ici, avant tout résultat)

- Portefeuille de base : Buy & Hold NDX-100
  (`data/nasdaq100_daily.txt`), identique à la référence du #47/#100.
- Porte 1 (tendance) : proximité au plus haut glissant 252j de l'indice
  NDX-100, `close(t) ≥ 0.95 × max_glissant_252j(t)` — IDENTIQUE au
  #37/#47.
- Porte 2 (dispersion du momentum) : dispersion cross-sectionnelle
  (ddof=1) des scores de momentum 12-1 mois individuels des titres
  NDX-100 ≥ sa médiane glissante causale 252j — IDENTIQUE au #100
  (`LOOKBACK=252, SKIP=21, MEDIAN_WINDOW=252, MIN_LISTED=10`).
- Porte combinée active si les DEUX portes sont actives SIMULTANÉMENT
  (AND strict, aucun seuil retouché).
- Échantillon restreint à la période où les DEUX portes sont réellement
  disponibles (leçon du #77, appliquée dès le départ, comme au #81/#98).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte combinée est active, **1.0x** sinon —
  mécanisme identique au #46/#47/#57/#78/#81/#94/#96/#97/#98/#99/#100.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100.

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1 (tous les
paramètres repris identiques aux #47/#100, aucune grille testée avant
ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au
#47/#57/#78/#81/#94/#96/#98/#99/#100.

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_dispersion_trend_and_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
momentum_dispersion_trend_and_overlay`.
