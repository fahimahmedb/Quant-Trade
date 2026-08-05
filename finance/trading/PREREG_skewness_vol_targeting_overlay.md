# Pré-enregistrement — Overlay vol-targeting gaté par l'asymétrie (skewness) glissante

**Committé AVANT tout calcul.** Cycle #218 du backlog non-ML. Le
backlog "à faire" étant de nouveau épuisé (#215-217 tous exécutés), ce
cycle propose 3 nouvelles idées (#218-220, thème des moments statistiques
d'ordre supérieur/second ordre) et exécute immédiatement la première.

## Hypothèse

Toutes les portes déjà testées pour le mécanisme hiérarchique (#46)
utilisent soit un prix/rendement moyen (tendance #47/#68, calendrier
#54, breadth #57, annuelle #80), soit la dispersion cross-sectionnelle
(#78), soit l'amplitude de gap (#216, FAIL), soit l'autocorrélation locale
(#217, PASS) — jamais l'ASYMÉTRIE (skewness, 3e moment) de la distribution
des rendements. Les rendements actions présentent une asymétrie négative
documentée (chutes brutales, hausses progressives) — une asymétrie
LOCALEMENT plus négative que d'habitude est l'hypothèse retenue comme
signal de risque de queue élevé (défavorable à l'amplification), une
asymétrie proche de sa norme récente ou moins négative comme signal
favorable.

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
autorisée) quand `Skew_glissant(t) >= médiane glissante 252j de
Skew_glissant`, c'est-à-dire une asymétrie récente MOINS négative (ou
plus positive) que sa propre norme historique récente — même technique
que les #78 (dispersion) et #216 (risque de gap), appliquée ici à un
moment statistique différent (asymétrie plutôt que dispersion/amplitude).

## Définitions et alignement causal (déclarés avant calcul)

- `Skew_glissant(t)` = asymétrie de Fisher-Pearson (biais corrigé,
  `scipy.stats.skew`) calculée sur la fenêtre `r[t-SKEW_WINDOW:t]`
  (SKEW_WINDOW=252 observations se terminant à `r[t-1]`, donc EXCLUANT
  `r[t]` lui-même — même convention causale que le #217, qui exclut déjà
  le rendement du jour de décision de son propre calcul de fenêtre).
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216 (Règle 7
  — pas de nouveau réglage). `SKEW_WINDOW=252` réutilisé de la même
  fenêtre dominante déjà employée par cette famille de portes.
- Porte = `Skew_glissant(t) >= rolling_median_252j(Skew_glissant)(t)`.
  Alignement causal identique au #217 : `gate[k]` déjà causal par
  construction (ne dépend que de `r[<k]`), appliqué directement à
  `r[k]`, sans décalage supplémentaire.

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80/#216/#217)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 254e séance (même convention que le
#217 : SKEW_WINDOW=252 + décalage d'une séance).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — rendements
déjà disponibles, aucun nouveau fetch.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#217).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La skewness glissante sur 252 jours est un estimateur statistiquement
   peu stable (le 3e moment nécessite plus d'observations que la moyenne
   ou la variance pour une estimation fiable) — le signal pourrait être
   dominé par du bruit d'estimation plutôt que par un vrai régime.
2. Comme pour le #217 (VR), la fenêtre médiane relative (auto-référencée)
   pourrait produire un taux d'activation très déséquilibré (très
   rarement ou très souvent actif), limitant la portée du test.
3. Le DSR est hors de portée pour les 218 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_skewness_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py
skewness_vol_targeting_overlay`.
