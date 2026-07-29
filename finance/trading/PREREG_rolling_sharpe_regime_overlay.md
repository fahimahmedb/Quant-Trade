# Pré-enregistrement — Overlay de régime par le Sharpe glissant de l'indice

**Committé AVANT tout calcul.** Cycle #107 du backlog non-ML.

## Hypothèse

Les signaux de régime déjà testés (vol #9/#31, range intra-séance #87,
skewness #92, kurtosis #93, autocorrélation #95) ne regardent que la
distribution des RENDEMENTS eux-mêmes, jamais leur ratio RISQUE-AJUSTÉ.
Ce cycle teste si un régime de Sharpe glissant ÉLEVÉ ("hot streak" de
qualité risque-ajustée, combinant rendement ET risque en un seul
signal) précède un contexte plus favorable à l'amplification — par
analogie directe avec le mécanisme de régime calme du #9/#87 mais un
estimateur de nature différente (ratio composite plutôt qu'un moment
de la distribution).

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#87/#92/#93/#95.
- Sharpe glissant = moyenne / écart-type (ddof=1) des rendements log
  quotidiens sur une fenêtre roulante `SHARPE_WINDOW=60` jours
  (annualisé ×√252, même fenêtre que les autres signaux de second
  ordre du backlog #15/#84/#92/#93/#95).
- Régime "hot streak" : Sharpe glissant(t-1) dans le tercile SUPÉRIEUR
  de sa distribution causale expansive (percentile calculé uniquement
  sur l'historique disponible jusqu'à t-1, méthode identique au
  #9/#87/#92/#93/#95), après un warm-up de `WARMUP=252` séances.
- Position : **CAP=2.0x** les jours de régime "hot streak", **1.0x**
  sinon (mécanisme binaire simple, identique au #9/#31/#87/#92/#93/#95).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#87/#92/#93/#95). n_trials=1
(SHARPE_WINDOW=60j identique au #92/#93/#95, WARMUP=252j et tercile
identiques au #9/#87/#92/#93/#95, CAP=2.0x identique à la famille,
aucune grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant
`nonml_rolling_sharpe_regime_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py rolling_sharpe_regime_overlay`.
