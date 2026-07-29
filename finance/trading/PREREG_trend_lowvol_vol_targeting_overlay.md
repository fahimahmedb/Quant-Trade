# Pré-enregistrement — Overlay vol-targeting gaté par tendance ET régime de vol faible (double porte)

**Committé AVANT tout calcul.** Cycle #61 du backlog non-ML. Combine
DEUX portes simultanées (intersection stricte, PAS une union) pour le
mécanisme hiérarchique vol-targeting : la tendance haussière (#47/#37,
qui fonctionne bien seule) ET le régime de volatilité réalisée faible
(#58, qui échoue seul faute de biais directionnel). Teste si ajouter la
condition de vol faible en FILTRE SUPPLÉMENTAIRE au signal directionnel
qui fonctionne déjà réduit le risque de levier en fin de tendance mature
(vol souvent croissante en fin de cycle haussier) sans détruire l'edge.

## Hypothèse

Le #58 a montré qu'un régime de vol faible seul n'est pas directionnel
(FAIL, 2/5). Le #47 a montré que la tendance seule fonctionne très bien
(PASS, 4/5, plateau parfait). Combiner les deux en INTERSECTION (au lieu
d'utiliser l'un ou l'autre séparément) pourrait éviter de lever pendant
les phases de tendance haussière mais de vol déjà croissante — souvent
un signe avant-coureur de retournement (ex. fin de bulle) — réduisant le
risque de rester levé juste avant un choc, potentiellement au prix d'un
edge légèrement réduit (porte plus restrictive que #47 seul).

## Définition (fixée ici, avant tout résultat)

- Porte tendance = proximité ≥95% du plus haut glissant 252j (identique
  au #37/#47, INDEX_LOOKBACK=252, INDEX_THRESHOLD=0.95).
- Porte vol faible = vol_lagged(t) < médiane glissante 252j de
  vol_lagged (identique au #58, VOL_WINDOW=20, MEDIAN_WINDOW=252).
- Porte combinée = tendance ET vol faible (intersection stricte).
- Quand la porte combinée est active : position = **clip(vol_cible /
  vol_lagged(t), 1.0, CAP)**, avec **vol_cible = 20%** et **CAP = 2,0x**
  (paramètres identiques au #46/#47/#57/#58, aucun retuning).
- Quand la porte combinée est inactive : position = **1,0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (tous les paramètres repris à l'identique des
cycles #37/#46/#47/#58 déjà validés, aucune grille testée avant ce
résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_trend_lowvol_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py trend_lowvol_vol_targeting_overlay`.
