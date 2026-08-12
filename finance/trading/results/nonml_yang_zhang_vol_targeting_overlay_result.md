# Résultat — Overlay de vol-targeting estimateur Yang-Zhang (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_YangZhang_20j(t), 0.0, 2.0x) — variante du #46/#50/#215/#221 combinant overnight + ouverture→clôture + Rogers-Satchell. Échantillon testable = à partir de la 22e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.54 | +77.7% | -36.8% | 1.09x | OUI | OUI |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.74 | +106793.7% | -61.1% | 1.19x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.38 | +4234.8% | -56.2% | 1.52x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.56 | +91270.2% | -63.9% | 1.52x | OUI | OUI |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.24 | +322.0% | -70.5% | 1.27x | OUI | non |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
