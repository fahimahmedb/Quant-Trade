# Résultat — Inversion de la courbe des taux DGS10-DGS3MO (pré-enregistré)

`position(t) = 0.5x` si DGS10(t-1) - DGS3MO(t-1) < 0 (courbe inversée), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps inversé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1249 | 49.8% | +0.52 | +58.0% | -36.4% | +0.23 | +13.8% | -35.7% | non | non |
| NDX (40 ans) | 10271 | 11.9% | +0.53 | +6679.8% | -82.9% | +0.52 | +5392.4% | -78.5% | non | non |
| Russell 2000 | 9780 | 12.5% | +0.34 | +595.6% | -59.9% | +0.33 | +494.8% | -60.4% | non | non |
| S&P 500 | 11303 | 11.0% | +0.51 | +2820.8% | -56.8% | +0.48 | +2039.1% | -57.1% | non | non |
| DAX | 6775 | 16.8% | +0.25 | +129.6% | -72.7% | +0.20 | +66.1% | -71.7% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
