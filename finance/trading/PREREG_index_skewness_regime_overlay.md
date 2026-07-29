# Pré-enregistrement — Overlay de régime par la skewness de l'indice

**Committé AVANT tout calcul.** Cycle #92 du backlog non-ML.

## Hypothèse

L'effet de levier (leverage effect, Black 1976) documente une asymétrie
négative des rendements de marché : les baisses de prix augmentent le
levier financier effectif des entreprises, ce qui accroît la volatilité
future et le risque de queue gauche. Ce cycle teste si un régime de
skewness MOINS négative (queue gauche moins prononcée, régime plus
"sain") de l'INDICE lui-même — DISTINCT de la skewness INDIVIDUELLE des
titres du #84 (sélection stock-level) et de la dispersion/corrélation
cross-sectionnelles des #78/#90 (mesurées entre titres à un instant
donné, pas sur la série temporelle d'un seul actif) — signale un
contexte plus favorable à l'amplification de l'exposition, par analogie
directe avec le mécanisme de régime calme du #9 (FAIL 2/5) mais avec un
estimateur différent (skewness au lieu de vol réalisée) — même logique
que le #87 qui a renversé la conclusion du #9 avec le range intra-séance.

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#87.
- Signal : skewness échantillon (formule G1 corrigée du biais de
  Fisher-Pearson, identique à `pandas.Series.rolling().skew()`, déjà
  validée au #84) des rendements log quotidiens de l'INDICE sur une
  fenêtre roulante `SKEW_WINDOW=60` jours (même fenêtre que le #84/#15,
  réutilisée par cohérence).
- Régime "sain" : skewness(t-1) dans le tercile SUPÉRIEUR (skewness la
  MOINS négative / la plus positive) de sa distribution causale
  expansive (percentile calculé uniquement sur l'historique disponible
  jusqu'à t-1, méthode identique au #9/#87), après un warm-up de
  `WARMUP=252` séances.
- Position : **CAP=2.0x** les jours de régime sain, **1.0x** sinon
  (mécanisme binaire simple, identique au #9/#31/#87, pas de
  vol-targeting hiérarchique).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#87). n_trials=1
(SKEW_WINDOW=60j identique au #15/#84, WARMUP=252j et tercile
identiques au #9/#87, CAP=2.0x identique à la famille, aucune grille
testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant
`nonml_index_skewness_regime_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py index_skewness_regime_overlay`.
