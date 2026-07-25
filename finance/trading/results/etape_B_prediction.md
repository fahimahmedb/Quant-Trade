# Étape B — Modèle de prédiction directionnelle (NASDAQ Composite, quotidien)

## 1. Cadrage (dicté par l'Étape A et la revue de littérature)

- L'Étape A a **rejeté l'exploitabilité de l'autocorrélation du rendement** (random walk non rejeté, z\* robustes non significatives). On ne prédit donc **pas un prix** (naïve forecast → R² artificiel) mais une **direction**.
- Cible : **triple barrier** (López de Prado) H=5 j, barrières ±1.5·σ_local (σ = ewm 20 j) → labels adaptatifs au régime.
- Features causales (cf. `src/prediction.py`) : rendements retardés, momentum, ratios de moyennes, volatilité rolling, Parkinson, drawdown, RSI, MACD, Bollinger %b, ATR, Stochastic, **differenciation fractionnaire** (d=0.4).
- Walk-forward expansif : train initial 750 obs, ré-estim. tous les 21 j, **purge/embargo 5 j** (= H, anti-fuite de labels). Coûts **5 bps** aller-retour. OOS = 500 jours (10/07/2024 → 09/07/2026).

## 2. Univers de signaux (FIGÉ avant évaluation — N=4 pour le DSR)

| # | Signal | Nature |
|---|---|---|
| 1 | Buy & Hold | benchmark, toujours long |
| 2 | Momentum (signe rdt 10 j) | règle simple, sans apprentissage |
| 3 | Régression logistique L2 | modèle parcimonieux |
| 4 | Gradient boosting (HistGB) | analogue XGBoost/LightGBM |

## 3. Performance out-of-sample (nette de coûts)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate |
|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | +18.9 % | -24.3 % | 1.15 | 58.0 % |
| Momentum | -0.33 | -0.43 | -0.19 | -7.1 % | -32.8 % | 0.94 | 51.2 % |
| LogitL2 | -0.69 | -1.00 | -0.28 | -14.2 % | -42.3 % | 0.88 | 52.4 % |
| HistGB | +0.05 | +0.07 | +0.04 | +1.0 % | -23.6 % | 1.01 | 51.8 % |

*Le R² est volontairement absent : c'est une métrique trompeuse pour le trading (un R²≈0.97 peut n'être qu'un naïve forecast). Seules les métriques de risque/rendement nettes comptent.*

## 4. Précision directionnelle (accuracy) sur l'OOS

| Signal | Accuracy directionnelle |
|---|---|
| Momentum | 53.40 % |
| LogitL2 | 51.20 % |
| HistGB | 54.20 % |

*Repère : une accuracy de 53–55 % suffit à générer de l'alpha si bien tradée ; ≈50 % = pas d'edge directionnel.*

## 5. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)

Correction du data-snooping (N=4 essais, σ²(SR essais)=1.5777e-03) et de la non-normalité des rendements. DSR = P(vrai Sharpe > 0 | sélection sur le max).

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0493 | 0.0418 | +0.17 | **0.567** |
| Momentum | -0.0210 | 0.0418 | -1.41 | **0.079** |
| LogitL2 | -0.0435 | 0.0418 | -1.86 | **0.031** |
| HistGB | +0.0028 | 0.0418 | -0.87 | **0.192** |

*DSR > 0.95 = Sharpe crédible après correction ; DSR faible = performance probablement due au hasard / à la sélection.*

## 6. Test de détection du lookahead (délai d'exécution)

Signal testé : **HistGB**. Un vrai edge se dégrade **graduellement** avec le délai ; un lookahead s'effondre **verticalement** entre 0 et 1 barre.

| Délai (barres) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Sharpe ann. | +0.05 | +0.03 | +0.19 | +0.11 |

*Dégradation 0→1 : +0.02 de Sharpe — graduelle → **pas de lookahead détecté**.*

## 7. Analyse du coût de rupture (break-even)

Coût maximal (bps/trade) supportable avant Sharpe nul, au turnover observé :

| Signal | Break-even (bps/trade) | vs coût réel 5 bps |
|---|---|---|
| Momentum | -4.66 | sous le coût réel → non rentable |
| LogitL2 | -14.17 | sous le coût réel → non rentable |
| HistGB | +5.74 | marge positive |

## 8. Verdict honnête

- Échantillon OOS : 500 jours (~2 ans, 07/2024→07/2026). Meilleur DSR : **BuyHold** (0.567).
- **Aucun signal actif ne bat le Buy & Hold avec un DSR > 0.95.** Le meilleur signal actif (HistGB) est cependant **rentable net de coûts** (Sharpe +0.05, break-even 6 bps > 5 bps réels) mais reste **en-dessous du simple achat-conservation** sur base ajustée du risque et déflatée. Cohérent avec l'Étape A (efficience à court terme).
- **Discipline** : l'univers (N=4) et le protocole sont figés dans ce script AVANT évaluation. On n'élargit pas l'univers jusqu'à obtenir un chiffre plaisant : le renforcement passe par **plus de données** (historique ≥ 2000, 2008 et dot-com), de **meilleures features** (microstructure intraday, sentiment FinBERT), ou un **horizon différent** — puis re-test unique au DSR.
- Rappel litt. : dégradation médiane backtest→live de **73 %** (Suhonen et al.) ; tout Sharpe backtest > 3 est un **red flag**. Les attentes sont calibrées en conséquence.
