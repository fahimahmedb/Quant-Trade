# Audit adversarial — Overlay de tendance par le temps depuis le dernier plus haut

## 1. Recalcul indépendant de days_since_high (np.maximum.accumulate vectorisé)

| Marché | Écart max absolu |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — days_since_high confirmé par recalcul indépendant sur les 5 marchés.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes, NDX)

Écart sur days_since_high calculé à des dates antérieures à la mutation : 0
**OK — aucune fuite, le passé est bien inchangé.**
