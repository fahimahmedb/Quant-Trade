# Pré-enregistrement — Overlay vol-targeting gaté par la dispersion du momentum

**Committé AVANT tout calcul.** Cycle #100 du backlog non-ML. Dernière
hypothèse en file avant renouvellement du backlog.

## Hypothèse

Distincte de la dispersion des RENDEMENTS quotidiens (#78, PASS,
amplitude des écarts du jour) : ce cycle mesure la dispersion
cross-sectionnelle des SCORES DE MOMENTUM 12-1 mois individuels
(construction du #73, PASS comme signal de sélection). Une forte
dispersion des momentums entre titres signale un environnement où les
trajectoires individuelles divergent nettement (stock-picking net,
leaders et retardataires clairement identifiables) ; une faible
dispersion signale un marché synchronisé où tous les titres évoluent
de façon similaire (momentum peu différenciant). Par analogie directe
avec le #78 (dispersion des rendements ÉLEVÉE = favorable), l'hypothèse
teste si une dispersion de MOMENTUM élevée est également favorable à
l'amplification de l'exposition.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #73/#78/#94.
- Momentum 12-1 mois par titre : IDENTIQUE au #73/#94
  (`LOOKBACK=252, SKIP=21`).
- Dispersion du momentum(t) = écart-type cross-sectionnel (ddof=1) des
  scores de momentum calculables au jour t (`MIN_LISTED=10`, identique
  au #78).
- Porte active si Dispersion du momentum(t) ≥ sa médiane glissante
  causale `MEDIAN_WINDOW=252` jours (dispersion ÉLEVÉE = favorable,
  même direction que le #78).
- Échantillon restreint à la période où le signal est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96/#97/#98/#99.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1
(LOOKBACK=252j/SKIP=21j identiques au #73/#94, MEDIAN_WINDOW=252j et
MIN_LISTED=10 identiques au #78, CAP=2.0x et vol cible/fenêtre
identiques à la famille, aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94/#96/#98/#99.

## Anti-cheat

Ce fichier committé avant
`nonml_momentum_dispersion_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
momentum_dispersion_vol_targeting_overlay`.
