# Résultat — Porte majoritaire (≥2/3) défaut carte de crédit (#286) + NFCI (#291) + BAA10Y (#199), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 2 des 3 signaux (DRCCLACBS_lag, NFCI_lag, BAA10Y_lag) sont dans leur tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (≥2/3) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 28.1% | +0.52 | +57.6% | -36.4% | +0.61 | +58.9% | -25.4% | OUI | OUI |
| NDX (40 ans) | 8883 | 19.7% | +0.50 | +3129.3% | -82.9% | +0.61 | +4142.3% | -71.9% | OUI | OUI |
| Russell 2000 | 8883 | 19.4% | +0.37 | +634.7% | -59.9% | +0.48 | +1059.4% | -39.5% | OUI | OUI |
| S&P 500 | 8883 | 14.5% | +0.47 | +1034.2% | -56.8% | +0.59 | +1457.7% | -38.5% | OUI | OUI |
| DAX | 6776 | 20.9% | +0.25 | +130.5% | -72.7% | +0.36 | +265.4% | -61.6% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
