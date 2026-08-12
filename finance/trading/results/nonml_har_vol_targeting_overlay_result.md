# Résultat — Overlay de vol-targeting estimateur HAR-P (Corsi 2009) (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_prévue_HAR-P(t), 0.0, 2.0x) — HAR-P fit sur la RV Parkinson (retards j/5j/22j), rééchelonné en variance close-to-close (`c2c_scale`), walk-forward T0=750, REFIT_EVERY=21j (réutilisé de l'Étape C, Règle 7). Échantillon testable à partir de la 750e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 500 | +0.78 | +40.9% | -24.3% | +0.50 | +17.8% | -17.1% | 0.86x | non | non |
| NDX (40 ans) | 9522 | +0.52 | +16652.5% | -82.9% | +0.67 | +14066.1% | -59.7% | 1.02x | OUI | non |
| Russell 2000 | 9031 | +0.39 | +2014.8% | -59.9% | +0.41 | +1513.5% | -44.5% | 1.17x | OUI | non |
| S&P 500 | 13501 | +0.44 | +6325.6% | -56.8% | +0.44 | +10725.3% | -63.2% | 1.42x | non | OUI |
| DAX | 6026 | +0.43 | +779.1% | -54.8% | +0.43 | +831.3% | -51.4% | 1.32x | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
