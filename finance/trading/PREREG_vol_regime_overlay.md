# Pré-enregistrement — Barbell : overlay de levier sur régime de volatilité calme

**Committé AVANT tout calcul.** Cycle #9 du backlog non-ML (remplace la
variante ToM déjà couverte au cycle #8 — teste plutôt la variante
"régime de volatilité" pour éviter une redondance directe). Soumis à la
règle de succès renforcée.

## Hypothèse

Plutôt qu'une fenêtre calendaire, utiliser le RÉGIME DE VOLATILITÉ
réalisée pour moduler le levier : ajouter du levier quand la volatilité
récente est CALME (tercile inférieur, causal), rester à 1.0x sinon.
Intuition Kelly-like (f\*=μ/σ² — plus la vol est faible, plus un même
budget de risque supporte de levier), mais implémentée ici SANS aucun
modèle GARCH (pas de refit lourd, pure vol réalisée roulante, hors ML).

## Définition (fixée ici, avant tout résultat)

- Vol réalisée = écart-type des rendements quotidiens sur les 20
  dernières séances, calculée à J-1 (causal, aucune fuite).
- **Seuil causal expansif** : à chaque jour *t* (après un warmup de 252
  séances), le tercile inférieur est calculé sur la distribution de la
  vol réalisée observée jusqu'à *t-1* UNIQUEMENT (fenêtre expansive,
  jamais sur le futur ni sur l'échantillon complet).
- Position = **1.0x en permanence**, **CAP = 2.0x** les jours où la vol
  réalisée (J-1) est dans le tercile inférieur causal.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition de régime.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), fenêtre testable
à partir de 252 séances de warmup.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0, fenêtre 20j, warmup 252j fixés une fois).

## Anti-cheat

Ce fichier committé avant `nonml_vol_regime_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py vol_regime_overlay`.
