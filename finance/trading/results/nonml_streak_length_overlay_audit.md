# Audit adversarial — Overlay de tendance par la longueur de série directionnelle

## 1. Recalcul indépendant du masque de streak (approche vectorisée alternative)

| Marché | Écart (nb jours différents) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque de streak confirmé par recalcul indépendant sur les 5 marchés.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)

Écart de masque sur les séances antérieures à la mutation : 0
**OK — aucune fuite, le passé est bien inchangé.**
