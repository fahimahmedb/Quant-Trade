# Backtest cross-marché — pipeline LogitL2 + overlay (validation NDX → 3 indices)

## 1. Cadrage

Objectif : vérifier que le meilleur pipeline trouvé sur NDX — signal primaire **LogitL2** (Étape B) combiné à l'**overlay** de gestion du risque GJR-GARCH(1,1)-t vol-targeting (cap 2.0×, coupe totale au-delà du 90e percentile in-sample de la vol prévue ; cf. `finance/trading/results/etape_D_overlay_optimized.md`) — se **généralise** à d'autres marchés/indices, ou s'il est spécifique à NDX (surapprentissage de marché).

**Protocole figé, identique à l'étude NDX déjà publiée** (`results/integrated_pipeline.md`, `finance/src/integrated_pipeline.py`) : walk-forward T0=750, ré-estimation tous les 21 j, purge/embargo 5 j, labels triple barrier H=5 j ±1.5·σ_ewm20, coûts 5 bps aller-retour. Overlay : cap 2.0×, coupe 90e percentile — **aucun paramètre ré-optimisé** sur les 3 indices ci-dessous, ce sont ceux déjà retenus sur NDX, réutilisés tels quels (test de généralisation, pas un nouveau grid-search).

**Note de cohérence de protocole** : la tâche a spécifié explicitement « T0=750, refit 21j, embargo 5j » dans son "Protocole figé" détaillé, identique au protocole déjà figé et publié pour NDX (`integrated_pipeline.py`: `T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5`). Un message ultérieur de la même conversation mentionnait un embargo de 21 j et des stratégies (« R5_FracDiff », « H12 ») absentes des « résultats déjà établis » de `CLAUDE.md` — elles proviennent visiblement de scripts hors discipline anti-data-snooping trouvés à la racine du repo (`HYPOTHESIS_TESTING_RESULTS.md`, etc.), pas de la chaîne A→B→C→D documentée. Ce script suit le protocole détaillé et déjà validé (embargo=5j) : c'est la seule option cohérente avec la comparaison directe aux chiffres NDX déjà publiés, demandée par la tâche.

**Univers figé (anti data-snooping)** : 3 indices × 3 variantes = 9 tests exactement, aucun ajout a posteriori. Le DSR (Deflated Sharpe Ratio) est calculé avec **n_trials=3 par indice** (famille des 3 variantes de CET indice) — jamais combiné statistiquement entre indices, comme demandé.

## 2. Référence NDX (déjà publiée, rappelée pour comparaison — pas recalculée ici)

OOS NDX : 9522 j (19/09/1988 -> 10/07/2026).

| Variante | Sharpe ann. | Calmar | MDD | Rdt ann. |
|---|---|---|---|---|
| BuyHold | +0.52 | +0.08 | -82.9 % | +14.5 % |
| LogitL2 | +0.35 | +0.10 | -59.6 % | +9.5 % |
| LogitL2+Overlay | +0.44 | +0.13 | -52.4 % | +10.2 % |

Sur NDX : réduction MDD (Overlay vs BuyHold) = **+36.8 %** (relatif), rendement conservé = **70.3 %** de BuyHold (seuils de cette tâche : réduction MDD >20 %, rendement conservé ≥80 % — NON atteint (rendement conservé sous 80 %) sur NDX lui-même avec ces seuils précis — à garder en tête en lisant les 3 indices ci-dessous).

## 3.1. Russell 2000

