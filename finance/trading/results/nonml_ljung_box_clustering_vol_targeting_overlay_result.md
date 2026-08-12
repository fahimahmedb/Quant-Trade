# Résultat — Overlay vol-targeting gaté par la statistique de Ljung-Box glissante (clustering ARCH multi-retards) (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si la statistique de Ljung-Box Q(22) glissante 252j (sur les rendements au carré) est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable à partir de la 504e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +84.4% | -24.3% | +1.02 | +92.0% | -24.3% | 21.8% | 1.08x | OUI | OUI |
| NDX (40 ans) | +0.49 | +14351.5% | -82.9% | +0.52 | +25281.6% | -82.9% | 27.6% | 1.13x | OUI | OUI |
| Russell 2000 | +0.35 | +1554.3% | -59.9% | +0.37 | +2484.5% | -61.4% | 36.0% | 1.20x | OUI | OUI |
| S&P 500 | +0.45 | +7249.2% | -56.8% | +0.46 | +16466.5% | -59.2% | 45.3% | 1.29x | OUI | OUI |
| DAX | +0.30 | +432.6% | -59.7% | +0.28 | +445.7% | -59.7% | 37.9% | 1.18x | non | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
