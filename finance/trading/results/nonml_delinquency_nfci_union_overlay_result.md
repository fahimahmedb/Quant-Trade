# Résultat — Porte combinée (OU) défaut carte de crédit (#286) + NFCI (#291), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRCCLACBS_lag(t-1) OU NFCI_lag(t-1) est dans son tercile expanding le plus HAUT (au moins un des deux), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé (OU) | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 77.9% | +0.52 | +57.6% | -36.4% | +0.56 | +39.9% | -20.2% | OUI | non |
| NDX (40 ans) | 8883 | 30.9% | +0.50 | +3129.3% | -82.9% | +0.57 | +2568.0% | -71.9% | OUI | non |
| Russell 2000 | 8883 | 30.5% | +0.37 | +634.7% | -59.9% | +0.50 | +1019.9% | -40.5% | OUI | OUI |
| S&P 500 | 8883 | 20.2% | +0.47 | +1034.2% | -56.8% | +0.56 | +1188.5% | -38.5% | OUI | OUI |
| DAX | 6776 | 32.3% | +0.25 | +130.5% | -72.7% | +0.35 | +244.0% | -60.5% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
