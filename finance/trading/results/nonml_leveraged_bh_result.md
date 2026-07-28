# Résultat — Buy & Hold levé en continu (pré-enregistré, règle renforcée)

Position = CAP=2.0x constante, rebalancement quotidien implicite.

| Marché | BH 1x Sharpe | BH 1x Rdt total | BH 1x MDD | Levé x2 Sharpe | Levé x2 Rdt total | Levé x2 MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +57.6% | -36.4% | +0.52 | +92.6% | -59.5% | non | OUI |
| NDX (40 ans) | +0.53 | +6599.5% | -82.9% | +0.53 | +28214.1% | -97.1% | non | OUI |
| Russell 2000 | +0.34 | +602.0% | -59.9% | +0.34 | +669.6% | -83.9% | non | OUI |
| S&P 500 | +0.45 | +3369.2% | -56.8% | +0.45 | +21177.8% | -81.3% | non | OUI |
| DAX | +0.25 | +130.5% | -72.7% | +0.25 | +35.8% | -92.5% | non | non |

**0/5 marchés où le levé x2.0 bat Buy&Hold 1x en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**

**Lecture honnête** : cohérent avec la discussion déjà eue avec l'utilisateur (décroissance par la volatilité) — un levier constant sans dimensionnement adaptatif dépend entièrement du ratio μ/σ² propre à chaque marché, pas d'un edge de timing.
