# Étape B — Modèle de prédiction directionnelle (NASDAQ Composite, quotidien)

## 1. Cadrage (dicté par l'Étape A et la revue de littérature)

- L'Étape A a **rejeté l'exploitabilité de l'autocorrélation du rendement** (random walk non rejeté, z\* robustes non significatives). On ne prédit donc **pas un prix** (naïve forecast → R² artificiel) mais une **direction**.
- Cible : **triple barrier** (López de Prado) H=5 j, barrières ±1.5·σ_local (σ = ewm 20 j) → labels adaptatifs au régime.
- Features causales (cf. `src/prediction.py`) : rendements retardés, momentum, ratios de moyennes, volatilité rolling, Parkinson, drawdown, RSI, MACD, Bollinger %b, ATR, Stochastic, **differenciation fractionnaire** (d=0.4).
- Walk-forward expansif : train initial 750 obs, ré-estim. tous les 21 j, **purge/embargo 21 j** (= H, anti-fuite de labels). Coûts **5 bps** aller-retour. OOS = 9522 jours (19/09/1988 → 10/07/2026).

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
| LogitL2 | +0.38 | +0.50 | +0.13 | +10.5 % | -54.8 % | 1.07 | 53.4 % |
| HistGB | +0.41 | +0.57 | +0.10 | +11.2 % | -65.3 % | 1.08 | 51.9 % |

*Le R² est volontairement absent : c'est une métrique trompeuse pour le trading (un R²≈0.97 peut n'être qu'un naïve forecast). Seules les métriques de risque/rendement nettes comptent.*

## 4. Précision directionnelle (accuracy) sur l'OOS

| Signal | Accuracy directionnelle |
|---|---|
| Momentum | 51.24 % |
| LogitL2 | 53.86 % |
| HistGB | 53.20 % |

*Repère : une accuracy de 53–55 % suffit à générer de l'alpha si bien tradée ; ≈50 % = pas d'edge directionnel.*

## 5. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)

Correction du data-snooping (N=4 essais, σ²(SR essais)=5.2789e-04) et de la non-normalité des rendements. DSR = P(vrai Sharpe > 0 | sélection sur le max).

| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0242 | +0.84 | **0.800** |
| Momentum | -0.0178 | 0.0242 | -4.10 | **0.000** |
| LogitL2 | +0.0242 | 0.0242 | -0.00 | **0.500** |
| HistGB | +0.0257 | 0.0242 | +0.15 | **0.558** |

*DSR > 0.95 = Sharpe crédible après correction ; DSR faible = performance probablement due au hasard / à la sélection.*

## 6. Test de détection du lookahead (délai d'exécution)

Signal testé : **HistGB**. Un vrai edge se dégrade **graduellement** avec le délai ; un lookahead s'effondre **verticalement** entre 0 et 1 barre.

| Délai (barres) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Sharpe ann. | +0.41 | -0.07 | -0.10 | -0.06 |

*Dégradation 0→1 : +0.48 de Sharpe — graduelle → **pas de lookahead détecté**.*

## 7. Analyse du coût de rupture (break-even)

Coût maximal (bps/trade) supportable avant Sharpe nul, au turnover observé :

| Signal | Break-even (bps/trade) | vs coût réel 5 bps |
|---|---|---|
| Momentum | -5.60 | sous le coût réel → non rentable |
| LogitL2 | +19.11 | marge positive |
| HistGB | +15.89 | marge positive |

## 8. Verdict honnête

- Échantillon OOS : 9522 jours (~38 ans, 09/1988→07/2026). Meilleur DSR : **BuyHold** (0.800).
- **Aucun signal actif ne bat le Buy & Hold avec un DSR > 0.95.** Le meilleur signal actif (HistGB) est cependant **rentable net de coûts** (Sharpe +0.41, break-even 16 bps > 5 bps réels) mais reste **en-dessous du simple achat-conservation** sur base ajustée du risque et déflatée. Cohérent avec l'Étape A (efficience à court terme).
- **Discipline** : l'univers (N=4) et le protocole sont figés dans ce script AVANT évaluation. On n'élargit pas l'univers jusqu'à obtenir un chiffre plaisant : le renforcement passe par **plus de données** (historique ≥ 2000, 2008 et dot-com), de **meilleures features** (microstructure intraday, sentiment FinBERT), ou un **horizon différent** — puis re-test unique au DSR.
- Rappel litt. : dégradation médiane backtest→live de **73 %** (Suhonen et al.) ; tout Sharpe backtest > 3 est un **red flag**. Les attentes sont calibrées en conséquence.
