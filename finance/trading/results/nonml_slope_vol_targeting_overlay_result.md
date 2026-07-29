# Résultat — Overlay vol-targeting gaté par la pente SMA200 (pré-enregistré, combinaison #66+#46)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si SMA200(t) > SMA200(t-20) (pente positive), sinon 1.0x. Échantillon testable = à partir de la 221e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.93 | +108.3% | -24.3% | +0.91 | +122.6% | -27.5% | 58.0% | 1.20x | non | OUI |
| NDX (40 ans) | +0.51 | +4956.4% | -82.9% | +0.54 | +8482.1% | -82.9% | 51.8% | 1.23x | OUI | OUI |
| Russell 2000 | +0.37 | +723.6% | -59.9% | +0.38 | +980.7% | -61.3% | 54.1% | 1.32x | OUI | OUI |
| S&P 500 | +0.47 | +3775.7% | -56.8% | +0.53 | +15424.5% | -59.3% | 68.5% | 1.48x | OUI | OUI |
| DAX | +0.21 | +80.7% | -69.1% | +0.23 | +99.8% | -69.7% | 54.3% | 1.29x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
