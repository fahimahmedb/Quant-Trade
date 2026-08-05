# Résultat — Overlay vol-targeting gaté par l'autocorrélation à un seul retard (ACF lag-1) glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si l'ACF(1) glissante 252j est ≥ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 504e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +73.6% | -24.3% | +1.00 | +79.3% | -24.3% | 36.1% | 1.13x | non | OUI |
| NDX (40 ans) | +0.49 | +3669.6% | -82.9% | +0.49 | +4087.7% | -82.9% | 28.1% | 1.12x | non | OUI |
| Russell 2000 | +0.35 | +591.6% | -59.9% | +0.35 | +664.0% | -60.2% | 34.1% | 1.18x | OUI | OUI |
| S&P 500 | +0.45 | +3109.4% | -56.8% | +0.47 | +5487.2% | -58.9% | 40.6% | 1.26x | OUI | OUI |
| DAX | +0.30 | +189.5% | -59.7% | +0.29 | +174.1% | -60.5% | 28.9% | 1.14x | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
