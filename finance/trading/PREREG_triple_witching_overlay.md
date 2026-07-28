# Pré-enregistrement — Overlay levé "triple witching"

**Committé AVANT tout calcul.** Cycle #26 du backlog non-ML. Le 3e
vendredi de mars/juin/septembre/décembre correspond à l'expiration
trimestrielle simultanée des options et futures sur indices (triple
witching), documentée dans la littérature comme associée à un pic de
volume et de volatilité de fin de séance. Détection **data-driven**
(rang du vendredi dans le mois via la calendrier de trading réel, pas de
dates codées en dur), comme au cycle #7.

## Hypothèse

L'activité de rebalancement massif autour du triple witching génère un
mouvement de prix directionnel exploitable (pas seulement du bruit), sur
la séance elle-même et le lendemain (retour à la normale après le pic de
volume).

## Définition (fixée ici, avant tout résultat)

- Mois concernés = mars, juin, septembre, décembre (4 mois/an,
  expiration trimestrielle standard).
- Jour witching = le **3e vendredi de bourse** de ces mois (rang
  ascendant des vendredis du mois, calculé sur les séances réellement
  ouvertes, donc data-driven même si un vendredi est férié).
- Position = **1.0x en permanence**, SAUF le jour witching **et** la
  séance suivante où position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_triple_witching_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py triple_witching_overlay`.
