# Résultat — Overlay de vol-targeting estimateur EWMA (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_EWMA(λ=0.94)(t-1), 0.0, 2.0x) — récursion RiskMetrics (`ewma_path`, Étape C) adaptée pour être causale. Échantillon testable = à partir de la 21e séance.

| Marché | Séances test. | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | +0.52 | +56.5% | -36.4% | +0.53 | +54.8% | -31.8% | 1.05x | OUI | non |
| NDX (40 ans) | 10252 | +0.53 | +6416.7% | -82.9% | +0.71 | +16295.0% | -56.8% | 1.08x | OUI | OUI |
| Russell 2000 | 9761 | +0.34 | +610.3% | -59.9% | +0.40 | +901.3% | -48.3% | 1.27x | OUI | OUI |
| S&P 500 | 14231 | +0.46 | +3696.8% | -56.8% | +0.51 | +10881.6% | -59.0% | 1.49x | OUI | OUI |
| DAX | 6756 | +0.24 | +116.5% | -72.7% | +0.26 | +137.7% | -66.0% | 1.19x | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
