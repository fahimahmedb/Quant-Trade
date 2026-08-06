# Résultat — Position graduée par nombre de votes (défaut carte #286 + NFCI #291 + BAA10Y #199), overlay défensif (pré-enregistré)

`position(t) = 1,0 - 0.5×Votes(t)/3` où Votes(t) ∈ {0,1,2,3} est le nombre de signaux (DRCCLACBS_lag, NFCI_lag, BAA10Y_lag) dans leur tercile expanding le plus haut. Sizing continu, pas de seuil binaire. Coûts 5 bps.

| Marché | Séances test. | % temps à 0 vote | % 1 vote | % 2 votes | % 3 votes | BH Sharpe | BH Rdt total | Overlay Sharpe | Overlay Rdt total | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 22.0% | 49.9% | 11.6% | 16.5% | +0.52 | +57.6% | +0.59 | +52.8% | OUI | non |
| NDX (40 ans) | 8883 | 49.0% | 31.3% | 13.8% | 5.8% | +0.50 | +3129.3% | +0.58 | +3227.1% | OUI | OUI |
| Russell 2000 | 8883 | 46.1% | 34.5% | 13.8% | 5.6% | +0.37 | +634.7% | +0.44 | +780.7% | OUI | OUI |
| S&P 500 | 8883 | 54.6% | 30.9% | 10.4% | 4.1% | +0.47 | +1034.2% | +0.57 | +1172.7% | OUI | OUI |
| DAX | 6776 | 59.4% | 19.7% | 13.1% | 7.8% | +0.25 | +130.5% | +0.35 | +249.8% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
