# Résultat — Renversement long terme au niveau indice, De Bondt & Thaler 1985 (pré-enregistré)

Marché : **NDX (40 ans)** uniquement. `position(t) = 2.0x` si `retour_3ans(t) ≤ percentile_33.33_expanding`, `1.0x` sinon. LOOKBACK=756j, BURN_IN=252j, coûts 5 bps.

- Séances testées : 9263.
- Part du temps en régime de renversement (2.0x) : **30.6%**.

| | Sharpe ann. | Rendement total | MDD |
|---|---|---|---|
| Buy & Hold | +0.50 | +13082.6% | -82.9% |
| **Overlay renversement 3 ans** | **+0.44** | **+48994.3%** | -90.0% |

- Sharpe overlay > BH : NON
- Rendement overlay > BH : OUI

**FAIL — critère pré-enregistré NON atteint.**
