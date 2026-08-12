# Résultat — Overlay de vol-targeting défensif uniquement (pré-enregistré, règle renforcée)

Position(t) = clip(15% / vol_réalisée_20j(t-1), 0.0, 1.0x) — jamais de levier au-dessus de 1.0x (variante du #43, CAP=2.0x). Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.64 | +62.0% | -24.0% | 0.77x | OUI | non |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.73 | +8524.4% | -48.3% | 0.76x | OUI | non |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.39 | +753.4% | -39.9% | 0.83x | OUI | non |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.53 | +4779.0% | -48.3% | 0.91x | OUI | non |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.24 | +158.2% | -56.2% | 0.81x | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
