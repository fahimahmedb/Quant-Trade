# Résultat — Overlay vol-targeting gaté par l'asymétrie (skewness) glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si la skewness glissante 252j est ≥ sa médiane glissante 252j, sinon 1.0x. Échantillon testable = à partir de la 254e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.00 | +133.5% | -24.3% | +0.94 | +133.4% | -24.3% | 27.8% | 1.10x | non | non |
| NDX (40 ans) | +0.52 | +21358.1% | -82.9% | +0.52 | +30708.6% | -82.9% | 30.3% | 1.13x | OUI | OUI |
| Russell 2000 | +0.37 | +1912.7% | -59.9% | +0.40 | +3280.1% | -60.3% | 37.7% | 1.20x | OUI | OUI |
| S&P 500 | +0.46 | +8040.9% | -56.8% | +0.49 | +21823.6% | -58.5% | 39.2% | 1.25x | OUI | OUI |
| DAX | +0.23 | +270.2% | -69.1% | +0.22 | +290.1% | -69.5% | 26.6% | 1.13x | non | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
