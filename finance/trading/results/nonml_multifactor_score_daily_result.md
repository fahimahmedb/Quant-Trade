# Résultat — Stratégie B : Score multi-facteurs /10 (daily, pré-enregistré)

Composite (5 ans), 1045 séances testables (à partir de la 206e, amorçage SMA200). Long only, entrée open(t+1) si score(t)≥7/10 (facteur Volume structurellement toujours 0/1, cf. PREREG — score max atteignable = 9/10). Stop=1.5×ATR14, TP=3.0×ATR14 (2R fixe, pas de BE ni trailing). Risque 0.5% equity/trade, coûts 5bps/transition, capital initial 5000€.

## Résultat agrégé (net de coûts)

| | Stratégie B | Buy & Hold |
|---|---|---|
| Sharpe annualisé | +0.49 | +0.79 |
| Rendement total | +5.7% | +108.5% |
| Max drawdown | -4.2% | -24.3% |
| Calmar | 0.31 | 0.64 |
| % jours en position | 60.7% | 100.0% |

## Statistiques de trades

- Nombre de trades : **58**
- Taux de réussite : 41.4%
- R moyen par trade : +0.24R
- Profit factor : 1.31
- Sorties stop / take-profit : 34 / 24
- Position ouverte en fin d'échantillon : oui

## Score — informations descriptives (non-décisionnelles)

- Score maximum observé sur l'échantillon : 9/10
- Séances à score=6 (setup faible, non tradées, seuil décisionnel = ≥7 uniquement) : 202
- Séances à score≥8 (signal très fort) : 121

- Sharpe B > Sharpe B&H : non
- Rendement B > B&H : non

**FAIL — critère pré-enregistré NON atteint (bat B&H simultanément en Sharpe ET rendement, seuil ≥7/10).**
