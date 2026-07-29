# Audit adversarial — Overlay de régime par l'autocorrélation lag-1 de l'indice

## 1. Recalcul indépendant de l'autocorrélation lag-1 (formule de Pearson manuelle, NDX)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 5.55e-17 |
| 760 | 5.26e-18 |
| 1460 | 8.33e-17 |
| 2160 | 1.39e-17 |
| 2860 | 2.43e-17 |
| 3560 | 2.78e-17 |
| 4260 | 1.39e-17 |
| 4960 | 8.33e-17 |
| 5660 | 0.00e+00 |
| 6360 | 1.11e-16 |
| 7060 | 4.16e-17 |
| 7760 | 6.94e-18 |
| 8460 | 2.78e-17 |
| 9160 | 0.00e+00 |
| 9860 | 0.00e+00 |

**OK — autocorrélation confirmée par recalcul indépendant (formule de Pearson manuelle).**

## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**
