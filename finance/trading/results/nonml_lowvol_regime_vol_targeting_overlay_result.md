# Résultat — Overlay vol-targeting gaté par un régime de volatilité réalisée faible (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si vol_réalisée(t-1) < médiane glissante 252j de vol_réalisée, sinon 1.0x.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.87 | +104.3% | -24.3% | +0.85 | +122.7% | -27.4% | 46.9% | 1.20x | non | OUI |
| NDX (40 ans) | +0.51 | +20605.1% | -82.9% | +0.52 | +34392.8% | -82.9% | 39.8% | 1.21x | OUI | OUI |
| Russell 2000 | +0.37 | +1891.0% | -59.9% | +0.37 | +2765.3% | -60.7% | 46.1% | 1.27x | OUI | OUI |
| S&P 500 | +0.46 | +7789.5% | -56.8% | +0.43 | +15770.5% | -65.5% | 51.0% | 1.40x | non | OUI |
| DAX | +0.23 | +279.6% | -67.6% | +0.21 | +293.2% | -69.5% | 44.1% | 1.27x | non | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
