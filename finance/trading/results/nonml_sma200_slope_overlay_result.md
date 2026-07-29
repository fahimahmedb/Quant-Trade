# Résultat — Overlay levé filtre de pente SMA200 (pré-enregistré, règle renforcée)

Position 1.0x en permanence, CAP=2.0x quand SMA200(t) > SMA200(t-20) (pente positive), 1.0x sinon.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1030 | +0.93 | +108.3% | -24.3% | +0.95 | +220.2% | -42.7% | 76.7% | OUI | OUI |
| NDX (40 ans) | 10052 | +0.51 | +4956.4% | -82.9% | +0.58 | +56384.0% | -88.6% | 79.1% | OUI | OUI |
| Russell 2000 | 9561 | +0.37 | +723.6% | -59.9% | +0.40 | +1778.3% | -66.4% | 68.9% | OUI | OUI |
| S&P 500 | 14031 | +0.47 | +3775.7% | -56.8% | +0.52 | +38508.2% | -63.1% | 74.8% | OUI | OUI |
| DAX | 6556 | +0.21 | +80.7% | -69.1% | +0.32 | +288.0% | -70.7% | 66.6% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
