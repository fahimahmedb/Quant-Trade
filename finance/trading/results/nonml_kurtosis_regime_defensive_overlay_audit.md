# Audit adversarial — Overlay défensif gaté par la kurtosis de l'indice

## 1. Recalcul indépendant de la kurtosis roulante (formule explicite, NDX)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 1.89e-15 |
| 760 | 8.60e-16 |
| 1460 | 4.44e-16 |
| 2160 | 2.22e-15 |
| 2860 | 5.55e-16 |
| 3560 | 3.05e-16 |
| 4260 | 1.11e-15 |
| 4960 | 3.89e-16 |
| 5660 | 5.34e-16 |
| 6360 | 1.55e-15 |
| 7060 | 4.44e-15 |
| 7760 | 3.11e-15 |
| 8460 | 5.77e-15 |
| 9160 | 6.11e-16 |
| 9860 | 1.55e-15 |

**OK — kurtosis confirmée par recalcul indépendant (formule Fisher corrigée du biais).**

## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**
