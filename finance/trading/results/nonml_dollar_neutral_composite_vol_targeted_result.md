# Résultat — Sleeve dollar-neutre composite redimensionné par sa propre volatilité (Piste C, pré-enregistré)

`pos(t) = clip(15% / vol_réalisée_20j(sleeve, t-1), 0, 2.0x)` (overlay #46 réutilisé à l'identique), appliqué au rendement quotidien du sleeve du #349 (déjà net de ses propres coûts de rebalancement). Coût supplémentaire 5 bps sur le turnover du levier quotidien.

Échantillon : 2887 séances (2015-02-02 → 2026-07-27). Position moyenne : 0.92x (min 0.25x, max 2.00x).

| | Sharpe ann. | Sharpe journalier | t-stat | Rendement total | MDD |
|---|---|---|---|---|---|
| Buy&Hold PIT (contexte, hérité du #349) | +0.74 | — | — | +494.3% | -29.7% |
| Sleeve #349 SANS vol-targeting (référence directe) | +0.19 | — | — | +62.7% | -36.5% |
| **Sleeve redimensionné par sa vol (Piste C)** | **+0.36** | +0.0227 | **+1.22** | +98.9% | -36.0% |

1. Sharpe annualisé > 0 : OUI
2. t-stat > 2 : non

**FAIL — critère pré-enregistré (Sharpe>0 ET t-stat>2, identique au #349) NON atteint.**
