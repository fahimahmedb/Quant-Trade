# Audit adversarial — Vol-targeting défensif, critère Calmar

## 1. Recalcul indépendant de la position (écart-type manuel, boucle Python, sans pandas.rolling)

| Date (indice) | Écart absolu |
|---|---|
| 500 | 0.00e+00 |
| 2000 | 0.00e+00 |
| 3500 | 9.99e-16 |
| 5000 | 0.00e+00 |
| 6500 | 0.00e+00 |
| 8000 | 0.00e+00 |
| 9500 | 0.00e+00 |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données NDX les plus récentes)

Écart max sur les positions passées (avant mutation) : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Recalcul manuel du Calmar (confirme le verdict 4/5)

| Marché | Calmar BH recalculé | Calmar overlay recalculé | Concorde avec le résultat |
|---|---|---|---|
| Composite (5 ans) | 0.260 | 0.324 | OUI |
| NDX (40 ans) | 0.077 | 0.145 | OUI |
| Russell 2000 | 0.081 | 0.105 | OUI |
| S&P 500 | 0.095 | 0.103 | OUI |
| DAX | 0.042 | 0.041 | non |

**OK — 4/5 confirmé, cohérent avec le résultat committé.**
