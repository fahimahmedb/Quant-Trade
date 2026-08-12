# Résultat — Sleeve dollar-neutre composite redimensionné par sa propre volatilité (Piste C, pré-enregistré)

`pos(t) = clip(15% / vol_réalisée_20j(sleeve, t-1), 0, 2.0x)` (overlay #46 réutilisé à l'identique), appliqué au rendement quotidien du sleeve du #349 (déjà net de ses propres coûts de rebalancement). Coût supplémentaire 5 bps sur le turnover du levier quotidien.

Échantillon : 2887 séances (2015-02-02 → 2026-07-27). Position moyenne : 0.93x (min 0.26x, max 2.00x).

| | Sharpe ann. | Sharpe journalier | t-stat | Rendement total | MDD |
|---|---|---|---|---|---|
| Buy&Hold PIT (contexte, hérité du #349) | +0.40 | — | — | +163.8% | -36.4% |
| Sleeve #349 SANS vol-targeting (référence directe) | +0.45 | — | — | +217.7% | -28.2% |
| **Sleeve redimensionné par sa vol (Piste C)** | **+0.61** | +0.0387 | **+2.08** | +222.6% | -32.4% |

1. Sharpe annualisé > 0 : OUI
2. t-stat > 2 : OUI

**PASS — critère pré-enregistré (Sharpe>0 ET t-stat>2, identique au #349) atteint.**
