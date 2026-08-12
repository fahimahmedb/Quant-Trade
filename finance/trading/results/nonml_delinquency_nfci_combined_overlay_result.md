# Résultat — Porte combinée (ET) défaut carte de crédit (#286) + NFCI (#291), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRCCLACBS_lag(t-1) ET NFCI_lag(t-1) sont TOUS DEUX dans leur tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (ET) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 24.3% | +0.52 | +79.0% | -36.4% | +0.63 | +84.1% | -27.1% | OUI | OUI |
| NDX (40 ans) | 8883 | 5.8% | +0.50 | +11049.9% | -82.9% | +0.52 | +10521.2% | -82.9% | OUI | non |
| Russell 2000 | 8883 | 5.6% | +0.37 | +1633.1% | -59.9% | +0.41 | +1777.2% | -46.0% | OUI | OUI |
| S&P 500 | 8883 | 4.1% | +0.47 | +1923.0% | -56.8% | +0.53 | +2219.0% | -49.1% | OUI | OUI |
| DAX | 6776 | 8.5% | +0.25 | +353.5% | -72.7% | +0.29 | +398.9% | -73.1% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
