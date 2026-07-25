# Pipeline intégrée B → meta-labeling → overlay (NDX 40 ans)

## 1. Cadrage

Objectif (cf. `CLAUDE.md`, Étape D) : vérifier que la **combinaison** des trois composantes déjà construites — signal primaire (Étape B), filtre meta-labeling, overlay de gestion du risque (Étape D optimisée) — réduit le max drawdown du **signal actif LogitL2 lui-même**, pas seulement celui de Buy & Hold (déjà traité dans `finance/trading/results/etape_D_overlay_optimized.md`).

Aucun des trois moteurs n'est réinventé : le primaire, le secondaire du meta-labeling et les paramètres de l'overlay sont ceux **déjà retenus** dans les études précédentes du repo (`meta_labeling_multi.md` : secondaire LogitL2, DSR=0.866 ; `etape_D_overlay_optimized.md` : cap 2.0×, coupe au 90e percentile), pas re-optimisés ici.

Position finale générique (chaque variante est un cas particulier, composante absente = neutre) :

```
pos_final = signe(LogitL2) × confiance_meta_labeling × exposition_overlay
```

**Protocole figé** : NDX (`nasdaq100_daily.txt`), walk-forward T0=750, ré-estimation tous les 21 j, purge/embargo 5 j (triple barrier H=5 j, ±1.5·σ_ewm20), coûts 5 bps aller-retour. OOS = 9522 jours (19/09/1988 → 10/07/2026).

## 2. Univers de 5 variantes (FIGÉ avant évaluation — N=5 pour le DSR)

| # | Variante | Composition |
|---|---|---|
| 1 | Buy & Hold | benchmark, toujours long |
| 2 | LogitL2 seul | signal primaire (Étape B) |
| 3 | LogitL2 + meta-labeling | primaire × confiance secondaire LogitL2 |
| 4 | LogitL2 + overlay | primaire × exposition vol-targeting |
| 5 | LogitL2 + meta-labeling + overlay | pipeline complète |

## 3. Performance out-of-sample (nette de coûts)

| Variante | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate | Turnover/j |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 1.10 | 54.8 % | 0.000 |
| LogitL2 | +0.35 | +0.45 | +0.10 | +9.5 % | -59.6 % | 1.07 | 53.4 % | 0.268 |
| LogitL2+Meta | +0.28 | +0.28 | +0.06 | +1.4 % | -19.2 % | 1.10 | 38.5 % | 0.039 |
| LogitL2+Overlay | +0.44 | +0.58 | +0.13 | +10.2 % | -52.4 % | 1.08 | 46.9 % | 0.320 |
| LogitL2+Meta+Overlay | +0.23 | +0.22 | +0.05 | +0.7 % | -14.4 % | 1.06 | 34.7 % | 0.040 |

## 4. Deflated Sharpe Ratio (N=5, univers des 5 variantes)

σ²(SR essais) = 5.5399e-05.

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0089 | +2.33 | **0.990** |
| LogitL2 | +0.0219 | 0.0089 | +1.27 | **0.898** |
| LogitL2+Meta | +0.0175 | 0.0089 | +0.84 | **0.799** |
| LogitL2+Overlay | +0.0277 | 0.0089 | +1.82 | **0.966** |
| LogitL2+Meta+Overlay | +0.0145 | 0.0089 | +0.55 | **0.708** |

## 5. Effet sur le drawdown du signal actif (LogitL2 seul vs pipeline complète)

- LogitL2 seul (variante 2) : MDD **-59.6 %**, rendement annualisé +9.5 %, Sharpe ann. +0.35.
- LogitL2 + meta-labeling + overlay (variante 5) : MDD **-14.4 %**, rendement annualisé +0.7 %, Sharpe ann. +0.23.
- Réduction relative du MDD : **+75.9 %** (seuil de succès déclaré : > 25 %).
- Rendement annualisé conservé : **7.5 %** de la variante 2 (seuil de succès déclaré : ≥ 50 %).

## 6. Verdict honnête

**Critère de succès non atteint** (rendement conservé (7.5 %) sous le seuil de 50 %). Rapporté tel quel, sans le présenter comme un succès.

Meilleur DSR de l'univers : **BuyHold** (0.990). Rappel (cf. `CLAUDE.md`, Étape B/D) : Buy & Hold reste la stratégie de référence sur NDX en Sharpe/DSR brut ; l'objet de cette pipeline n'est pas de la battre en rendement mais de vérifier si la combinaison des trois composantes améliore le **profil risque du signal actif lui-même** — conclusion à lire à la lumière du tableau ci-dessus, pas en absolu.

Discipline anti data-snooping : 5 variantes figées avant évaluation, DSR déflaté sur cette famille (n_trials=5) ; aucun paramètre (secondaire meta, cap/percentile overlay) n'a été retouché après avoir vu ce résultat combiné - ils proviennent de recherches antérieures déjà publiées dans le repo (finance/src/meta_labeling.py, finance/src/overlay.py).
