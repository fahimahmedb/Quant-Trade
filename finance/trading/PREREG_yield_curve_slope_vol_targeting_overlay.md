# Pré-enregistrement — Overlay vol-targeting gaté par la pente de la courbe des taux US (T10Y2Y)

**Committé AVANT tout calcul.** Cycle #114 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Rupture délibérée avec la famille de gates titre-par-titre NDX-100
(~15 variantes déjà testées, toutes corrélées entre 55% et 77%,
mécanisme et source de données cross-sectionnelle identiques). Ce cycle
utilise un signal MACRO indépendant : la pente de la courbe des taux
américains (rendement 10 ans − rendement 2 ans, série FRED `T10Y2Y`,
gratuite, publique, aucune dépendance aux données titre-par-titre déjà
lourdement minées). Hypothèse a priori (littérature établie : une
inversion de la courbe des taux précède historiquement les récessions,
ex. Estrella & Mishkin 1996) : une courbe STEEP/positive (pente au-dessus
de sa médiane récente) signale un contexte macro plus sain, propice à
amplifier l'exposition ; une courbe plate/inversée (pente en dessous de
sa médiane) signale un risque macro élevé, régime où l'on reste au
plancher 1.0x (comportement par défaut de tout le mécanisme hiérarchique
déjà validé, cohérent avec la convention "porte inactive = position de
base 1.0x, jamais < 1.0x").

## Définition (fixée ici, avant tout résultat)

- Signal : `data/t10y2y_daily.csv` (FRED, série `T10Y2Y`, quotidienne,
  récupérée le 29/07/2026, couvre 1976-06-01 → 2026-07-28 — 13087
  observations, dont valeurs manquantes les jours fériés US marquées
  "." dans le fichier source, à traiter en NaN).
- Alignement causal explicite : `Slope(t-1)` (valeur de la VEILLE de
  bourse, jamais la valeur du jour même — même discipline que la
  correction du cycle #110 sur le spillover DAX, éviter toute ambiguïté
  de publication/decalage). Alignement par `reindex` + `ffill` sur le
  calendrier NDX (weekends/fériés asymétriques entre marché obligataire
  et NDX).
- `MEDIAN_WINDOW = 252` séances (médiane glissante, même convention que
  toute la famille).
- Porte active si `Slope(t-1) ≥` sa médiane glissante 252j.
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique à toute la
  famille — SEULE la porte change, pas le mécanisme).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Univers : NDX-100 (`nasdaq100_daily.txt`, 40 ans d'historique — PAS
  restreint à ~2021+ comme la famille titre-par-titre, puisque T10Y2Y
  est disponible sur toute la période NDX). Échantillon testable =
  intersection des dates NDX et T10Y2Y disponibles.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour ce backtest individuel
(construction nouvelle, jamais testée, direction du gate fixée a priori
par la littérature — pas choisie après avoir vu un résultat).

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py yield_curve_slope_vol_
targeting_overlay`, n_trials=taille totale du backlog. Avantage
attendu de ce cycle par rapport aux précédents : historique NDX complet
(40 ans) disponible pour ce signal, contrairement à la famille
titre-par-titre limitée à ~2021+ — les stress-tests de crise (2000-02,
2008) devraient enfin être couverts.

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — MEDIAN_WINDOW=252j n'est PAS
retuné (paramètre de définition, identique à toute la famille).

## Anti-cheat

Ce fichier committé avant
`nonml_yield_curve_slope_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py yield_curve_slope_vol_targeting_overlay`.
Fichier de données `data/t10y2y_daily.csv` committé en même temps que ce
PREREG (source publique gratuite, aucun retraitement autre que le
téléchargement brut).
