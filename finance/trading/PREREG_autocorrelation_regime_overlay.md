# Pré-enregistrement — Overlay de régime par l'autocorrélation des rendements

**Committé AVANT tout calcul.** Cycle #95 du backlog non-ML.

## Hypothèse

L'Étape A du projet documente, via le ratio de variance de
Lo-MacKinlay, un retour à la moyenne FAIBLE mais statistiquement
détecté sur NDX (40 ans) : VR(5)=0,89, z*=−2,68, p=0,007 (random walk
rejeté), alors que sur le Composite (5 ans) le random walk n'est PAS
rejeté. Ce cycle exploite directement cette observation en testant si
l'autocorrélation lag-1 GLISSANTE des rendements quotidiens de
l'indice — jamais utilisée comme signal de trading dans ce backlog —
porte une information de régime exploitable : un régime
d'autocorrélation POSITIVE (momentum à court terme dominant) pourrait
signaler un contexte plus favorable à l'amplification qu'un régime
d'autocorrélation négative (mean-reversion dominant, où amplifier une
tendance risquerait un retournement).

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#87/#92/#93.
- Signal : autocorrélation d'ordre 1 (lag-1, coefficient de Pearson
  entre `r(t)` et `r(t-1)`) des rendements log quotidiens de l'INDICE
  sur une fenêtre roulante `AUTOCORR_WINDOW=60` jours (même fenêtre que
  le #92/#93/#15/#84, réutilisée par cohérence).
- Régime "momentum" : autocorrélation(t-1) dans le tercile SUPÉRIEUR
  (la PLUS POSITIVE) de sa distribution causale expansive (percentile
  calculé uniquement sur l'historique disponible jusqu'à t-1, méthode
  identique au #9/#87/#92/#93), après un warm-up de `WARMUP=252`
  séances.
- Position : **CAP=2.0x** les jours de régime momentum, **1.0x** sinon
  (mécanisme binaire simple, identique au #9/#31/#87/#92).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#87/#92). n_trials=1
(AUTOCORR_WINDOW=60j identique au #92/#93, WARMUP=252j et tercile
identiques au #9/#87/#92/#93, CAP=2.0x identique à la famille, aucune
grille testée avant ce résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant
`nonml_autocorrelation_regime_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py autocorrelation_regime_overlay`.
