# Résultat — Overlay levé après un gap d'ouverture extrême (pré-enregistré, règle renforcée)

Gap(t) = open(t)/close(t-1)-1. Position 1.0x en permanence, CAP=2.0x pendant 2j après un gap tel que |Gap| ≥ 2% (relance si nouveau gap pendant la fenêtre), 1.0x sinon.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j levé | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +0.52 | +79.0% | -36.4% | +0.42 | +77.5% | -41.4% | 7.5% | non | non |
| NDX (40 ans) | +0.53 | +26208.9% | -82.9% | +0.40 | +17591.4% | -88.9% | 4.4% | non | non |
| Russell 2000 | +0.34 | +1646.9% | -59.9% | +0.31 | +1571.8% | -65.0% | 0.6% | non | non |
| S&P 500 | +0.45 | +7977.0% | -56.8% | +0.41 | +7238.4% | -56.8% | 0.4% | non | non |
| DAX | +0.25 | +353.5% | -72.7% | +0.28 | +585.0% | -72.7% | 2.6% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
