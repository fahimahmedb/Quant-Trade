# Résultat — Momentum du Bitcoin (CBBTCUSD, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BTCmom_lag(t)=log(BTC(t-1)/BTC(t-1-21)) est dans son tercile expanding le plus BAS (repli marqué du Bitcoin), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 31.5% | +0.52 | +56.8% | -36.4% | +0.77 | +88.6% | -33.4% | OUI | OUI |
| NDX (40 ans) | 2897 | 32.4% | +0.76 | +424.3% | -35.6% | +0.93 | +445.3% | -29.9% | OUI | OUI |
| Russell 2000 | 2897 | 32.4% | +0.34 | +80.8% | -43.1% | +0.52 | +145.2% | -30.2% | OUI | OUI |
| S&P 500 | 2897 | 32.4% | +0.63 | +203.8% | -33.9% | +0.84 | +237.7% | -24.5% | OUI | OUI |
| DAX | 2920 | 33.3% | +0.44 | +114.0% | -38.8% | +0.53 | +127.0% | -25.4% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
