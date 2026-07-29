# Audit adversarial — Overlay de régime par la skewness de l'indice

## 1. Recalcul indépendant de la skewness roulante (formule G1 explicite, NDX)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 1.53e-16 |
| 760 | 2.72e-15 |
| 1460 | 1.39e-15 |
| 2160 | 1.31e-15 |
| 2860 | 8.88e-16 |
| 3560 | 4.16e-16 |
| 4260 | 5.55e-17 |
| 4960 | 2.28e-15 |
| 5660 | 6.04e-16 |
| 6360 | 2.83e-15 |
| 7060 | 5.22e-15 |
| 7760 | 2.22e-15 |
| 8460 | 4.39e-15 |
| 9160 | 8.12e-16 |
| 9860 | 1.22e-15 |

**OK — skewness confirmée par recalcul indépendant (formule G1).**

## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**
