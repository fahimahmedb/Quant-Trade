# Résultat — Breadth de drawdown profond, univers POINT-IN-TIME (pré-enregistré)

Réutilisation stricte (Règle 7) du cycle d'origine : **aucun paramètre modifié**. Seul l'univers du SIGNAL change — appartenance NDX-100 résolue à chaque date (`tickers_as_of_date`) au lieu de la liste 2026 appliquée rétroactivement.

`position(t) = clip(20% / vol_réalisée_20j(t-1), 1.0, 2.0x)` si Breadth_DD(t) ≥ sa médiane glissante 252j, sinon 1.0x. Coûts 5 bps.

Univers PIT : 174 tickers disponibles. Couverture moyenne (membres avec prix / membres réels) : 88.4%.
2645 séances testables (2016-01-04 → 2026-07-13).

%j porte drawdown profond active : 25.8%
Position moyenne : 1.11x
Breadth drawdown profond moyenne : 27.4%

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Buy&Hold (NDX) | +0.79 | +542.3% | -35.6% |
| **Overlay gaté breadth DD (univers PIT)** | **+0.82** | **+698.4%** | -36.9% |

1. Sharpe overlay > Buy&Hold : OUI
2. Rendement overlay > Buy&Hold : OUI

**PASS — critère renforcé (Sharpe ET rendement) atteint sur univers point-in-time.**

Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent, comme les 7 paires `*_pit_universe` déjà committées. La comparaison des deux mesure l'effet du biais du survivant sur ce candidat.
