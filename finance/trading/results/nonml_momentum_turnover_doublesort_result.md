# Résultat — Momentum 12-1 + double-tri turnover/volume-dollars (pré-enregistré, combinaison #73 + nouvelle donnée volume)

Univers : 99 tickers NDX-100 avec prix ET volume disponibles (0 exclus faute de volume : aucun), 1144 séances testables (2022-01-03 → 2026-07-27), rebalancement tous les 21j. Référence = momentum 12-1 seul (cycle #73), PAS Buy&Hold. Double tri : tercile momentum 12-1 (SKIP=21j, LOOKBACK=252j), puis tercile à turnover (volume en dollars moyen 126j) LE PLUS FAIBLE parmi ce sous-ensemble. Construction causale dès le départ (`lag_one_day` appliqué à la construction).

| | Sharpe ann. | Rendement total net | MDD |
|---|---|---|---|
| Momentum 12-1 seul (référence, cycle #73, univers restreint) | +0.66 | +93.8% | -31.8% |
| **Momentum 12-1 + double-tri turnover faible** | **+1.04** | **+178.3%** | -26.0% |

1. Sharpe double tri > référence : OUI
2. Rendement double tri > référence : OUI

**PASS — critère renforcé atteint.**
