# Pré-enregistrement — Effet janvier small-cap (overlay levé)

**Committé AVANT tout calcul.** Cycle #12 du backlog non-ML. Soumis à la
règle de succès renforcée. Construit en OVERLAY (comme les cycles #8/#11,
pas flat-hors-fenêtre comme #2/#6/#7) — leçon tirée des cycles précédents
où une exposition partielle ne peut structurellement pas battre le
rendement composé de Buy&Hold.

## Hypothèse

Rozeff & Kinney (1976) : rendement de janvier historiquement plus élevé
pour les small-caps que pour les large-caps ("January effect", souvent
attribué à la vente à perte fiscale de fin d'année suivie d'un rachat).
Testé ici sur Russell 2000 (proxy small-cap déjà dans le projet).

## Définition (fixée ici, avant tout résultat)

- Position = **1.0x en permanence** sur Russell 2000 (comme Buy & Hold),
  SAUF durant le mois de **janvier** où position = **CAP = 2.0x**
  (cohérent avec les cycles #8/#9/#10/#11, jamais retuné).
- **Coûts** : 5 bps par unité de changement de position, 2
  transitions/an (entrée/sortie janvier).
- **Référence** : Buy & Hold Russell 2000 classique (1.0x en permanence).

## Univers et période

Russell 2000 uniquement (`data/russell2000_daily.txt`), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay janvier doit battre Buy & Hold Russell 2000 **simultanément**
en Sharpe annualisé net de coûts ET en rendement total net de coûts.
n_trials=1 (un seul marché testé ici — Russell 2000 est le proxy
small-cap du projet, pas une grille sur plusieurs indices).

## Anti-cheat

Ce fichier committé avant `nonml_january_smallcap_backtest.py`,
vérification via `nonml_anti_cheat_check.py january_smallcap`.
