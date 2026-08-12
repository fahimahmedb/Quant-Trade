# Résultat — Overlay vol-targeting gaté par le ratio de variance de Lo-MacKinlay glissant (pré-enregistré, règle renforcée)

Position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x) si VR(5) calculé sur les 252 rendements précédents est ≥1,0 (régime de persistance locale), sinon 1.0x. Échantillon testable = à partir de la 254e séance.

| Marché | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | %j porte active | Position moy. | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | +1.00 | +133.5% | -24.3% | +1.05 | +147.6% | -24.3% | 7.8% | 1.04x | OUI | OUI |
| NDX (40 ans) | +0.52 | +21358.1% | -82.9% | +0.52 | +27494.8% | -82.9% | 19.6% | 1.08x | OUI | OUI |
| Russell 2000 | +0.37 | +1912.7% | -59.9% | +0.43 | +4494.4% | -59.9% | 37.2% | 1.25x | OUI | OUI |
| S&P 500 | +0.46 | +8040.9% | -56.8% | +0.47 | +17926.6% | -58.6% | 38.2% | 1.25x | OUI | OUI |
| DAX | +0.23 | +270.2% | -69.1% | +0.21 | +271.7% | -69.8% | 25.5% | 1.13x | non | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
