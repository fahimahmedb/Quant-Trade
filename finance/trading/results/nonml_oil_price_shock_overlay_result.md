# Résultat — Choc de prix du pétrole WTI (DCOILWTICO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si OilChange(t)=log(WTI(t)/WTI(t-21)) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 29.0% | +0.52 | +79.0% | -36.4% | +0.68 | +97.9% | -28.8% | OUI | OUI |
| NDX (40 ans) | 10187 | 35.9% | +0.52 | +22094.2% | -82.9% | +0.49 | +9265.8% | -76.5% | non | non |
| Russell 2000 | 9781 | 36.6% | +0.34 | +1646.9% | -59.9% | +0.36 | +1280.3% | -50.7% | OUI | non |
| S&P 500 | 10187 | 35.9% | +0.48 | +3446.9% | -56.8% | +0.43 | +1638.6% | -48.8% | non | non |
| DAX | 6776 | 30.3% | +0.25 | +353.5% | -72.7% | +0.27 | +332.2% | -64.6% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
