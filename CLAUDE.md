# Quant-Trade — contexte projet (lu automatiquement par toute session/agent)

Outil probabiliste sur indices NASDAQ. Trois étapes construites (A, B, C),
une quatrième en cours (D). Historique complet dans le repo, mais voici
l'essentiel pour ne pas repartir de zéro.

## Fichiers de données (`data/`)

- `nasdaq_composite_daily.txt` — **échantillon PRÉ-ENREGISTRÉ, NE JAMAIS MODIFIER.**
  NASDAQ Composite, 13/07/2021→10/07/2026, 1251 séances. Toutes les analyses
  "protocole figé" de référence tournent dessus par défaut.
- `nasdaq100_daily.txt` — NASDAQ-100 (NDX), 01/10/1985→13/07/2026, 10273
  séances (ère à volume réel ≥ 1985 uniquement ; fourni par l'utilisateur,
  nettoyé : 2 arrondis OHLC corrigés). Sert à ré-exécuter le même protocole
  sur un historique long (40 ans, plusieurs cycles).

Format (tabulé, fins de ligne CRLF, décimales `.`) :
```
date	ouv	haut	bas	clot	vol	devise	
13/07/2021 00:00	14715.133	14803.676	14660.19	14677.654	0	Pts	
```
Chargement : `src/data_loader.py::load_ohlc(path)` → DataFrame `[date,open,high,low,close]`.
`quality_report(df)` valide (lève si dates dupliquées ou OHLC incohérent).

## Code (`src/`)

- `data_loader.py` — `load_ohlc`, `quality_report`, `log_returns_pct` (rendements
  log %, close-to-close), `parkinson_var_pct` (variance range-based intra-séance).
- `diagnostics.py` (Étape A) — `summary_stats`, `lo_mackinlay_vr(r,q)` (ratio de
  variance, z homoscéd. et z\* robuste hétéro.), `ljung_box`, `acf`,
  `engle_arch_lm`, `fit_student_t`.
- `prediction.py` (Étape B) — `build_features(df)` (features CAUSALES : momentum,
  vol rolling, RSI/MACD/Bollinger/ATR/Stochastic, differenciation fractionnaire
  `frac_diff`), `triple_barrier_labels(df,horizon,vol_span,mult)` (labels
  ±1/0, barrières ∝ vol locale ewm), `walk_forward_signals` (purge/embargo),
  `backtest(pos,r_fwd,cost_bps,delay)`, `trading_metrics` (Sharpe/Sortino/
  Calmar/MDD/profit factor — **jamais le R²**), `dsr` (Deflated Sharpe Ratio,
  Bailey & López de Prado 2014).
- `volatility.py` (Étape C) — `ARCH_SPECS` (GARCH-n/t, GJR-t, GJR-skewt),
  `fit_arch`, `garch_path`/`garch_multistep` (récursions maison, validées vs
  `arch`), `ewma_path`, `fit_har`/`har_forecast` (HAR sur RV Parkinson),
  `qlike`/`mse`, `spa_test` (SPA de Hansen, bootstrap stationnaire), `dm_test`
  (Diebold-Mariano, HAC).

## Scripts (`scripts/`)

Chacun : `python3 scripts/run_etape_X.py [chemin_données] [chemin_sortie]`
(défaut = Composite pré-enregistré + `results/etape_X_....md`).
`run_etape_c.py` respecte la variable d'env `REFIT_EVERY` (défaut 5 ; utiliser
21 sur les historiques longs, sinon très lent — ~450 ré-estimations GARCH
sinon des milliers).

## Résultats déjà établis (ne PAS refaire, seulement RÉUTILISER)

**Étape A** — Composite (5 ans) : random walk NON rejeté (z\* robuste
non significative). NDX (40 ans) : random walk **REJETÉ** (VR(5)=0,89,
z\*=−2,68, p=0,007 → retour à la moyenne faible mais détecté). Effet ARCH
massif et queues épaisses (ν≈4,8 non conditionnel) dans les deux cas.

