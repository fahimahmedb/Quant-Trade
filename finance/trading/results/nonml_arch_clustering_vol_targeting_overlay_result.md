# Résultat — Overlay vol-targeting gaté par le clustering ARCH glissant (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si l'autocorrélation glissante 252j des rendements au carré est ≥ sa médiane glissante 252j, sinon 1.0x. Échantillon testable = à partir de la 254e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.00 | +133.5% | -24.3% | +0.90 | +129.0% | -27.5% | 34.5% | 1.12x | non | non |
| NDX (40 ans) | +0.52 | +21358.1% | -82.9% | +0.52 | +28921.4% | -82.9% | 24.0% | 1.11x | OUI | OUI |
| Russell 2000 | +0.37 | +1912.7% | -59.9% | +0.38 | +2684.4% | -61.0% | 35.2% | 1.19x | OUI | OUI |
| S&P 500 | +0.46 | +8040.9% | -56.8% | +0.48 | +19471.1% | -60.4% | 36.0% | 1.25x | OUI | OUI |
| DAX | +0.23 | +270.2% | -69.1% | +0.27 | +442.4% | -69.1% | 36.0% | 1.20x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
