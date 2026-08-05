# Pré-enregistrement — Overlay vol-targeting gaté par la kurtosis (aplatissement) glissante

**Committé AVANT tout calcul.** Cycle #219 du backlog non-ML. Idée #219
proposée au cycle #218, première ligne "à faire" de ce cycle.

## Hypothèse

Après la skewness glissante (#218, FAIL 3/5) et le ratio de variance
(#217, PASS 4/5), ce cycle teste le 4e moment statistique — l'excès de
kurtosis (épaisseur des queues de distribution) — comme porte du
mécanisme hiérarchique vol-targeting (#46). Un excès de kurtosis
localement ÉLEVÉ (queues épaisses, risque de choc extrême) est documenté
dans la littérature comme un signal associé aux périodes de stress de
marché ; un excès de kurtosis localement FAIBLE (distribution plus proche
de la normale) est associé à des régimes plus calmes.

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
autorisée) quand `Kurt_glissant(t) <= médiane glissante 252j de
Kurt_glissant`, c'est-à-dire un excès de kurtosis récent SOUS sa norme
historique récente (queues moins épaisses que d'habitude = régime calme
= favorable à l'amplification). Même logique "calme = amplifier" que le
#216 (risque de gap) et même technique auto-référencée que les
#78/#216/#218.

## Définitions et alignement causal (déclarés avant calcul)

- `Kurt_glissant(t)` = excès de kurtosis de Fisher (biais corrigé,
  `scipy.stats.kurtosis(fisher=True, bias=False)`) calculé sur la fenêtre
  `r[t-KURT_WINDOW:t]` (KURT_WINDOW=252 observations se terminant à
  `r[t-1]`, donc EXCLUANT `r[t]` lui-même — même convention causale que
  les #217/#218).
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216/#218
  (Règle 7 — pas de nouveau réglage). `KURT_WINDOW=252` réutilisé de la
  même fenêtre dominante que le #218.
- Porte = `Kurt_glissant(t) <= rolling_median_252j(Kurt_glissant)(t)`.
  Alignement causal identique aux #217/#218 : `gate[k]` déjà causal par
  construction, appliqué directement à `r[k]`, sans décalage
  supplémentaire.

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80/#216/#217/#218)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 254e séance (même convention que les
#217/#218).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — rendements
déjà disponibles, aucun nouveau fetch.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#218).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour la skewness (#218) et le VR (#217), le 4e moment statistique
   nécessite un échantillon important pour une estimation stable — le
   signal pourrait être dominé par du bruit d'estimation.
2. La kurtosis est mécaniquement liée à la volatilité (les épisodes de
   forte vol génèrent souvent aussi des queues épaisses) — le signal
   pourrait être largement redondant avec le niveau de volatilité déjà
   utilisé dans le mécanisme lui-même, réduisant l'information marginale
   apportée par cette porte.
3. Le DSR est hors de portée pour les 219 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_kurtosis_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py
kurtosis_vol_targeting_overlay`.
