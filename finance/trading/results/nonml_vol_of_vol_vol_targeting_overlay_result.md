# Résultat — Overlay vol-targeting gaté par la vol-de-la-vol glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si l'écart-type glissant 252j de la vol réalisée est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable = à partir de la 525e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.10 | +79.5% | -24.3% | +1.13 | +90.8% | -24.3% | 27.7% | 1.10x | OUI | OUI |
| NDX (40 ans) | +0.54 | +6044.4% | -82.9% | +0.58 | +11242.9% | -82.9% | 31.1% | 1.14x | OUI | OUI |
| Russell 2000 | +0.35 | +585.9% | -59.9% | +0.34 | +574.7% | -60.8% | 32.3% | 1.17x | non | non |
| S&P 500 | +0.45 | +3100.9% | -56.8% | +0.48 | +6468.1% | -60.2% | 46.4% | 1.32x | OUI | OUI |
| DAX | +0.29 | +168.5% | -59.7% | +0.30 | +190.4% | -60.5% | 41.0% | 1.21x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
