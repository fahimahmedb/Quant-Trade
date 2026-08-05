# Pré-enregistrement — Overlay vol-targeting gaté par la vol-de-la-vol glissante

**Committé AVANT tout calcul.** Cycle #220 du backlog non-ML. Idée #220
proposée au cycle #218, dernière ligne "à faire" de la série de moments
statistiques (#217 VR PASS, #218 skewness FAIL, #219 kurtosis PASS).

## Hypothèse

Toutes les portes déjà testées pour le mécanisme hiérarchique (#46)
capturent un signal de PREMIER ordre (niveau de tendance/calendrier/
breadth/dispersion/gap/autocorrélation/asymétrie/kurtosis). Ce cycle
teste un signal de SECOND ordre sur la volatilité elle-même : la
**vol-de-la-vol** (écart-type glissant de la série de volatilité réalisée,
distincte du NIVEAU de volatilité déjà utilisé partout dans le mécanisme
#46 lui-même). Une vol-de-la-vol ÉLEVÉE signale un régime de volatilité
INSTABLE/en transition (risque de rupture de régime), une vol-de-la-vol
FAIBLE un régime de volatilité STABLE (même si le niveau absolu de vol
peut être haut ou bas).

**Direction déclarée à l'avance (Règle 2)** : porte active (amplification
autorisée) quand `VolOfVol(t) <= médiane glissante 252j de VolOfVol`,
c'est-à-dire une instabilité de régime récente SOUS sa norme historique
récente (régime de volatilité stable = favorable à l'amplification).
Même logique "stable/calme = amplifier" que les #216 (risque de gap) et
#219 (kurtosis).

## Définitions et alignement causal (déclarés avant calcul)

- `vol_ann_lagged(t)` = EXACTEMENT la même série que celle utilisée par
  le mécanisme #46 lui-même pour piloter l'exposition (écart-type
  glissant `VOL_WINDOW=20` des rendements, annualisé, décalé d'un jour
  — donc `vol_ann_lagged(t)` ne dépend que de `r[<t]`, jamais de `r(t)`).
- `VolOfVol(t)` = écart-type glissant sur `VOV_WINDOW=252` observations
  de `vol_ann_lagged`, se terminant AU jour t inclus. Comme
  `vol_ann_lagged(t)` ne dépend déjà que de `r[<t]`, `VolOfVol(t)` ne
  dépend également que de `r[<t]` — causal par construction, sans
  décalage supplémentaire nécessaire (même style que les #217/#218/#219).
- `MEDIAN_WINDOW=252` réutilisé à l'identique des #78/#100/#216/#218/#219
  (Règle 7). `VOV_WINDOW=252` réutilisé de la même fenêtre dominante.
- Porte = `VolOfVol(t) <= rolling_median_252j(VolOfVol)(t)`.

## Mécanisme (identique aux #47/#54/#57/#68/#78/#80/#216-#219)

`Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
active, `1.0x` sinon. CAP=2.0, TARGET_VOL_ANNUAL=0.20, VOL_WINDOW=20
réutilisés à l'identique du #46 (Règle 7). Coût 5 bps aller-retour.
Échantillon testable à partir de la 274e séance (VOL_WINDOW=20 pour
`vol_ann_lagged`, puis VOV_WINDOW=252 et MEDIAN_WINDOW=252 empilés
dessus).

## Univers

Les 5 marchés déjà utilisés dans toute la lignée vol-targeting
(Composite 5 ans, NDX 40 ans, Russell 2000, S&P 500, DAX) — rendements
déjà disponibles, aucun nouveau fetch.

## Critère de succès (n_trials=1, PASS niveau 1)

Sur ≥4/5 marchés, l'overlay doit battre Buy & Hold ET en Sharpe annualisé
ET en rendement total net de coûts (règle renforcée identique à toute la
lignée #46-#219).

## Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. La vol-de-la-vol pourrait être fortement corrélée au NIVEAU de
   volatilité lui-même (les pics de vol s'accompagnent souvent de
   variations rapides de la vol) — risque de redondance avec le
   mécanisme sous-jacent, comme anticipé (et finalement non confirmé)
   pour la kurtosis au #219.
2. Empiler trois fenêtres de calcul (VOL_WINDOW puis VOV_WINDOW puis
   MEDIAN_WINDOW) réduit l'échantillon testable et pourrait lisser le
   signal au point de le rendre trop lent (risque déjà matérialisé pour
   les portes lentes #68/#80 en Règle 9).
3. Le DSR est hors de portée pour les 220 hypothèses testées jusqu'ici
   sans aucune exception.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## Anti-cheat

Ce fichier committé avant tout calcul. Script :
`scripts/nonml_vol_of_vol_vol_targeting_overlay_backtest.py` (nouveau).
Vérification via `nonml_anti_cheat_check.py
vol_of_vol_vol_targeting_overlay`.
