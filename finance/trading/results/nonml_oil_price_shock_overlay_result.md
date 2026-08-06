# Résultat — Choc de prix du pétrole WTI (DCOILWTICO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si OilChange(t)=log(WTI(t)/WTI(t-21)) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 29.0% | +0.52 | +57.6% | -36.4% | +0.68 | +78.8% | -28.8% | OUI | OUI |
| NDX (40 ans) | 10187 | 35.9% | +0.52 | +5570.3% | -82.9% | +0.49 | +3192.3% | -76.5% | non | non |
| Russell 2000 | 9781 | 36.6% | +0.34 | +602.0% | -59.9% | +0.36 | +591.2% | -50.7% | OUI | non |
| S&P 500 | 10187 | 35.9% | +0.48 | +1678.4% | -56.8% | +0.43 | +902.1% | -48.8% | non | non |
| DAX | 6776 | 30.3% | +0.25 | +130.5% | -72.7% | +0.27 | +150.8% | -64.6% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
