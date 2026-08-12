# Résultat — Croissance de la masse monétaire M2 (glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si M2Growth(t)=log(M2SL(t)/M2SL(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 46.2% | +0.52 | +79.0% | -36.4% | +0.65 | +74.5% | -24.3% | OUI | non |
| NDX (40 ans) | 10272 | 37.4% | +0.53 | +26208.9% | -82.9% | +0.42 | +5672.8% | -82.9% | non | non |
| Russell 2000 | 9781 | 32.5% | +0.34 | +1646.9% | -59.9% | +0.27 | +674.9% | -59.9% | non | non |
| S&P 500 | 14251 | 45.4% | +0.45 | +7977.0% | -56.8% | +0.40 | +2584.6% | -60.5% | non | non |
| DAX | 6776 | 45.4% | +0.25 | +353.5% | -72.7% | +0.15 | +123.0% | -69.9% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
