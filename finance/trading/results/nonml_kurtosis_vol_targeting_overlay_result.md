# Résultat — Overlay vol-targeting gaté par la kurtosis (aplatissement) glissante (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si l'excès de kurtosis glissant 252j est ≤ sa médiane glissante 252j, sinon 1.0x. Échantillon testable = à partir de la 254e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.00 | +113.4% | -24.3% | +1.05 | +128.1% | -24.3% | 16.9% | 1.07x | OUI | OUI |
| NDX (40 ans) | +0.52 | +5429.9% | -82.9% | +0.53 | +7399.4% | -82.9% | 27.8% | 1.11x | OUI | OUI |
| Russell 2000 | +0.37 | +739.6% | -59.9% | +0.38 | +869.3% | -60.0% | 32.6% | 1.18x | OUI | OUI |
| S&P 500 | +0.46 | +3436.7% | -56.8% | +0.49 | +7394.5% | -59.8% | 44.6% | 1.27x | OUI | OUI |
| DAX | +0.23 | +93.1% | -69.1% | +0.20 | +62.8% | -69.1% | 34.0% | 1.16x | non | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
