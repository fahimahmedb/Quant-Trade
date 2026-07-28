# Pré-enregistrement — Window Dressing de fin de trimestre

**Committé AVANT tout calcul.** Cycle #19 du backlog non-ML. Soumis à la
règle de succès renforcée. Construit en overlay (leçon des cycles
#8/#11/#12/#17).

## Hypothèse

Les gestionnaires de fonds ajustent leurs portefeuilles en fin de
trimestre pour la présentation aux clients ("window dressing" —
littérature sur le sujet, ex. Lakonishok et al. 1991), créant une
pression acheteuse sur les gagnants récents en fin de trimestre. Ici
testé au niveau indice (pas de sélection de titres) : simple effet de
calendrier sur les 3 derniers jours de chaque trimestre.

## Définition (fixée ici, avant tout résultat)

- Fenêtre = **3 derniers jours de bourse de chaque trimestre** (fin
  mars, juin, septembre, décembre), calculée via rang descendant par
  groupby trimestriel (même méthode que les cycles #2/#8, jamais de
  calendrier codé en dur).
- Position = **1.0x en permanence** (comme Buy & Hold), SAUF pendant
  cette fenêtre où position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position, ~8
  transitions/an (2 par trimestre × 4 trimestres).
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_quarter_end_window_dressing_backtest.py`,
vérification via `nonml_anti_cheat_check.py quarter_end_window_dressing`.
