# Résultat — Balance commerciale US (FRED BOPGSTB), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BOPGSTB_lag(t-1) (niveau brut, décalage 2 mois) est dans son tercile expanding le plus BAS (déficit commercial le plus large observé à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 37.1% | +0.52 | +57.6% | -36.4% | +0.68 | +69.8% | -26.1% | OUI | OUI |
| NDX (40 ans) | 8650 | 77.7% | +0.49 | +2416.2% | -82.9% | +0.55 | +1175.2% | -58.6% | OUI | non |
| Russell 2000 | 8650 | 77.7% | +0.35 | +494.4% | -59.9% | +0.37 | +347.2% | -42.3% | OUI | non |
| S&P 500 | 8650 | 77.7% | +0.46 | +928.9% | -56.8% | +0.51 | +505.2% | -35.4% | OUI | non |
| DAX | 6776 | 59.1% | +0.25 | +130.5% | -72.7% | +0.26 | +116.7% | -50.4% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
