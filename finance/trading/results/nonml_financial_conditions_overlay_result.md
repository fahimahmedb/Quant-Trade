# Résultat — Indice des conditions financières NFCI, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si NFCI_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 32.2% | +0.52 | +79.0% | -36.4% | +0.74 | +95.1% | -24.3% | OUI | OUI |
| NDX (40 ans) | 10272 | 22.2% | +0.53 | +26208.9% | -82.9% | +0.55 | +12679.8% | -78.7% | OUI | non |
| Russell 2000 | 9781 | 18.2% | +0.34 | +1646.9% | -59.9% | +0.44 | +1830.6% | -43.1% | OUI | OUI |
| S&P 500 | 13988 | 13.8% | +0.46 | +7974.4% | -56.8% | +0.52 | +8405.8% | -49.1% | OUI | OUI |
| DAX | 6776 | 22.7% | +0.25 | +353.5% | -72.7% | +0.28 | +329.9% | -71.6% | OUI | non |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
