# Résultat — Renversement 1 an au niveau indice (pré-enregistré, complète le #177)

Marché : **NDX (40 ans)** uniquement. `position(t) = 2.0x` si `retour_1an(t) ≤ percentile_33.33_expanding`, `1.0x` sinon. LOOKBACK=252j, BURN_IN=252j, coûts 5 bps.

- Séances testées : 9767.
- Part du temps en régime de renversement (2.0x) : **32.3%**.

| | Sharpe ann. | Rendement total | MDD |
|---|---|---|---|
| Buy & Hold | +0.49 | +3644.8% | -82.9% |
| **Overlay renversement 1 an** | **+0.36** | **+998.2%** | -95.5% |

- Sharpe overlay > BH : NON
- Rendement overlay > BH : NON

**FAIL — critère pré-enregistré NON atteint.**
