# Résultat — Porte majoritaire (≥2/3) défaut carte de crédit (#286) + NFCI (#291) + BAA10Y (#199), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 2 des 3 signaux (DRCCLACBS_lag, NFCI_lag, BAA10Y_lag) sont dans leur tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (≥2/3) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 28.1% | +0.52 | +79.0% | -36.4% | +0.61 | +72.3% | -25.4% | OUI | non |
| NDX (40 ans) | 8883 | 19.7% | +0.50 | +11049.9% | -82.9% | +0.61 | +9319.3% | -71.9% | OUI | non |
| Russell 2000 | 8883 | 19.4% | +0.37 | +1633.1% | -59.9% | +0.48 | +1897.3% | -39.5% | OUI | OUI |
| S&P 500 | 8883 | 14.5% | +0.47 | +1923.0% | -56.8% | +0.59 | +2255.2% | -38.5% | OUI | OUI |
| DAX | 6776 | 20.9% | +0.25 | +353.5% | -72.7% | +0.36 | +470.4% | -61.6% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
