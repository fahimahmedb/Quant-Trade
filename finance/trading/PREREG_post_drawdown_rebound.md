# Pré-enregistrement — Overlay levé post-drawdown extrême

**Committé AVANT tout calcul.** Cycle #13 du backlog non-ML. Distinct du
reversal hebdomadaire du cycle #5 (FAIL catastrophique) : ici, niveau
INDICE (pas titre individuel), choc plus extrême (drawdown -10%, pas un
simple rendement négatif), horizon de rebond plus long (20j, pas 5j).
Soumis à la règle de succès renforcée, construit en overlay (leçon des
cycles #8/#11/#12).

## Hypothèse

Après un choc de marché sévère au niveau indice, la phase de rebond
qui suit tend à être plus favorable que la moyenne — hypothèse
distincte du reversal titre-par-titre court terme déjà réfuté (cycle #5).

## Définition (fixée ici, avant tout résultat)

- **Détection du choc** : à chaque jour *t*, drawdown depuis le plus haut
  des 20 séances précédentes (`close_t / max(close_{t-20:t}) - 1`,
  causal). Choc détecté si ce drawdown ≤ **-10%**.
- Dès qu'un choc est détecté au jour *t*, position = **CAP = 2.0x**
  pendant les **20 séances suivantes** (t+1 à t+20), retour à 1.0x
  ensuite (ou nouveau choc qui prolonge/relance la fenêtre de levier).
- **Coûts** : 5 bps par unité de changement de position.
- **Référence** : Buy & Hold classique (1.0x en permanence).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (seuil -10%, fenêtre de rebond 20j, CAP=2.0 fixés
une fois).

## Anti-cheat

Ce fichier committé avant `nonml_post_drawdown_rebound_backtest.py`,
vérification via `nonml_anti_cheat_check.py post_drawdown_rebound`.
