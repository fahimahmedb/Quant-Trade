# Résultat — Inflation réalisée US (FRED CPIAUCSL), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CPIGrowth_lag(t-1)=log(CPIAUCSL(t)/CPIAUCSL(t-12)) est dans son tercile expanding le plus HAUT (inflation réalisée la plus élevée observée à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 19.6% | +0.52 | +57.6% | -36.4% | +0.70 | +80.5% | -26.2% | OUI | OUI |
| NDX (40 ans) | 10272 | 28.3% | +0.53 | +6599.5% | -82.9% | +0.64 | +12687.9% | -72.1% | OUI | OUI |
| Russell 2000 | 9781 | 24.1% | +0.34 | +602.0% | -59.9% | +0.44 | +1127.2% | -44.6% | OUI | OUI |
| S&P 500 | 14251 | 16.0% | +0.45 | +3369.2% | -56.8% | +0.51 | +4499.0% | -50.2% | OUI | OUI |
| DAX | 6776 | 33.7% | +0.25 | +130.5% | -72.7% | +0.30 | +191.2% | -67.2% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
