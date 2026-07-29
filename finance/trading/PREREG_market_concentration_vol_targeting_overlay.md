# Pré-enregistrement — Overlay vol-targeting gaté par la concentration du marché

**Committé AVANT tout calcul.** Cycle #99 du backlog non-ML.

## Hypothèse

Distincte de la dispersion des rendements du jour (#78, amplitude des
écarts) et de la corrélation moyenne (#90, co-mouvement temporel), ce
cycle mesure la CONCENTRATION du rendement du marché : le gain total du
panier est-il porté par un petit nombre de titres (marché étroit,
analogue à la thèse "Magnificent 7" largement discutée sur les indices
US récents) ou largement partagé entre les titres ? Un marché à
participation LARGE (gains diffus entre de nombreux titres) est
généralement considéré plus sain/résilient qu'un marché porté par
quelques titres seulement (fragilité si ces leaders se retournent),
motivant une amplification de l'exposition en régime de FAIBLE
concentration.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #78/#90.
- Fenêtre de calcul `CONC_WINDOW=60` jours (même fenêtre que le
  #15/#84/#92/#93, réutilisée par cohérence).
- Pour chaque titre coté avec historique complet sur la fenêtre :
  rendement cumulé sur `CONC_WINDOW` jours, `contribution_i =
  max(rendement_i, 0)` (seule la contribution POSITIVE compte, un
  titre en baisse ne "concentre" pas le gain).
- Concentration(t) = indice de Herfindahl-Hirschman des parts de
  contribution : `HHI(t) = Σ(contribution_i / Σcontribution)²` sur les
  titres éligibles (`MIN_LISTED=10`, identique au #78). HHI élevé =
  gains concentrés sur peu de titres ; HHI bas = gains diffus.
- Porte active si Concentration(t) ≤ sa médiane glissante causale
  `MEDIAN_WINDOW=252` jours (régime de FAIBLE concentration = marché
  large/sain, mécanisme identique au #78 mais direction adaptée au sens
  économique : faible concentration = favorable, contrairement à la
  dispersion du #78 où c'est la dispersion ÉLEVÉE qui est favorable).
- Échantillon restreint à la période où le signal est réellement
  disponible (leçon du #77, appliquée dès le départ).
- Position(t) = **clip(vol_cible 20% / vol_réalisée_NDX_20j(t-1), 1.0,
  CAP=2.0)** si la porte est active, **1.0x** sinon — mécanisme
  identique au #46/#47/#57/#78/#89/#90/#94/#96/#97/#98.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX-100 (`data/nasdaq100_daily.txt`).

## Univers et période

Prix NDX-100 déjà récupérés (`data/pead/prices/`), `data/nasdaq100_daily.txt`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts. n_trials=1
(CONC_WINDOW=60j identique au #15/#84/#92/#93, MEDIAN_WINDOW=252j et
MIN_LISTED=10 identiques au #78, CAP=2.0x et vol cible/fenêtre
identiques à la famille, aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — identique au #47/#57/#78/#94/#96/#98.

## Anti-cheat

Ce fichier committé avant
`nonml_market_concentration_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
market_concentration_vol_targeting_overlay`.
