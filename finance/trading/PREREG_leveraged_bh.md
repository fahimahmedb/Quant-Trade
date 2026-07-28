# Pré-enregistrement — Buy & Hold levé en continu (CAP=2.0x)

**Committé AVANT tout calcul.** Cycle #10 du backlog non-ML. Soumis à la
règle de succès renforcée. Complète (sans dupliquer) l'analyse Kelly
antérieure (`finance/trading/results/analysis_kelly_criterion.md`, hors
du backlog non-ML) par un test formel pré-enregistré avec critère
Sharpe+rendement chiffré, sur les 5 marchés.

## Hypothèse

Un levier fixe modéré (CAP=2.0x, même valeur que les cycles #8/#9,
cohérence inter-cycles), appliqué en permanence à Buy & Hold, bat-il
Buy & Hold 1x en Sharpe ET en rendement total net de coûts ? Test
descriptif d'une règle d'allocation, pas une découverte d'edge — déjà
discuté avec l'utilisateur que le résultat dépend structurellement du
ratio μ/σ² propre à chaque marché (décroissance par la volatilité si
μ insuffisant).

## Définition (fixée ici, avant tout résultat)

- Position = **CAP = 2.0x constante**, rebalancement quotidien implicite
  (le levier reste 2.0x chaque jour, pas de retour à 1x).
- **Coûts** : 5 bps à l'entrée uniquement (position jamais modifiée
  ensuite — un seul changement de 0 à 2.0x au premier jour).
- **Référence** : Buy & Hold 1x classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

Le Buy&Hold levé doit battre le Buy&Hold 1x **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts, sur **au
moins 4 des 5 marchés**. n_trials=1 (CAP=2.0 fixé une fois, cohérent avec
les cycles #8/#9, pas choisi après résultat).

## Anti-cheat

Ce fichier committé avant `nonml_leveraged_bh_backtest.py`, vérification
via `nonml_anti_cheat_check.py leveraged_bh`.
