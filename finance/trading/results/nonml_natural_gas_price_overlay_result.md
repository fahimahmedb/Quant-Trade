# Résultat — Prix du gaz naturel US Henry Hub (DHHNGSP), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si GasChange(t)=log(DHHNGSP(t)/DHHNGSP(t-21)) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 29.3% | +0.52 | +57.6% | -36.4% | +0.51 | +50.2% | -32.6% | non | non |
| NDX (40 ans) | 7402 | 32.2% | +0.43 | +982.2% | -82.9% | +0.40 | +637.4% | -80.4% | non | non |
| Russell 2000 | 7402 | 32.2% | +0.30 | +252.2% | -59.9% | +0.31 | +255.5% | -60.7% | OUI | OUI |
| S&P 500 | 7402 | 32.2% | +0.40 | +458.2% | -56.8% | +0.37 | +329.7% | -60.0% | non | non |
| DAX | 6776 | 31.5% | +0.25 | +130.5% | -72.7% | +0.23 | +95.8% | -68.2% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
