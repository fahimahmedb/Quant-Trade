# Résultat — Position graduée par nombre de votes (défaut carte #286 + NFCI #291 + BAA10Y #199), overlay défensif (pré-enregistré)

`position(t) = 1,0 - 0.5×Votes(t)/3` où Votes(t) ∈ {0,1,2,3} est le nombre de signaux (DRCCLACBS_lag, NFCI_lag, BAA10Y_lag) dans leur tercile expanding le plus haut. Sizing continu, pas de seuil binaire. Coûts 5 bps.

| Marché | Séances test. | % temps à 0 vote | % 1 vote | % 2 votes | % 3 votes | BH Sharpe | BH Rdt total | Overlay Sharpe | Overlay Rdt total | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 22.0% | 49.9% | 11.6% | 16.5% | +0.52 | +79.0% | +0.59 | +64.2% | OUI | non |
| NDX (40 ans) | 8883 | 49.0% | 31.3% | 13.8% | 5.8% | +0.50 | +11049.9% | +0.58 | +7189.9% | OUI | non |
| Russell 2000 | 8883 | 46.1% | 34.5% | 13.8% | 5.6% | +0.37 | +1633.1% | +0.44 | +1389.7% | OUI | non |
| S&P 500 | 8883 | 54.6% | 30.9% | 10.4% | 4.1% | +0.47 | +1923.0% | +0.57 | +1756.8% | OUI | non |
| DAX | 6776 | 59.4% | 19.7% | 13.1% | 7.8% | +0.25 | +353.5% | +0.35 | +443.0% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
