# Résultat — Inversion de la courbe des taux DGS10-DGS3MO (pré-enregistré)

`position(t) = 0.5x` si DGS10(t-1) - DGS3MO(t-1) < 0 (courbe inversée), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps inversé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1249 | 49.8% | +0.52 | +79.4% | -36.4% | +0.23 | +24.0% | -35.7% | non | non |
| NDX (40 ans) | 10271 | 11.9% | +0.53 | +26522.2% | -82.9% | +0.52 | +18648.4% | -78.5% | non | non |
| Russell 2000 | 9780 | 12.5% | +0.34 | +1630.8% | -59.9% | +0.33 | +1266.5% | -60.4% | non | non |
| S&P 500 | 11303 | 11.0% | +0.51 | +5982.7% | -56.8% | +0.48 | +4145.3% | -57.1% | non | non |
| DAX | 6775 | 16.8% | +0.25 | +351.7% | -72.7% | +0.20 | +212.9% | -71.7% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
