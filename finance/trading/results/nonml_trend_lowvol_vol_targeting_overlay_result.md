# Résultat — Overlay vol-targeting gaté par double porte tendance+vol faible (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si tendance haussière (≥95% du plus haut 252j) ET vol réalisée sous sa médiane glissante 252j, sinon 1.0x.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.02 | +84.4% | -24.3% | +0.95 | +94.1% | -26.9% | 45.6% | 1.22x | non | OUI |
| NDX (40 ans) | +0.49 | +14351.5% | -82.9% | +0.49 | +21128.2% | -82.9% | 30.1% | 1.17x | OUI | OUI |
| Russell 2000 | +0.35 | +1554.3% | -59.9% | +0.35 | +1984.5% | -60.6% | 29.2% | 1.18x | OUI | OUI |
| S&P 500 | +0.45 | +7249.2% | -56.8% | +0.47 | +19247.7% | -58.4% | 38.5% | 1.32x | OUI | OUI |
| DAX | +0.30 | +432.6% | -59.7% | +0.30 | +515.2% | -59.7% | 34.1% | 1.24x | non | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