**Étape B** — univers figé N=4 (BuyHold, Momentum signe rdt-10j, Logit L2,
HistGB). Triple-barrier H=5j, ±1,5σ (ewm 20j). Walk-forward T0=750,
purge/embargo=5j, coûts 5 bps aller-retour.
- Composite : **aucun signal actif ne bat Buy & Hold** à DSR>0,95 (DSR
  BuyHold=0,567, le meilleur).
- NDX : LogitL2 **rentable net de coûts** (Sharpe +0,30, accuracy 53,7 %,
  break-even ≈17 bps ≫ 5 bps) mais **encore sous Buy & Hold** en DSR
  (BuyHold 0,842 vs LogitL2 0,372).
- **Conclusion actuelle : Buy & Hold reste la meilleure stratégie testée.**

**Étape C** — univers figé N=6 (EWMA, GARCH-n=bench, GARCH-t, GJR-t,
GJR-skewt, HAR-P). Perte QLIKE, test DM vs bench, test SPA famille entière.
- Composite (500 obs OOS) : GJR-t bat le bench (DM p=0,014 h=1, p=0,030 h=5)
  mais le SPA famille entière **échoue** (p≈0,11–0,15, non robuste — limite
  d'échantillon).
- NDX (9522 obs OOS) : GJR-t/GJR-skewt battent le bench ET **passent le SPA**
  (p=0,0000 h=1, p=0,0034 h=5) → **edge de volatilité statistiquement solide**.
- **Le modèle de volatilité C est le plus robuste des trois — utile pour le
  risk management (position sizing, VaR), pas pour prédire une direction.**

## Étape D (construite et validée — partiellement)

Overlay défensif combinant B (direction, faible) + C (volatilité, robuste) :
`finance/src/overlay.py` (vol-targeting GJR-t + coupe au 95e percentile
in-sample, cap 1,5×) ; script `finance/trading/scripts/run_etape_d.py` ;
résultat `finance/trading/results/etape_D_overlay.md`. Critère pré-enregistré :
réduction MDD >25 % relatif ET rendement annualisé conservé ≥80 % de Buy&Hold.

- **NDX (40 ans)** : VolTarget+Cut **ATTEINT** le critère — MDD −82,9 %→−57,2 %
  (réduction relative 31,0 %), rendement annualisé conservé à 111,2 % de BH,
  Calmar amélioré (+0,18 vs +0,08). **Résultat le plus solide de gestion du
  risque de tout le projet.**
- **Composite (5 ans)** : critère NON atteint (réduction MDD 17,4 % < seuil
  25 %, rendement conservé 69,1 % < seuil 80 %).
- **Généralisation cross-marché testée et documentée** (backlog #165-#170,
  `PREREG_gjr_vol_managed_crossmarket.md`) : l'edge GJR-t vol-targeting
  **NE généralise PAS** à S&P 500/Russell 2000/DAX — passe nominalement
  mais échoue une fois les coûts de financement réalistes appliqués
  (Règle 10, DGS3MO) ; DAX échoue net. Méga-famille vol-targeting déclarée
  close (synthèse #256/#371).
- **Conclusion honnête** : l'overlay défensif Étape D fonctionne
  spécifiquement sur NDX (40 ans d'historique), pas ailleurs — à ne pas
  généraliser au-delà de ce qui est montré dans `etape_D_overlay.md`.

## Discipline anti-data-snooping (NON NÉGOCIABLE)

Les univers de modèles/signaux et les protocoles OOS sont **figés avant
évaluation** dans chaque script. Toute extension doit être déclarée, comptée
(N essais) et re-testée au SPA/DSR. On n'itère jamais sur l'échantillon de
test jusqu'à un chiffre plaisant. R² interdit comme métrique de succès —
seules les métriques de trading nettes de coûts comptent.

## Git

Branche de travail : `claude/price-prediction-model-ykhog1`. Ne pas modifier
`data/nasdaq_composite_daily.txt` (échantillon pré-enregistré). Ne pas
pousser sans consigne explicite si vous êtes un sous-agent — laissez
l'orchestrateur intégrer et pousser.
