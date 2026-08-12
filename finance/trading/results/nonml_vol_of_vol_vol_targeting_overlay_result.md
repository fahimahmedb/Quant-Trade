# Résultat — Overlay vol-targeting gaté par la vol-de-la-vol glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si l'écart-type glissant 252j de la vol réalisée est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable = à partir de la 525e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.10 | +90.5% | -24.3% | +1.13 | +104.6% | -24.3% | 27.7% | 1.10x | OUI | OUI |
| NDX (40 ans) | +0.54 | +22617.1% | -82.9% | +0.58 | +48420.3% | -82.9% | 31.1% | 1.14x | OUI | OUI |
| Russell 2000 | +0.35 | +1540.6% | -59.9% | +0.34 | +1763.8% | -60.8% | 32.3% | 1.17x | non | OUI |
| S&P 500 | +0.45 | +7228.4% | -56.8% | +0.48 | +20624.0% | -60.2% | 46.4% | 1.32x | OUI | OUI |
| DAX | +0.29 | +391.6% | -59.7% | +0.30 | +507.8% | -60.5% | 41.0% | 1.21x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
