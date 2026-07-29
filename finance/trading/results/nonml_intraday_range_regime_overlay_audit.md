# Audit adversarial — Overlay de régime par le range intra-séance

## 1. Recalcul indépendant du range moyen roulant (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 20 | 0.00e+00 |
| 520 | 0.00e+00 |
| 1020 | 1.73e-18 |
| 1520 | 0.00e+00 |
| 2020 | 0.00e+00 |
| 2520 | 0.00e+00 |
| 3020 | 6.94e-18 |
| 3520 | 3.47e-18 |
| 4020 | 0.00e+00 |
| 4520 | 6.94e-18 |
| 5020 | 1.73e-18 |
| 5520 | 0.00e+00 |
| 6020 | 0.00e+00 |
| 6520 | 3.47e-18 |
| 7020 | 1.73e-18 |
| 7520 | 1.73e-18 |
| 8020 | 1.73e-18 |
| 8520 | 0.00e+00 |
| 9020 | 0.00e+00 |
| 9520 | 0.00e+00 |
| 10020 | 0.00e+00 |

**OK — range moyen confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des OHLC des 20% de données les plus récentes)

Écart de classification de régime sur 7936 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Fréquence du régime calme détecté (NDX, hors warmup) : 35.5% du temps.
