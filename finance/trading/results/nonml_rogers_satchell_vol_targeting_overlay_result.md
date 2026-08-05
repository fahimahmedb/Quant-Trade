# Résultat — Overlay de vol-targeting estimateur Rogers-Satchell (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_RogersSatchell_20j(t-1), 0.0, 2.0x) — variante robuste au drift intra-séance du #46/#50/#215. Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +56.5% | -36.4% | +0.58 | +83.3% | -45.3% | 1.41x | OUI | OUI |
| NDX (40 ans) | 10252 | +0.53 | +6416.7% | -82.9% | +0.72 | +57505.7% | -67.7% | 1.36x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +610.3% | -59.9% | +0.37 | +1064.0% | -57.6% | 1.61x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +3696.8% | -56.8% | +0.55 | +25397.8% | -64.8% | 1.56x | OUI | OUI |
| DAX | 6756 | +0.24 | +116.5% | -72.7% | +0.27 | +155.0% | -71.5% | 1.44x | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
