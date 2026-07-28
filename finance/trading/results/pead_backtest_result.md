# Backtest PEAD — résultat (spécification pré-enregistrée, exécutée UNE fois)

Univers : NDX-100 actuel (99 tickers avec prix exploitable). Événements longs/courts retenus : 597/598 (tercile médian ignoré). 0 événements écartés faute de prix.

Terciles de surprise : long si surprise ≥ 10.62%, court si surprise ≤ 2.61%.

## Portefeuille long-short dollar-neutre (calendar-time, net de coûts 10bps)

- Période complète (2021-07-15 → 2026-07-27, 1263 jours actifs) : Sharpe ann. = +0.52, t-stat = +1.16
- Design (< 2024-01-01, 620 obs) : Sharpe ann. = +0.06
- Test (≥ 2024-01-01, 643 obs) : Sharpe ann. = +1.07
- Dégradation design→test : -1813.0%

## Verdict vis-à-vis du critère pré-enregistré

1. Sharpe>0 ET t-stat>2 sur période complète : NON
2. Sharpe test>0 ET dégradation<50% : OUI

**FAIL — critère pré-enregistré NON atteint.**

**Rappel des limites pré-enregistrées** : biais de survie (constituants NDX-100 actuels, pas point-in-time), coûts 10bps modélisés de façon simplifiée (5bps entrée + 5bps sortie, pas de slippage réel), jours de détention calés sur le calendrier propre à chaque titre (pas de gestion fine des jours fériés croisés). n_trials=1, aucune variante testée après ce résultat.
