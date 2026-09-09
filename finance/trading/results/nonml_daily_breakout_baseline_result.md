# Résultat — Stratégie A : Daily Breakout (baseline, pré-enregistré)

Composite (5 ans), 1195 séances testables (à partir de la 56e). Long only, entrée open(t+1) si close>SMA50 ET breakout 20j (high, décalé 1j) ET RSI14∈[50,75]. Stop=1.5×ATR14, TP=3.0×ATR14 (2R). Risque 0.5% equity/trade, coûts 5bps/transition, capital initial 5000€.

## Résultat agrégé (net de coûts)

| | Stratégie A | Buy & Hold |
|---|---|---|
| Sharpe annualisé | +0.55 | +0.54 |
| Rendement total | +5.6% | +80.1% |
| Max drawdown | -2.8% | -36.4% |
| Calmar | 0.40 | 0.27 |
| % jours en position | 35.6% | 100.0% |

## Statistiques de trades

- Nombre de trades : **41**
- Taux de réussite : 43.9%
- R moyen par trade : +0.32R
- Profit factor : 1.45
- Sorties stop / take-profit : 23 / 18
- Position ouverte en fin d'échantillon : non

- Sharpe A > Sharpe B&H : OUI
- Rendement A > B&H : non

**FAIL — critère pré-enregistré NON atteint (bat B&H simultanément en Sharpe ET rendement).**
