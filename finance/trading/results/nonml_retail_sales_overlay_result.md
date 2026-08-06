# Résultat — Ventes au détail US (RSXFS, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RetailGrowth(t)=log(RSXFS(t)/RSXFS(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 61.2% | +0.52 | +57.6% | -36.4% | +0.50 | +41.6% | -24.3% | non | non |
| NDX (40 ans) | 8417 | 49.5% | +0.49 | +2258.9% | -82.9% | +0.49 | +1330.7% | -67.8% | OUI | non |
| Russell 2000 | 8417 | 49.5% | +0.34 | +451.9% | -59.9% | +0.28 | +200.9% | -42.6% | non | non |
| S&P 500 | 8417 | 49.5% | +0.46 | +862.9% | -56.8% | +0.44 | +462.3% | -35.6% | non | non |
| DAX | 6776 | 40.5% | +0.25 | +130.5% | -72.7% | +0.30 | +170.5% | -54.7% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
