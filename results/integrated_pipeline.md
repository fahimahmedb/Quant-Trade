# Pipeline intégrée B → meta-labeling → overlay (NDX 40 ans)

## 1. Cadrage

Objectif (cf. `CLAUDE.md`, Étape D) : vérifier que la **combinaison** des trois composantes déjà construites — signal primaire (Étape B), filtre meta-labeling, overlay de gestion du risque (Étape D optimisée) — réduit le max drawdown du **signal actif LogitL2 lui-même**, pas seulement celui de Buy & Hold (déjà traité dans `results/etape_D_overlay_optimized.md`).

Aucun des trois moteurs n'est réinventé : le primaire, le secondaire du meta-labeling et les paramètres de l'overlay sont ceux **déjà retenus** dans les études précédentes du repo (`results/meta_labeling_multi.md` : secondaire LogitL2, DSR=0.866 ; `results/etape_D_overlay_optimized.md` : cap 2.0×, coupe au 90e percentile), pas re-optimisés ici.

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
| LogitL2 | +0.30 | +0.39 | +0.08 | +8.3 % | -64.2 % | 1.06 | 53.2 % | 0.272 |
| LogitL2+Meta | +0.24 | +0.24 | +0.06 | +1.1 % | -18.1 % | 1.08 | 37.5 % | 0.038 |
| LogitL2+Overlay | +0.46 | +0.61 | +0.18 | +11.6 % | -44.9 % | 1.09 | 46.8 % | 0.326 |
| LogitL2+Meta+Overlay | +0.22 | +0.21 | +0.05 | +0.7 % | -14.0 % | 1.06 | 33.6 % | 0.037 |

## 4. Deflated Sharpe Ratio (N=5, univers des 5 variantes)

σ²(SR essais) = 7.1916e-05.

| Variante | Sharpe quotidien | seuil SR₀ | z | **DSR** |
|---|---|---|---|---|
| BuyHold | +0.0328 | 0.0101 | +2.21 | **0.987** |
| LogitL2 | +0.0192 | 0.0101 | +0.88 | **0.811** |
| LogitL2+Meta | +0.0152 | 0.0101 | +0.50 | **0.691** |
| LogitL2+Overlay | +0.0292 | 0.0101 | +1.85 | **0.968** |
| LogitL2+Meta+Overlay | +0.0139 | 0.0101 | +0.37 | **0.645** |

## 5. Effet sur le drawdown du signal actif (LogitL2 seul vs pipeline complète)

- LogitL2 seul (variante 2) : MDD **-64.2 %**, rendement annualisé +8.3 %, Sharpe ann. +0.30.
- LogitL2 + meta-labeling + overlay (variante 5) : MDD **-14.0 %**, rendement annualisé +0.7 %, Sharpe ann. +0.22.
- Réduction relative du MDD : **+78.2 %** (seuil de succès déclaré : > 25 %).
- Rendement annualisé conservé : **8.6 %** de la variante 2 (seuil de succès déclaré : ≥ 50 %).

## 6. Verdict honnête

**Critère de succès non atteint** (rendement conservé (8.6 %) sous le seuil de 50 %). Rapporté tel quel, sans le présenter comme un succès.

Meilleur DSR de l'univers : **BuyHold** (0.987). Rappel (cf. `CLAUDE.md`, Étape B/D) : Buy & Hold reste la stratégie de référence sur NDX en Sharpe/DSR brut ; l'objet de cette pipeline n'est pas de la battre en rendement mais de vérifier si la combinaison des trois composantes améliore le **profil risque du signal actif lui-même** — conclusion à lire à la lumière du tableau ci-dessus, pas en absolu.

Discipline anti data-snooping : 5 variantes figées avant évaluation, DSR déflaté sur cette famille (n_trials=5) ; aucun paramètre (secondaire meta, cap/percentile overlay) n'a été retouché après avoir vu ce résultat combiné - ils proviennent de recherches antérieures déjà publiées dans le repo.
