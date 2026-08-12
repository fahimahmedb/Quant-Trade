# Résultat — Stratégie nuit seulement vs Buy&Hold (pré-enregistré, règle renforcée)

Position = 1.0x de la clôture(t) à l'ouverture(t+1), 0.0x pendant la séance (2 transactions/jour, 5 bps chacune). r_nuit(t)+r_jour(t)=r_BH(t) par construction.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Nuit Sharpe | Nuit Rdt total | Nuit MDD | Part nuit du rdt brut | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +79.0% | -36.4% | -1.35 | -60.9% | -62.3% | 53% | non | non |
| NDX (40 ans) | +0.53 | +26208.9% | -82.9% | -1.79 | -100.0% | -100.0% | 35% | non | non |
| Russell 2000 | +0.34 | +1646.9% | -59.9% | -4.47 | -100.0% | -100.0% | 26% | non | non |
| S&P 500 | +0.45 | +7977.0% | -56.8% | -5.97 | -100.0% | -100.0% | 17% | non | non |
| DAX | +0.25 | +353.5% | -72.7% | -1.80 | -99.3% | -99.3% | 119% | non | non |

**0/5 marchés où la stratégie nuit bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
