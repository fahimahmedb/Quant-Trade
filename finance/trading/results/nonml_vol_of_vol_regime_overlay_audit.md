# Audit adversarial — Overlay de régime par le vol-of-vol de l'indice

## 1. Recalcul indépendant du vol-of-vol (formule manuelle explicite, NDX)

| Date (indice) | Écart absolu |
|---|---|
| 80 | 8.67e-19 |
| 780 | 3.64e-16 |
| 1480 | 2.90e-16 |
| 2180 | 1.31e-16 |
| 2880 | 1.42e-16 |
| 3580 | 6.07e-17 |
| 4280 | 1.65e-16 |
| 4980 | 3.65e-16 |
| 5680 | 1.28e-16 |
| 6380 | 3.44e-16 |
| 7080 | 4.75e-16 |
| 7780 | 2.04e-16 |
| 8480 | 3.48e-16 |
| 9180 | 2.27e-16 |
| 9880 | 6.25e-16 |

**OK — vol-of-vol confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)

Écart de classification de régime sur 7935 jours antérieurs à la mutation (NDX) : 0 jours différents.
**OK — aucune fuite, le passé est bien inchangé.**
