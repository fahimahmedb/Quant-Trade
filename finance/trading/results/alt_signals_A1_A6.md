# Signaux alternatifs A1-A6 (NDX) — univers ignoré par l'Étape B

## 1. Contexte et objectif

L'Étape B a figé un univers N=4 (BuyHold, Momentum, LogitL2, HistGB) et conclu que **Buy & Hold reste la meilleure stratégie testée** (cf. CLAUDE.md). Ce script teste un **second univers disjoint**, figé avant évaluation, de 6 signaux à base de règles jamais évalués avec le protocole walk-forward strict de ce repo (contrairement aux scripts `run_hypothesis_*.py` antérieurs, qui calculent certains seuils sur l'échantillon complet — biais corrigé ici).

Protocole : NDX (`nasdaq100_daily.txt`), T0=750, refit=21 j, embargo=21 j (mécaniquement pertinent seulement pour A2, seul signal recalibré en walk-forward), coûts 5 bps aller-retour. OOS = 9522 jours (~38 ans, 09/1988→07/2026).

## 2. Univers de signaux (FIGÉ avant évaluation — N=6 essais actifs)

| # | Signal | Nature | Paramètres (fixés a priori) |
|---|---|---|---|
| A1 | RSI(14) simple | mean-reversion, baseline | seuils 30/70 (textbook) |
| A2 | RSI(14) + vol-targeting | A1 + overlay risque (analogue H12) | cap 1.5x, coupe 0.5x >p95 vol réalisée (walk-forward) |
| A3 | CCI(20) | mean-reversion, alternative à RSI | seuils ±100 (textbook) |
| A4 | Donchian(20) breakout | suivi de tendance (turtle) | canal 20 j, tenu jusqu'à casse opposée |
| A5 | ATR trend + stop Chandelier | entrée sur expansion de vol + tendance | ATR14>1.2×SMA50(ATR), EMA50, stop 3×ATR |
| A6 | ACF(1) raffinée | régime tendance/retour à la moyenne | fenêtre 60 j, seuil signif. 1.96/√60 |

*A6 corrige un défaut du signal `R10_ACF` déjà testé dans ce repo (`HYPOTHESIS_TESTING_RESULTS.md`, Sharpe -0.198) : R10 posait position = signe(ACF) seul, indépendamment du sens du dernier rendement — ici position = signe(ACF₁) × signe(rₜ) si significatif, sinon plat.*

## 3. Performance out-of-sample (nette de coûts), classée par Sharpe

| Rang | Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Turnover | Profit factor | Hit rate |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BuyHold **(BuyHold)** | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 0.000 | 1.10 | 54.8 % |
| 2 | A1_RSI | +0.28 | +0.20 | +0.06 | +2.4 % | -31.9 % | 0.060 | 1.19 | 5.1 % |
| 3 | A4_Donchian20 | +0.18 | +0.24 | +0.04 | +4.8 % | -65.9 % | 0.047 | 1.03 | 51.8 % |
| 4 | A3_CCI | +0.14 | +0.11 | +0.04 | +2.0 % | -35.7 % | 0.128 | 1.06 | 11.6 % |
| 5 | A6_ACF_Refined | +0.14 | +0.05 | +0.02 | +0.9 % | -45.4 % | 0.053 | 1.13 | 2.4 % |
| 6 | A2_RSI_VolTarget | +0.04 | +0.03 | +0.01 | +0.4 % | -41.0 % | 0.078 | 1.02 | 5.1 % |
| 7 | A5_ATR_TrendStop | -0.01 | -0.01 | -0.00 | -0.1 % | -61.2 % | 0.022 | 1.00 | 16.0 % |

*Le R² est volontairement absent (métrique trompeuse pour le trading, cf. Étape B). Turnover = variation moyenne absolue de position par jour OOS (proxy du coût de friction).*

## 4. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)

Univers N=7 essais (BuyHold + A1..A6, même convention que `run_etape_b.py`), σ²(SR essais)=1.2121e-04. DSR = P(vrai Sharpe > 0 | sélection sur le max).

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0153 | +1.71 | **0.956** |
| A1_RSI | +0.0178 | 0.0153 | +0.27 | **0.605** |
| A4_Donchian20 | +0.0114 | 0.0153 | -0.38 | **0.352** |
| A3_CCI | +0.0090 | 0.0153 | -0.61 | **0.270** |
| A6_ACF_Refined | +0.0088 | 0.0153 | -0.64 | **0.262** |
| A2_RSI_VolTarget | +0.0028 | 0.0153 | -1.23 | **0.110** |
| A5_ATR_TrendStop | -0.0005 | 0.0153 | -1.54 | **0.062** |

## 5. A1 vs A2 — l'overlay vol-targeting aide-t-il le RSI ?

- A1 (RSI brut) : Sharpe +0.28, MDD -31.9 %, Calmar +0.06.
- A2 (RSI + vol-targeting) : Sharpe +0.04, MDD -41.0 %, Calmar +0.01 (réduction de MDD vs A1 : -28.3 %).
- **Verdict** : l'overlay n'aide pas ici (ni Sharpe ni MDD améliorés) — cohérent avec Étape D : le vol-targeting sert surtout un signal déjà robuste (Buy & Hold), pas un signal RSI faible/bruité.

## 6. Test de détection du lookahead (délai d'exécution)

Signal testé : **A1_RSI** (meilleur Sharpe parmi A1-A6). Un vrai edge se dégrade **graduellement** avec le délai ; un lookahead s'effondre **verticalement** entre 0 et 1 barre.

| Délai (barres) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Sharpe ann. | +0.28 | +0.12 | -0.17 | -0.18 |

*Dégradation 0→1 : +0.17 de Sharpe — graduelle → **pas de lookahead détecté**.*

## 7. Verdict honnête

- Échantillon OOS : 9522 jours (~38 ans). Meilleur signal alternatif par Sharpe : **A1_RSI** (+0.28 vs BuyHold +0.52).
- **Aucun signal alternatif ne bat BuyHold en Sharpe**, même avant déflation.
- Aucun signal alternatif ne bat BuyHold avec un DSR > 0.95.
- Aucun signal alternatif ne réduit le MDD de plus de 30 % sans sacrifier plus de 20 % du rendement annualisé de BuyHold.
- **Conclusion** : cette exploration confirme, sur un second univers disjoint de règles techniques classiques (RSI, CCI, Donchian, ATR/Chandelier, ACF), qu'**on n'a pas raté de signal évident** : Buy & Hold demeure la référence sur NDX avec ce protocole. Cohérent avec l'Étape A (efficience) et l'Étape B (aucun signal directionnel ne bat BuyHold net de coûts et déflaté).

- **Discipline anti data-snooping** : univers N=6 figé avant évaluation, DSR compte N=7 essais (BuyHold inclus, même convention que l'Étape B). Aucun seuil n'a été retouché après avoir vu les résultats OOS.
