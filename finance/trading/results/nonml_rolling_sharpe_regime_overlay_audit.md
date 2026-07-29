# Audit adversarial — Overlay de régime par le Sharpe glissant de l'indice

## 1. Recalcul indépendant du Sharpe glissant (formule manuelle explicite, NDX)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 0.00e+00 |
| 760 | 4.66e-15 |
| 1460 | 5.33e-15 |
| 2160 | 1.42e-14 |
| 2860 | 1.20e-14 |
| 3560 | 4.44e-15 |
| 4260 | 8.88e-16 |
| 4960 | 4.27e-15 |
| 5660 | 3.11e-15 |
| 6360 | 2.49e-14 |
| 7060 | 7.37e-14 |
| 7760 | 3.72e-15 |
| 8460 | 1.31e-13 |
| 9160 | 1.04e-14 |
| 9860 | 1.11e-14 |

**OK — Sharpe glissant confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**
