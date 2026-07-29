# Audit adversarial — Overlay défensif EWMA + ensemble 3 moteurs

## 1. Recalcul indépendant du chemin EWMA (récursion manuelle, boucle Python explicite)

| Date (indice) | Vol annualisée originale | Vol annualisée recalculée | Écart relatif |
|---|---|---|---|
| 755 | -- | 0.1358 | position: 0.00e+00 |
| 1250 | -- | 0.2958 | position: 1.11e-16 |
| 3750 | -- | 0.4852 | position: 5.55e-17 |
| 6750 | -- | 0.2084 | position: 1.11e-16 |

**OK — chemin EWMA confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données NDX les plus récentes)

Écart max sur les positions passées (avant mutation) : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Recalcul indépendant de la moyenne à 3 (boucle Python explicite)

**OK — moyenne à 3 confirmée par recalcul indépendant (7 dates, à partir des 3 npz sources séparées).**
