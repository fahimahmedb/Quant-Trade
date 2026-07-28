# Pré-enregistrement — Overlay levé proximité du plus haut 52-semaines (niveau indice)

**Committé AVANT tout calcul.** Cycle #37 du backlog non-ML. Signal de
tendance encore différent des moyennes mobiles (#29/#34/#36) : la
proximité au plus haut glissant sur 252 séances (52 semaines), déjà
utilisée comme critère de SÉLECTION DE TITRES au cycle #4 (momentum
George & Hwang 2004), testée ici comme signal de RÉGIME au niveau
INDICE (pas de sélection de titres).

## Hypothèse

Un indice proche de son plus haut sur 1 an (régime de force relative)
est statistiquement plus susceptible de poursuivre sa tendance
(continuation de momentum documentée par George & Hwang 2004, déjà
validée en sélection de titres au #4) — hypothèse testée ici comme
filtre de régime global plutôt que critère de sélection.

## Définition (fixée ici, avant tout résultat)

- Plus haut glissant = maximum des 252 dernières clôtures (fenêtre
  causale, même longueur que le #4).
- Régime "proche du plus haut" = clôture du jour t **≥ 95%** de son plus
  haut glissant 252j au jour t (seuil fixé a priori, cohérent avec la
  littérature du "52-week high momentum").
- Position = **1.0x en permanence**, SAUF les jours en régime "proche du
  plus haut" où position = **CAP = 2.0x**. Décision prise à la clôture
  de t, appliquée au rendement t→t+1.
- Échantillon testable = à partir de la 253e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x, fenêtre 252j et seuil 95% fixés a
priori, aucune grille testée avant ce résultat — le seuil 95% sera
soumis à une grille de robustesse APRÈS le résultat, pas de retuning).

## Anti-cheat

Ce fichier committé avant `nonml_index_52w_high_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py index_52w_high_overlay`.
