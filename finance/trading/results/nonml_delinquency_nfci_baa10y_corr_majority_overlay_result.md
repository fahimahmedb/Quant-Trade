# Résultat — Panel élargi à 4 signaux (défaut carte #286 + NFCI #291 + BAA10Y #199 + corrélation NDX-DAX #193), vote ≥3/4, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si AU MOINS 3 des 4 signaux sont dans leur tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (≥3/4) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 21.0% | +0.52 | +79.0% | -36.4% | +0.59 | +77.4% | -30.5% | OUI | non |
| NDX (40 ans) | 6651 | 17.4% | +0.30 | +756.1% | -82.9% | +0.38 | +877.1% | -74.2% | OUI | OUI |
| Russell 2000 | 6651 | 17.1% | +0.27 | +484.9% | -59.9% | +0.36 | +559.9% | -42.3% | OUI | OUI |
| S&P 500 | 6651 | 13.4% | +0.34 | +452.3% | -56.8% | +0.42 | +537.5% | -41.2% | OUI | OUI |
| DAX | 6714 | 17.3% | +0.21 | +254.5% | -72.7% | +0.29 | +333.8% | -62.9% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
