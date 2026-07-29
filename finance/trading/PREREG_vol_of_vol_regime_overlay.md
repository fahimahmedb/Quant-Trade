# Pré-enregistrement — Overlay de régime par le vol-of-vol

**Committé AVANT tout calcul.** Cycle #102 du backlog non-ML.

## Hypothèse

Signal de SECOND ORDRE, distinct du niveau de vol lui-même (#9/#31,
close-to-close ; #87, range intra-séance, PASS), de la skewness (#92)
et de la kurtosis (#93) des rendements : l'écart-type glissant de la
VOL RÉALISÉE elle-même ("vol-of-vol"), motivé par la littérature sur le
clustering de volatilité non stationnaire — un régime où la vol
elle-même varie beaucoup (transition, instabilité) pourrait être moins
propice à l'amplification qu'un régime où la vol reste STABLE, même si
son niveau absolu n'est pas particulièrement bas. Par analogie directe
avec le mécanisme de régime calme du #9/#87 (stabilité = favorable),
ce cycle teste si un vol-of-vol FAIBLE (vol stable, pas de
retournement de régime) précède un contexte plus favorable à
l'amplification.

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#87/#92/#93/#95.
- Vol réalisée = écart-type roulant `VOL_WINDOW=20` jours des
  rendements log quotidiens de l'indice (même fenêtre que le
  vol-targeting #46/#47).
- Vol-of-vol = écart-type roulant `VOV_WINDOW=60` jours de la série de
  vol réalisée elle-même (même fenêtre que les autres signaux de second
  ordre du backlog, #15/#84/#92/#93).
- Régime "stable" : vol-of-vol(t-1) dans le tercile INFÉRIEUR (vol-of-vol
  la plus FAIBLE) de sa distribution causale expansive (percentile
  calculé uniquement sur l'historique disponible jusqu'à t-1, méthode
  identique au #9/#87/#92/#93), après un warm-up de `WARMUP=252`
  séances.
- Position : **CAP=2.0x** les jours de régime stable, **1.0x** sinon
  (mécanisme binaire simple, identique au #9/#31/#87/#92/#93).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#87/#92/#93). n_trials=1
(VOL_WINDOW=20j identique au #46/#47, VOV_WINDOW=60j identique au
#15/#84/#92/#93, WARMUP=252j et tercile identiques au #9/#87/#92/#93,
CAP=2.0x identique à la famille, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant `nonml_vol_of_vol_regime_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py vol_of_vol_regime_overlay`.
