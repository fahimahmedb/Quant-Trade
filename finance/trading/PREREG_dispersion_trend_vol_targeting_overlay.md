# Pré-enregistrement — Overlay vol-targeting gaté par double porte dispersion ET tendance

**Committé AVANT tout calcul.** Cycle #81 du backlog non-ML. Combine
DEUX portes simultanées (intersection stricte, PAS une union) pour le
mécanisme hiérarchique vol-targeting : la dispersion cross-sectionnelle
NDX-100 (#78, PASS SEUL) ET la tendance 52w-high indicielle (#47, PASS
SEUL). Teste si le résultat négatif du #61 (combiner un signal
directionnel avec un signal non-directionnel DILUE l'edge) se
généralise aussi quand les DEUX portes sont individuellement des PASS —
contrairement au #61 où la porte non-directionnelle (vol faible, #58)
était elle-même un FAIL seule.

## Hypothèse

Le #61 a montré qu'ajouter une porte non-directionnelle (#58, FAIL
seule) en AND à une porte directionnelle qui fonctionne (#47, PASS
seule) dilue l'edge plutôt que de l'améliorer, car la porte
non-directionnelle retire des jours de tendance haussière sans apporter
de sélectivité utile. Ici, contrairement au #61, la dispersion (#78)
est elle-même un PASS quand elle est utilisée seule — teste si combiner
deux portes qui fonctionnent chacune séparément produit une amélioration
(les deux signaux se renforcent) ou si le même écueil de rétrécissement
de fenêtre observé au #61 se reproduit malgré tout.

## Définition (fixée ici, avant tout résultat)

- Porte dispersion = dispersion cross-sectionnelle NDX-100 ≥ sa médiane
  glissante 252j (identique au #78, MEDIAN_WINDOW=252, MIN_LISTED=10).
- Porte tendance = proximité ≥95% du plus haut glissant 252j de l'indice
  NDX-100 (identique au #37/#47, INDEX_LOOKBACK=252,
  INDEX_THRESHOLD=0.95).
- Porte combinée = dispersion ET tendance (intersection stricte).
- Quand la porte combinée est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%**, **CAP = 2,0x**,
  fenêtre de vol **VOL_WINDOW=20j** (paramètres identiques aux cycles
  #46/#47/#78, aucun retuning).
- Quand la porte combinée est inactive : position = **1,0x**.
- Échantillon restreint à la période où la dispersion cross-sectionnelle
  est disponible (~2021+, leçon des cycles #77/#78).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/pead/prices/*.json` (titres NDX-100, pour la dispersion) et
`data/nasdaq100_daily.txt` (indice, pour le rendement testé et la
tendance), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Un seul
marché testé (NDX), comme aux #77/#78 (signal dérivé des constituants
NDX-100). n_trials=1 (tous les paramètres repris à l'identique des
cycles déjà validés, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_dispersion_trend_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py dispersion_trend_vol_targeting_overlay`.
