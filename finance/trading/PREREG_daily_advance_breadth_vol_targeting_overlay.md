# Pré-enregistrement — Overlay vol-targeting gaté par la breadth journalière (advance/decline)

**Committé AVANT tout calcul.** Cycle #101 du backlog non-ML.

## Hypothèse

Toutes les breadth déjà testées dans ce backlog mesurent une notion de
MOYEN/LONG terme : niveau extrême sur 252j (#77/#89/#97), position par
rapport à une moyenne mobile 200j (#96), signe d'un momentum 12-1 mois
(#94/#98/#100). Ce cycle teste une granularité radicalement plus
courte : la fraction de titres NDX-100 en HAUSSE au jour le jour
("advance/decline" quotidien classique en analyse technique de
largeur), lissée sur une fenêtre TRÈS COURTE pour limiter le bruit d'un
seul jour. Une large majorité de titres avançant simultanément sur les
derniers jours pourrait signaler une dynamique de marché plus large et
saine que la même hausse portée par peu de titres, motivant une
amplification via le mécanisme hiérarchique déjà validé sur 9 autres
types de porte.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION, identique au #77/#78/#89/#94/#96/#97/#100.
- Avance quotidienne(t) pour un titre = `close(t) > close(t-1)`
  (rendement journalier strictement positif).
- Breadth d'avance(t) = fraction des titres COTÉS ce jour-là (avec un
  rendement journalier calculable) en avance, moyennée sur une fenêtre
  roulante `ADV_WINDOW=5` jours (une semaine de bourse — fenêtre
  volontairement TRÈS COURTE par rapport aux 60-252j des autres portes
  de ce backlog, pour tester spécifiquement la granularité quotidienne,
  pas un simple retuning d'une fenêtre déjà testée).
- Porte active si Breadth d'avance(t) ≥ `BREADTH_THRESHOLD=0.50` (majorité
  du panier en hausse sur la semaine écoulée — même seuil que le
  #77/#89/#94/#96, aucun retuning).
- Échantillon restreint à la période où la breadth est réellement
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
(ADV_WINDOW=5j fixé ici a priori — une semaine de bourse, choix motivé
par la granularité "quotidienne" recherchée, pas une grille testée —,
BREADTH_THRESHOLD=0.50 identique au #77/#89/#94/#96, CAP=2.0x et vol
cible/fenêtre identiques à la famille, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol-targeting ∈ {15j, 20j, 25j, 30j} — identique au
#47/#57/#78/#94/#96/#98/#99/#100. `ADV_WINDOW` n'est PAS perturbé (au
cœur de l'hypothèse testée : la granularité courte elle-même).

## Anti-cheat

Ce fichier committé avant
`nonml_daily_advance_breadth_vol_targeting_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py
daily_advance_breadth_vol_targeting_overlay`.
