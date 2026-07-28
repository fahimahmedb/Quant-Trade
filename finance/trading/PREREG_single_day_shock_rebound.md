# Pré-enregistrement — Overlay levé sur rebond après choc 1 séance (niveau indice)

**Committé AVANT tout calcul.** Cycle #24 du backlog non-ML. Variante du
cycle #22 (repli 3j/-3% -> FAIL catastrophique, l'overlay se retrouvait
levé pendant des krachs prolongés) : ici le déclencheur est un choc
**plus brutal mais strictement ponctuel** (une seule séance, pas un repli
étalé sur 3 jours), pour tester si la nature "un seul jour" change la
conclusion (hypothèse de rebond technique post-panique intrajournalière,
différente de la mean-reversion de marché sur plusieurs jours testée au
#22).

## Hypothèse

Une chute brutale (≥5%) concentrée sur une seule séance de bourse
(événement de type panique/liquidation plutôt que tendance baissière
installée) est suivie d'un rebond technique à très court terme, plus
fiable qu'un repli étalé sur plusieurs séances (#22).

## Définition (fixée ici, avant tout résultat)

- Choc = rendement log de clôture-à-clôture de la séance t ≤ **-5%**
  (une seule séance, pas cumulé).
- Dès qu'un choc est détecté au jour t (décision prise avec les données
  disponibles à la clôture de t, appliquée au rendement t→t+1, même
  convention causale que tous les cycles précédents), position =
  **CAP = 2.0x** pendant les **5** séances suivantes (fenêtre de rebond,
  même longueur que #22 pour isoler l'effet du seul changement de
  déclencheur), 1.0x sinon. Si un nouveau choc survient pendant la
  fenêtre déjà active, la fenêtre est relancée à 5 séances (même logique
  de re-déclenchement que #13/#22).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents, seuil -5% et fenêtre 5j fixés a priori, aucune grille testée
avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_single_day_shock_rebound_backtest.py`,
vérification via `nonml_anti_cheat_check.py single_day_shock_rebound`.
