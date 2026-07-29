# Résultat — Overlay vol-targeting gaté par le golden cross (pré-enregistré, combinaison #34+#46)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si SMA50 > SMA200 (golden cross), sinon 1.0x. Échantillon testable = à partir de la 201e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.79 | +89.3% | -24.3% | +0.78 | +99.8% | -27.5% | 55.4% | 1.20x | non | OUI |
| NDX (40 ans) | +0.51 | +5004.2% | -82.9% | +0.52 | +7401.4% | -82.9% | 48.8% | 1.22x | OUI | OUI |
| Russell 2000 | +0.37 | +724.6% | -59.9% | +0.34 | +644.4% | -61.0% | 54.2% | 1.31x | non | non |
| S&P 500 | +0.47 | +3751.7% | -56.8% | +0.54 | +18142.8% | -58.9% | 66.8% | 1.46x | OUI | OUI |
| DAX | +0.21 | +77.6% | -70.4% | +0.22 | +84.1% | -72.0% | 53.4% | 1.29x | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
