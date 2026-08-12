# Résultat — Indice des prix immobiliers Case-Shiller US (CSUSHPISA, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si HomePriceGrowth(t)=log(CSUSHPISA(t)/CSUSHPISA(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 72.0% | +0.52 | +79.0% | -36.4% | +0.38 | +34.5% | -31.7% | non | non |
| NDX (40 ans) | 9662 | 29.8% | +0.52 | +16990.2% | -82.9% | +0.48 | +7664.0% | -82.9% | non | non |
| Russell 2000 | 9662 | 29.8% | +0.38 | +2066.2% | -59.9% | +0.39 | +1327.0% | -46.0% | OUI | non |
| S&P 500 | 9662 | 29.8% | +0.49 | +2711.0% | -56.8% | +0.52 | +1900.3% | -49.1% | OUI | non |
| DAX | 6776 | 38.2% | +0.25 | +353.5% | -72.7% | +0.28 | +308.7% | -64.5% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
