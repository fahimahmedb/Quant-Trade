# Pré-enregistrement — Overlay levé filtre de tendance SMA200

**Committé AVANT tout calcul.** Cycle #29 du backlog non-ML. Filtre de
tendance simple (Faber 2007, "A Quantitative Approach to Tactical Asset
Allocation") : position au-dessus/au-dessous de la moyenne mobile 200
jours comme proxy de régime haussier/baissier. Jamais testé jusqu'ici
dans ce backlog (tous les cycles précédents étaient calendaires ou basés
sur un choc ponctuel de prix).

## Hypothèse

Un régime où le prix de clôture est au-dessus de sa moyenne mobile 200
jours est statistiquement associé à une meilleure persistance des
tendances haussières (moins de krachs violents que sous la moyenne) —
une exposition additionnelle pendant ce régime devrait améliorer Sharpe
et rendement sans les pertes catastrophiques d'un simple "tout ou rien"
(design flat déjà écarté par les enseignements #2/#6/#8).

## Définition (fixée ici, avant tout résultat)

- SMA200 = moyenne mobile simple des 200 dernières clôtures (fenêtre
  causale, aucune donnée future). Les 200 premières séances de chaque
  marché (sans SMA200 valide) restent hors échantillon testable.
- Position = **1.0x en permanence**, SAUF si la clôture du jour t est
  **strictement au-dessus** de sa SMA200 au jour t, où position =
  **CAP = 2.0x**. Décision prise à la clôture de t, appliquée au
  rendement t→t+1 (même convention causale que tous les cycles
  précédents).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique (sur le même sous-échantillon
  testable, à partir du 201e jour).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`). Note : le
Composite (5 ans, 1251 séances) perd ~16% de son échantillon aux 200
premiers jours ; les 4 autres marchés (longs historiques) ne sont
quasiment pas affectés.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x et fenêtre SMA200 fixés a priori,
cohérents avec la littérature de référence, aucune grille testée avant
ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_sma200_trend_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py sma200_trend_overlay`.
