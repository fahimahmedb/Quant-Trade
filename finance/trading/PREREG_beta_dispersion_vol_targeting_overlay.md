# Pré-enregistrement — Overlay vol-targeting gaté par la dispersion des betas individuels

**Committé AVANT tout calcul.** Cycle #109 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

Distincte de la dispersion des RENDEMENTS quotidiens (#78, PASS) et de
la dispersion du MOMENTUM (#100, PASS) : ce cycle mesure la dispersion
cross-sectionnelle des BETAS individuels glissants (sensibilité de
chaque titre au marché, régression roulante), pas leur performance ou
leur direction. Une forte hétérogénéité des sensibilités au marché
(certains titres très corrélés au marché, d'autres peu) pourrait
signaler un environnement où la sélection de titres est plus
pertinente qu'un simple pari directionnel sur l'indice — même logique
que le #78 (dispersion élevée = favorable) mais appliquée à un
troisième moment statistique distinct (la sensibilité, pas le niveau
ou la direction).

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #78/#100.
- Marché de référence pour la régression : rendements log quotidiens de
  l'indice NDX-100 (`data/nasdaq100_daily.txt`), aligné sur le
  calendrier des titres (dates communes, les titres étant des
  composantes de l'indice).
- Beta glissant par titre : `Beta_i(t) = Cov(r_i, r_marché) /
  Var(r_marché)` sur une fenêtre roulante `BETA_WINDOW=60` jours (même
  fenêtre que les autres signaux de second ordre du backlog
  #15/#84/#92/#93/#95/#100/#107), écart-type/covariance ddof=1.
- Dispersion des betas(t) = écart-type cross-sectionnel (ddof=1) des
  betas individuels calculables au jour t (`MIN_LISTED=10`, identique
  au #78/#100).
- Porte active si Dispersion des betas(t) ≥ sa médiane glissante
  causale `MEDIAN_WINDOW=252` jours (dispersion ÉLEVÉE = favorable,
  même direction que le #78/#100).
- Échantillon restreint à la période où le signal est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96/#97/#98/#99/#100.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1
(BETA_WINDOW=60j identique aux autres signaux de second ordre,
MEDIAN_WINDOW=252j et MIN_LISTED=10 identiques au #78/#100, CAP=2.0x et
vol cible/fenêtre identiques à la famille, aucune grille testée avant
ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au
#47/#57/#78/#94/#96/#98/#99/#100.

## Anti-cheat

Ce fichier committé avant
`nonml_beta_dispersion_vol_targeting_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py beta_dispersion_vol_targeting_overlay`.
