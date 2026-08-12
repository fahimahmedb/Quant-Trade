# Audit adversarial — Turn-of-Month overlay de levier

## 1. Recalcul indépendant de l'équité finale (NDX, boucle explicite vs vectorisé)

Équité finale (boucle) : 560.1686 (+55916.9%)
Équité finale (vectorisé, backtest principal) : 8497.4286 (+849642.9%)
Écart : 7.94e+03
**ÉCHEC — divergence.**

## 2. Valeurs de position (doivent être exactement {1.0, 2.0})

Valeurs observées : [np.float64(1.0), np.float64(2.0)]
**OK.**

## 3. Cohérence du masque ToM avec le cycle #2 (même fonction, pas de divergence)

Fraction de jours en fenêtre ToM (NDX) : 33.4% -- comparable au 33.4% déjà rapporté et audité au cycle #2 (`results/nonml_turn_of_month_audit.md`), confirmant l'absence de divergence de définition entre les deux cycles.
