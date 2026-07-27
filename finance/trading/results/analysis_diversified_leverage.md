# Analyse — Diversification (4 marchés actions) + levier à risque égalisé

Fenêtre commune : 1999-11-02 → 2026-07-10 (6598 obs, ~26.2 ans). **Limite assumée : 4 indices ACTIONS uniquement — pas de vraie diversification multi-classes d'actifs (pas d'obligations/or/matières premières disponibles).**

## Corrélations des rendements quotidiens (fenêtre commune)

| | NDX | Russell 2000 | S&P 500 | DAX |
|---|---|---|---|---|
| NDX | 1.00 | 0.78 | 0.86 | 0.50 |
| Russell 2000 | 0.78 | 1.00 | 0.89 | 0.54 |
| S&P 500 | 0.86 | 0.89 | 1.00 | 0.59 |
| DAX | 0.50 | 0.54 | 0.59 | 1.00 |

## Portefeuille diversifié (risk parity, non levé) vs chaque marché seul

| | Sharpe ann. | Vol ann. % | Calmar | MDD % | Rdt ann. % |
|---|---|---|---|---|---|
| **Portefeuille diversifié** | +0.34 | 19.7 | +0.08 | -57.7 | +6.9 |
| NDX (seul) | +0.28 | 27.1 | +0.05 | -81.3 | +7.9 |
| Russell 2000 (seul) | +0.27 | 24.4 | +0.06 | -63.9 | +6.8 |
| S&P 500 (seul) | +0.31 | 19.3 | +0.07 | -59.3 | +6.2 |
| DAX (seul) | +0.18 | 22.4 | +0.03 | -70.3 | +4.2 |

## Portefeuille diversifié LEVÉ à risque égalisé sur S&P 500 (meilleur Sharpe seul)

Levier appliqué = min(CAP=3.0, vol(S&P 500)/vol(diversifié)) = **0.98×**

| | Sharpe ann. | Vol ann. % | Calmar | MDD % | Rdt ann. % |
|---|---|---|---|---|---|
| S&P 500 (seul, référence) | +0.31 | 19.3 | +0.07 | -59.3 | +6.2 |
| **Diversifié × 0.98** | +0.34 | 19.3 | +0.08 | -57.1 | +6.8 |

**Verdict honnête** : à volatilité annualisée égalisée (~19.3%), le portefeuille diversifié levé apporte un supplément de rendement de +0.5 points annualisés vs S&P 500 seul (bénéfice de diversification réel). Rappel : ceci reste une diversification actions-actions uniquement — un vrai portefeuille risk-parity inclurait obligations/or/matières premières, non disponibles ici.
