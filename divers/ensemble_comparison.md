# Comparaison univers primaires complet — 4 signaux × {solo, +overlay} (NDX)

## 1. Cadrage

Objectif (cf. `CLAUDE.md`, Étape D) : l'overlay vol-targeting GJR-GARCH(1,1)-t (cap, coupe extrême — réglage **déjà retenu**, cf. `results/etape_D_overlay_optimized.md`, pas re-optimisé ici) n'avait été vérifié que sur Buy & Hold (Étape D) et sur LogitL2 seul (`results/integrated_pipeline.md`). Ce script étend la même question aux **4 signaux primaires de l'Étape B simultanément** : quel signal bénéficie le plus de l'overlay, et une combinaison simple des 4 bat-elle Buy & Hold ?

**Protocole figé** : NDX (`nasdaq100_daily.txt`), walk-forward T0=750, ré-estimation tous les 21 j, purge/embargo 5 j (triple barrier H=5 j, ±1.5·σ_ewm20), coûts 5 bps aller-retour. Overlay : cap 2.0×, coupe totale au 90e percentile in-sample. OOS = 9522 jours (19/09/1988 → 10/07/2026).

## 2. Univers de 8 variantes (FIGÉ avant évaluation — N=8 pour le DSR)

| # | Variante | Composition |
|---|---|---|
| 1 | BuyHold | toujours long, benchmark |
| 2 | BuyHold+Overlay | toujours long, benchmark × exposition vol-targeting GJR-t |
| 3 | Momentum | signe du rendement 10 j |
| 4 | Momentum+Overlay | signe du rendement 10 j × exposition vol-targeting GJR-t |
| 5 | LogitL2 | régression logistique L2 (Étape B) |
| 6 | LogitL2+Overlay | régression logistique L2 (Étape B) × exposition vol-targeting GJR-t |
| 7 | HistGB | gradient boosting (Étape B) |
| 8 | HistGB+Overlay | gradient boosting (Étape B) × exposition vol-targeting GJR-t |

## 3. Performance out-of-sample (nette de coûts)

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 1.10 | 54.8 % | 0.000 |
| BuyHold+Overlay | +0.65 | +0.84 | +0.19 | +16.5 % | -55.1 % | 1.12 | 48.1 % | 0.057 |
| Momentum | -0.28 | -0.38 | -0.02 | -7.1 % | -97.6 % | 0.95 | 50.6 % | 0.275 |
| Momentum+Overlay | -0.31 | -0.43 | -0.02 | -7.2 % | -97.9 % | 0.95 | 44.3 % | 0.378 |
| LogitL2 | +0.30 | +0.39 | +0.08 | +8.3 % | -64.2 % | 1.06 | 53.2 % | 0.272 |
| LogitL2+Overlay | +0.46 | +0.61 | +0.18 | +11.6 % | -44.9 % | 1.09 | 46.8 % | 0.326 |
| HistGB | +0.23 | +0.31 | +0.04 | +6.1 % | -77.7 % | 1.04 | 52.0 % | 0.378 |
| HistGB+Overlay | +0.07 | +0.10 | +0.01 | +1.8 % | -70.1 % | 1.01 | 45.3 % | 0.480 |

## 4. Deflated Sharpe Ratio (N=8, univers des 8 variantes)

σ²(SR essais) = 5.0689e-04.

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0328 | -0.00 | **0.499** |
| BuyHold+Overlay | +0.0406 | 0.0328 | +0.75 | **0.774** |
| Momentum | -0.0178 | 0.0328 | -4.95 | **0.000** |
| Momentum+Overlay | -0.0197 | 0.0328 | -5.14 | **0.000** |
| LogitL2 | +0.0192 | 0.0328 | -1.33 | **0.092** |
| LogitL2+Overlay | +0.0292 | 0.0328 | -0.35 | **0.362** |
| HistGB | +0.0144 | 0.0328 | -1.80 | **0.036** |
| HistGB+Overlay | +0.0047 | 0.0328 | -2.75 | **0.003** |

## 5. Effet de l'overlay, signal par signal

Seuils de succès déclarés avant lecture : DSR(+overlay) ≥ DSR(BuyHold), OU réduction de MDD > 30 % (relatif, +overlay vs le même signal seul) sans perdre plus de 20 % de rendement annualisé.

| Signal | ΔMDD relatif (+overlay) | Rdt ann. conservé | DSR(+overlay) ≥ DSR(BuyHold) ? | Critère MDD/rdt ? | **Succès** |
|---|---|---|---|---|---|
| Momentum | -0.3 % | 101.2 % | non | non | non |
| LogitL2 | +30.1 % | 141.0 % | non | OUI | **OUI** |
| HistGB | +9.8 % | 28.8 % | non | non | non |

## 6. Bonus — portefeuilles combinés (EXPLORATOIRE, hors protocole figé N=8)

**Avertissement anti data-snooping** : les poids Sharpe-pondérés sont calculés à partir du Sharpe OOS de la **même fenêtre** évaluée ci-dessous (pas de split train/test séparé pour les poids). Ce n'est donc **pas** un test out-of-sample indépendant — résultat illustratif uniquement, non compté dans le DSR (N=8) ci-dessus, ne remplace pas un protocole à poids fixés a priori.

Poids égal-poids : BuyHold=0.25, Momentum=0.25, LogitL2=0.25, HistGB=0.25. Poids Sharpe-pondéré : BuyHold=0.49, Momentum=0.00, LogitL2=0.29, HistGB=0.22.

| Portefeuille | Sharpe ann. | Calmar | Rdt ann. | MDD | Turnover/j |
|---|---|---|---|---|---|
| EqualWeight | +0.35 | +0.06 | +5.6 % | -60.1 % | 0.199 |
| EqualWeight+Overlay | +0.35 | +0.10 | +6.1 % | -44.3 % | 0.251 |
| SharpeWeighted | +0.48 | +0.08 | +11.0 % | -71.3 % | 0.149 |
| SharpeWeighted+Overlay | +0.56 | +0.19 | +12.1 % | -44.8 % | 0.200 |

*Pour référence, BuyHold seul (protocole figé, section 3) : Sharpe ann. +0.52, Calmar +0.08, MDD -82.9 %.*

- Meilleur portefeuille (Sharpe ann.) : **SharpeWeighted+Overlay** — bat BuyHold en Sharpe (résultat exploratoire, cf. avertissement ci-dessus).

## 7. Verdict honnête

Meilleur DSR de l'univers figé (N=8) : **BuyHold+Overlay** (0.774). DSR BuyHold seul (référence) : **0.499**.

**Critère de succès atteint** pour LogitL2 : au moins un signal primaire actif + overlay satisfait le critère déclaré en section 5 (DSR ≥ BuyHold, ou réduction de MDD matérielle sans perte excessive de rendement). Détail par signal : voir tableau section 5.

Discipline anti data-snooping : 8 variantes figées avant évaluation, DSR déflaté sur cette famille (n_trials=8) ; aucun paramètre de l'overlay (cap 2.0×, percentile 90e) n'a été retouché après avoir vu ce résultat — il provient d'une recherche antérieure déjà publiée dans le repo. La section 6 (portefeuilles) est explicitement exploratoire et exclue de ce compte N=8.
