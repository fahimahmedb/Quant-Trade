# Résultat — Régime de volatilité des taux courts DGS3MO (pré-enregistré)

`position(t) = 0.5x` si vol(taux, 63j) dans le tercile SUPÉRIEUR expanding (incertitude), `2.0x` si tercile INFÉRIEUR (calme), `1.0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % coupé | % levé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 997 | 17.8% | 33.5% | +1.00 | +113.3% | -24.3% | +0.93 | +155.4% | -37.9% | non | OUI |
| NDX (40 ans) | 10019 | 17.2% | 67.2% | +0.52 | +5399.1% | -82.9% | +0.51 | +13959.2% | -96.2% | non | OUI |
| Russell 2000 | 9528 | 15.3% | 66.3% | +0.37 | +736.3% | -59.9% | +0.38 | +1336.9% | -82.8% | OUI | OUI |
| S&P 500 | 10985 | 9.2% | 73.7% | +0.51 | +2493.2% | -56.8% | +0.59 | +24112.0% | -75.9% | OUI | OUI |
| DAX | 6523 | 20.7% | 49.2% | +0.22 | +88.8% | -69.1% | +0.23 | +67.3% | -91.5% | OUI | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
