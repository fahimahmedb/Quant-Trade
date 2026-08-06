# Résultat — Mises en chantier de logements US (HOUST, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si HoustGrowth(t)=log(HOUST(t)/HOUST(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 47.3% | +0.52 | +57.6% | -36.4% | +0.71 | +72.8% | -23.9% | OUI | OUI |
| NDX (40 ans) | 10272 | 31.1% | +0.53 | +6599.5% | -82.9% | +0.53 | +4481.6% | -79.3% | OUI | non |
| Russell 2000 | 9781 | 28.4% | +0.34 | +602.0% | -59.9% | +0.37 | +592.2% | -47.1% | OUI | non |
| S&P 500 | 14251 | 28.6% | +0.45 | +3369.2% | -56.8% | +0.50 | +3228.8% | -52.0% | OUI | non |
| DAX | 6776 | 32.1% | +0.25 | +130.5% | -72.7% | +0.24 | +107.4% | -70.5% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
