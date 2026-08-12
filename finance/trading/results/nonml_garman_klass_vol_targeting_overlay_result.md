# Résultat — Overlay de vol-targeting estimateur Garman-Klass (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_GarmanKlass_20j(t-1), 0.0, 2.0x) — variante du #46 (close-to-close) et du #50 (Parkinson). Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +77.6% | -36.4% | +0.62 | +132.3% | -44.2% | 1.42x | OUI | OUI |
| NDX (40 ans) | 10252 | +0.53 | +25465.6% | -82.9% | +0.74 | +274813.0% | -67.5% | 1.35x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +1666.8% | -59.9% | +0.39 | +5772.2% | -58.2% | 1.59x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +8735.1% | -56.8% | +0.55 | +114693.8% | -65.4% | 1.56x | OUI | OUI |
| DAX | 6756 | +0.24 | +325.5% | -72.7% | +0.27 | +513.4% | -70.9% | 1.44x | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
