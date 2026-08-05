# Résultat — Overlay de vol-targeting estimateur HAR-P (Corsi 2009) (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_prévue_HAR-P(t), 0.0, 2.0x) — HAR-P fit sur la RV Parkinson (retards j/5j/22j), rééchelonné en variance close-to-close (`c2c_scale`), walk-forward T0=750, REFIT_EVERY=21j (réutilisé de l'Étape C, Règle 7). Échantillon testable à partir de la 750e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 500 | +0.78 | +34.2% | -24.3% | +0.50 | +14.6% | -17.1% | 0.86x | non | non |
| NDX (40 ans) | 9522 | +0.52 | +4553.2% | -82.9% | +0.67 | +6804.0% | -59.7% | 1.02x | OUI | OUI |
| Russell 2000 | 9031 | +0.39 | +791.2% | -59.9% | +0.41 | +753.7% | -44.5% | 1.17x | OUI | non |
| S&P 500 | 13501 | +0.44 | +2714.7% | -56.8% | +0.44 | +3651.7% | -63.2% | 1.42x | non | OUI |
| DAX | 6026 | +0.43 | +410.6% | -54.8% | +0.43 | +427.7% | -51.4% | 1.32x | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