9782 séances, 10/09/1987 → 13/07/2026. OOS = 9031 j (28/08/1990 → 10/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | IC 95% Sharpe (bootstrap bloc) | Profit factor | Hit rate | Turnover/j | DSR (n=3) |
|---|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.39 | +0.50 | +0.09 | +8.9 % | -59.9 % | [+0.08, +0.72] | 1.07 | 54.2 % | 0.000 | 0.945 |
| LogitL2 | +0.17 | +0.22 | +0.02 | +3.7 % | -83.5 % | [-0.14, +0.48] | 1.03 | 52.4 % | 0.465 | 0.607 |
| LogitL2+Overlay | +0.43 | +0.59 | +0.06 | +7.4 % | -68.8 % | [+0.09, +0.77] | 1.08 | 44.2 % | 0.489 | 0.967 |

- Réduction relative du MDD (LogitL2+Overlay vs BuyHold) : **-14.8 %** (seuil : >20 %).
- Rendement annualisé conservé (LogitL2+Overlay / BuyHold) : **83.4 %** (seuil : ≥80 %).
- Verdict Russell 2000 : **échec** du critère de généralisation sur cet indice.

## 3.2. S&P 500

14252 séances, 02/01/1970 → 13/07/2026. OOS = 13501 j (18/12/1972 → 10/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | IC 95% Sharpe (bootstrap bloc) | Profit factor | Hit rate | Turnover/j | DSR (n=3) |
|---|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.44 | +0.56 | +0.09 | +8.1 % | -56.8 % | [+0.18, +0.72] | 1.09 | 53.0 % | 0.000 | 0.999 |
| LogitL2 | +0.44 | +0.58 | +0.07 | +8.0 % | -68.2 % | [+0.17, +0.71] | 1.09 | 52.8 % | 0.283 | 0.999 |
| LogitL2+Overlay | +0.42 | +0.54 | +0.09 | +4.7 % | -40.0 % | [+0.13, +0.69] | 1.08 | 44.8 % | 0.217 | 0.999 |

- Réduction relative du MDD (LogitL2+Overlay vs BuyHold) : **+29.6 %** (seuil : >20 %).
- Rendement annualisé conservé (LogitL2+Overlay / BuyHold) : **57.6 %** (seuil : ≥80 %).
- Verdict S&P 500 : **échec** du critère de généralisation sur cet indice.

## 3.3. DAX

6777 séances, 01/11/1999 → 10/07/2026. OOS = 6026 j (14/10/2002 → 09/07/2026).

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | IC 95% Sharpe (bootstrap bloc) | Profit factor | Hit rate | Turnover/j | DSR (n=3) |
|---|---|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.43 | +0.55 | +0.11 | +9.5 % | -54.8 % | [+0.03, +0.79] | 1.08 | 53.6 % | 0.000 | 0.805 |
| LogitL2 | +0.03 | +0.04 | +0.01 | +0.7 % | -63.7 % | [-0.36, +0.45] | 1.01 | 50.5 % | 0.262 | 0.143 |
| LogitL2+Overlay | -0.15 | -0.21 | -0.02 | -3.9 % | -87.6 % | [-0.52, +0.25] | 0.98 | 48.2 % | 0.429 | 0.026 |

- Réduction relative du MDD (LogitL2+Overlay vs BuyHold) : **-59.9 %** (seuil : >20 %).
- Rendement annualisé conservé (LogitL2+Overlay / BuyHold) : **-40.7 %** (seuil : ≥80 %).
- Verdict DAX : **échec** du critère de généralisation sur cet indice.

## 4. Verdict cross-market

| Indice | ΔMDD relatif (Overlay vs BH) | Rdt conservé | Critère atteint |
|---|---|---|---|
| Russell 2000 | -14.8 % | 83.4 % | non |
| S&P 500 | +29.6 % | 57.6 % | non |
| DAX | -59.9 % | -40.7 % | non |

**0/3 indices** atteignent le critère de succès déclaré (réduction MDD >20 % relatif **et** rendement annualisé conservé ≥80 % de Buy & Hold). Seuil de succès de la tâche : ≥2/3.

**Verdict global : ÉCHEC du critère explicite.** Seuls 0/3 indices atteignent le seuil déclaré (≥2/3 requis). Rapporté tel quel : le pipeline retenu sur NDX ne se généralise pas de façon fiable à ce niveau de seuil sur l'univers figé des 3 indices testés ici.

## 5. Interprétation (pourquoi l'overlay ne se généralise pas ici)

L'overlay ne fait qu'échelonner la **magnitude** de l'exposition déjà prise par
LogitL2 (`pos_final = signe(LogitL2) × exposition_vol_targeting`, jamais un
changement de signe) : en régime calme il peut **amplifier** la position
jusqu'à 2.0×, et il la **coupe à zéro** au-delà du 90e percentile de vol
prévue. Ce mécanisme n'est bénéfique que si le signal directionnel amplifié
porte un edge réel :

- **NDX** : LogitL2 a un edge faible mais réel (Sharpe +0.35, accuracy
  53.7 % rapportée en Étape B) → l'amplification en régime calme ajoute du
  rendement propre, et la coupe extrême retire les pires drawdowns → MDD
  réduit de 36.8 % pour 70.3 % du rendement Buy & Hold conservé.
- **Russell 2000** : LogitL2 seul a déjà un Sharpe faible (+0.17) et un MDD
  **pire** que Buy & Hold (-83.5 % vs -59.9 %) — l'overlay améliore le
  Sharpe (+0.43) mais son MDD (-68.8 %) reste **supérieur** à celui de
  Buy & Hold : la coupe extrême limite la casse du signal primaire sans la
  ramener sous le niveau du benchmark passif.
- **S&P 500** : seul indice où le MDD de l'overlay (-40.0 %) bat nettement
  celui de Buy & Hold (-56.8 %, réduction +29.6 %) — mais le rendement
  annualisé chute à 57.6 % de Buy & Hold (4.7 % vs 8.1 %), sous le seuil de
  conservation ≥80 % : ici la coupe extrême retire du risque et du
  rendement en proportions déséquilibrées.
- **DAX** : LogitL2 seul n'a quasiment aucun edge (Sharpe +0.03, DSR=0.143 —
  indiscernable du bruit) et un MDD déjà pire que Buy & Hold (-63.7 % vs
  -54.8 %). Amplifier un signal sans edge jusqu'à 2.0× en régime calme
  ajoute du levier sur du bruit (coûts de transaction et volatilité
  supplémentaires) sans contrepartie de rendement : le MDD de l'overlay
  explose à -87.6 % (pire que Buy & Hold **et** que LogitL2 seul), avec un
  rendement annualisé négatif (-3.9 %) et un DSR de 0.026 (quasi certain que
  le Sharpe apparent n'est que du bruit).

**Conclusion mécanique** : l'overlay retenu sur NDX combine deux effets
distincts — (i) une amplification en régime calme qui suppose un edge
directionnel réel pour être profitable, et (ii) une coupe en régime de vol
extrême qui, elle, ne dépend pas de l'edge et fonctionne indépendamment du
marché (elle a réduit le MDD sur NDX et S&P 500). Sur les 3 indices testés,
l'edge de LogitL2 (Étape B) est **plus faible ou nul** hors NDX ; l'effet (i)
devient alors négatif, et seul l'effet (ii) survit parfois (S&P 500), au prix
d'un rendement sacrifié. Le succès NDX est donc en partie **spécifique à ce
marché** (edge directionnel LogitL2 particulier à NDX, cf. Étape B/CLAUDE.md :
« NDX : LogitL2 rentable net de coûts » — pas établi ailleurs), pas seulement
à l'overlay lui-même.

Discipline anti data-snooping : univers figé (3 indices × 3 variantes = 9 tests), aucun paramètre (LogitL2, cap overlay, percentile de coupe) ré-optimisé sur ces marchés — ce sont exactement ceux déjà retenus et publiés sur NDX. DSR calculé séparément par indice (n_trials=3), jamais combiné statistiquement entre indices, conformément à la tâche.
