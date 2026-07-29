# Pré-enregistrement — Overlay DÉFENSIF gaté par la kurtosis de l'indice

**Committé AVANT tout calcul.** Cycle #93 du backlog non-ML.

## Hypothèse

L'Étape A du projet documente un effet ARCH massif et des queues
épaisses (ν≈4,8 non conditionnel) sur les deux échantillons étudiés.
Ce cycle teste si un régime de kurtosis ÉLEVÉE (risque de queue accru,
mouvements extrêmes plus fréquents que la normale) de l'INDICE
lui-même — distinct de la vol réalisée (#9/#31, échec/rejet) et du
range intra-séance (#87, PASS) — précède des mouvements qu'il vaudrait
mieux éviter d'AMPLIFIER. Contrairement aux mécanismes #9/#87/#92 (qui
amplifient en régime "sain"), ce cycle teste une porte DÉFENSIVE :
RÉDUIRE l'exposition (jamais l'amplifier) en régime de kurtosis élevée,
symétrique dans l'esprit du #44 (vol-targeting défensif uniquement,
FAIL — Sharpe amélioré mais rendement structurellement inférieur faute
d'amplification), mais ici gaté par un régime binaire plutôt qu'un
scaling continu.

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #9/#29/#31/#87/#92.
- Signal : kurtosis échantillon en excès (définition Fisher, identique
  à `pandas.Series.rolling().kurt()`) des rendements log quotidiens de
  l'INDICE sur une fenêtre roulante `KURT_WINDOW=60` jours (même
  fenêtre que le #92/#15/#84, réutilisée par cohérence).
- Régime de kurtosis élevée : kurtosis(t-1) dans le tercile SUPÉRIEUR
  de sa distribution causale expansive (percentile calculé uniquement
  sur l'historique disponible jusqu'à t-1, méthode identique au
  #9/#87/#92), après un warm-up de `WARMUP=252` séances.
- Position : **CUT=0.5x** les jours de régime de kurtosis élevée
  (réduction défensive, JAMAIS d'amplification au-dessus de 1.0x),
  **1.0x** sinon.
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #9/#29/#31/#44). n_trials=1
(KURT_WINDOW=60j identique au #92, WARMUP=252j et tercile identiques
au #9/#87/#92, CUT=0.5x fixé ici a priori par symétrie avec le CAP=2.0x
habituel — ni "0" trop extrême, ni proche de 1.0x rendant le test non
informatif —, aucune grille testée avant ce résultat).

**Attente honnête déclarée a priori** : par analogie directe avec le
#44 (design purement défensif, jamais d'amplification), un FAIL est
l'issue la plus probable pour la jambe rendement, même si le Sharpe
s'améliore et le MDD se réduit — signalé ici pour la traçabilité, pas
pour biaiser l'interprétation du résultat qui sera rapporté tel quel.

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CUT ∈ {0.3x, 0.4x, 0.5x, 0.6x,
0.7x} (grille symétrique autour de 0.5x, analogue à la grille CAP
habituelle mais côté défensif).

## Anti-cheat

Ce fichier committé avant
`nonml_kurtosis_regime_defensive_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py kurtosis_regime_defensive_overlay`.
