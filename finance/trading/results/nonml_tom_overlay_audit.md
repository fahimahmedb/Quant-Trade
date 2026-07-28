# Audit adversarial — Turn-of-Month overlay de levier

## 1. Recalcul indépendant de l'équité finale (NDX, boucle explicite vs vectorisé)

Équité finale (boucle) : 560.1686 (+55916.9%)
Équité finale (vectorisé, backtest principal) : 560.1686 (+55916.9%)
Écart : 0.00e+00
**OK — concordance parfaite, le chiffre extrême est mathématiquement confirmé (composition à 40 ans avec levier partiel).**

## 2. Valeurs de position (doivent être exactement {1.0, 2.0})

Valeurs observées : [1.0, 2.0]
**OK.**

## 3. Cohérence du masque ToM avec le cycle #2 (même fonction, pas de divergence)

Fraction de jours en fenêtre ToM (NDX) : 33.4% -- comparable au 33.4% déjà rapporté et audité au cycle #2 (`results/nonml_turn_of_month_audit.md`), confirmant l'absence de divergence de définition entre les deux cycles.
