# Étape B — Modèle de prédiction directionnelle (NASDAQ Composite, quotidien)

## 1. Cadrage (dicté par l'Étape A et la revue de littérature)

- L'Étape A a **rejeté l'exploitabilité de l'autocorrélation du rendement** (random walk non rejeté, z\* robustes non significatives). On ne prédit donc **pas un prix** (naïve forecast → R² artificiel) mais une **direction**.
- Cible : **triple barrier** (López de Prado) H=5 j, barrières ±1.5·σ_local (σ = ewm 20 j) → labels adaptatifs au régime.
- Features causales (cf. `src/prediction.py`) : rendements retardés, momentum, ratios de moyennes, volatilité rolling, Parkinson, drawdown, RSI, MACD, Bollinger %b, ATR, Stochastic, **differenciation fractionnaire** (d=0.4).
- Walk-forward expansif : train initial 750 obs, ré-estim. tous les 21 j, **purge/embargo 5 j** (= H, anti-fuite de labels). Coûts **5 bps** aller-retour. OOS = 9522 jours (19/09/1988 → 10/07/2026).

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
| BuyHold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 1.10 | 54.8 % |
| Momentum | -0.28 | -0.38 | -0.02 | -7.1 % | -97.6 % | 0.95 | 50.6 % |
| LogitL2 | +0.30 | +0.39 | +0.08 | +8.3 % | -64.2 % | 1.06 | 53.2 % |
| HistGB | +0.23 | +0.31 | +0.04 | +6.1 % | -77.7 % | 1.04 | 52.0 % |

*Le R² est volontairement absent : c'est une métrique trompeuse pour le trading (un R²≈0.97 peut n'être qu'un naïve forecast). Seules les métriques de risque/rendement nettes comptent.*

## 4. Précision directionnelle (accuracy) sur l'OOS

| Signal | Accuracy directionnelle |
|---|---|
| Momentum | 51.24 % |
| LogitL2 | 53.67 % |
| HistGB | 52.33 % |

*Repère : une accuracy de 53–55 % suffit à générer de l'alpha si bien tradée ; ≈50 % = pas d'edge directionnel.*

## 5. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)

Correction du data-snooping (N=4 essais, σ²(SR essais)=4.5921e-04) et de la non-normalité des rendements. DSR = P(vrai Sharpe > 0 | sélection sur le max).

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0225 | +1.00 | **0.842** |
| Momentum | -0.0178 | 0.0225 | -3.94 | **0.000** |
| LogitL2 | +0.0192 | 0.0225 | -0.33 | **0.372** |
| HistGB | +0.0144 | 0.0225 | -0.79 | **0.214** |

*DSR > 0.95 = Sharpe crédible après correction ; DSR faible = performance probablement due au hasard / à la sélection.*

## 6. Test de détection du lookahead (délai d'exécution)

Signal testé : **LogitL2**. Un vrai edge se dégrade **graduellement** avec le délai ; un lookahead s'effondre **verticalement** entre 0 et 1 barre.

| Délai (barres) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Sharpe ann. | +0.30 | +0.12 | +0.05 | +0.03 |

*Dégradation 0→1 : +0.18 de Sharpe — graduelle → **pas de lookahead détecté**.*

## 7. Analyse du coût de rupture (break-even)

Coût maximal (bps/trade) supportable avant Sharpe nul, au turnover observé :

| Signal | Break-even (bps/trade) | vs coût réel 5 bps |
|---|---|---|
| Momentum | -5.60 | sous le coût réel → non rentable |
| LogitL2 | +16.56 | marge positive |
| HistGB | +11.26 | marge positive |

## 8. Verdict honnête

- Échantillon OOS : 9522 jours (~38 ans, 09/1988→07/2026). Meilleur DSR : **BuyHold** (0.842).
- **Aucun signal actif ne bat le Buy & Hold avec un DSR > 0.95.** Le meilleur signal actif (LogitL2) est cependant **rentable net de coûts** (Sharpe +0.30, break-even 17 bps > 5 bps réels) mais reste **en-dessous du simple achat-conservation** sur base ajustée du risque et déflatée. Cohérent avec l'Étape A (efficience à court terme).
- **Discipline** : l'univers (N=4) et le protocole sont figés dans ce script AVANT évaluation. On n'élargit pas l'univers jusqu'à obtenir un chiffre plaisant : le renforcement passe par **plus de données** (historique ≥ 2000, 2008 et dot-com), de **meilleures features** (microstructure intraday, sentiment FinBERT), ou un **horizon différent** — puis re-test unique au DSR.
- Rappel litt. : dégradation médiane backtest→live de **73 %** (Suhonen et al.) ; tout Sharpe backtest > 3 est un **red flag**. Les attentes sont calibrées en conséquence.
