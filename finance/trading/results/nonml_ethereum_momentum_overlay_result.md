# Résultat — Momentum de l'Ethereum (CBETHUSD, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ETHmom_lag(t)=log(ETH(t-1)/ETH(t-1-21)) est dans son tercile expanding le plus BAS (repli marqué de l'Ethereum), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 38.0% | +0.52 | +56.8% | -36.4% | +0.76 | +76.6% | -30.6% | OUI | OUI |
| NDX (40 ans) | 2529 | 32.2% | +0.84 | +420.1% | -35.6% | +0.97 | +391.7% | -31.5% | OUI | non |
| Russell 2000 | 2529 | 32.2% | +0.40 | +94.7% | -43.1% | +0.46 | +102.3% | -34.4% | OUI | OUI |
| S&P 500 | 2529 | 32.2% | +0.71 | +207.2% | -33.9% | +0.85 | +201.3% | -26.9% | OUI | non |
| DAX | 2554 | 32.6% | +0.52 | +120.9% | -38.8% | +0.49 | +89.6% | -31.9% | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
