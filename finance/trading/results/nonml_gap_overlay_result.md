# Résultat — Overlay levé après un gap d'ouverture extrême (pré-enregistré, règle renforcée)

Gap(t) = open(t)/close(t-1)-1. Position 1.0x en permanence, CAP=2.0x pendant 2j après un gap tel que |Gap| ≥ 2% (relance si nouveau gap pendant la fenêtre), 1.0x sinon.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +57.6% | -36.4% | +0.42 | +46.9% | -41.4% | 7.5% | non | non |
| NDX (40 ans) | +0.53 | +6599.5% | -82.9% | +0.40 | +2150.8% | -88.9% | 4.4% | non | non |
| Russell 2000 | +0.34 | +602.0% | -59.9% | +0.31 | +456.4% | -65.0% | 0.6% | non | non |
| S&P 500 | +0.45 | +3369.2% | -56.8% | +0.41 | +2674.1% | -56.8% | 0.4% | non | non |
| DAX | +0.25 | +130.5% | -72.7% | +0.28 | +185.2% | -72.7% | 2.6% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
