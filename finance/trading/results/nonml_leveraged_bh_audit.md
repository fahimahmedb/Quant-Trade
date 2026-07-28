# Audit adversarial — Buy & Hold levé en continu

## Vérification de la propriété mathématique attendue (Sharpe quasi-invariant au levier constant)

| Marché | Sharpe BH 1x (sans coût) | Sharpe levé x2 (sans coût) | Écart |
|---|---|---|---|
| Composite (5 ans) | +0.518794 | +0.518794 | 0.00e+00 |
| NDX (40 ans) | +0.528552 | +0.528552 | 0.00e+00 |
| Russell 2000 | +0.341261 | +0.341261 | 0.00e+00 |
| S&P 500 | +0.451187 | +0.451187 | 0.00e+00 |
| DAX | +0.250969 | +0.250969 | 0.00e+00 |

**OK — invariance confirmée (le Sharpe est bien mathématiquement inchangé par un levier constant, hors coûts). Le FAIL du backtest principal vient donc uniquement du coût d’entrée + du critère de rendement, pas d’un edge manqué.**

**Conclusion méthodologique** : ce test est structurellement quasi impossible à faire PASSer sur le critère Sharpe pour un levier constant sans dimensionnement adaptatif — pas une découverte, une propriété mathématique du design (cohérent avec la discussion Kelly/vol-targeting déjà eue : seul un LEVIER VARIABLE, informé par μ/σ² ou un régime, peut espérer améliorer le Sharpe).
