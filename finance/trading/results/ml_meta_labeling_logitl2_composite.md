# ML-1 — Meta-labeling sur LogitL2 (nasdaq_composite_daily)

PREREG : `PREREG_ml_meta_labeling_logitl2_ndx.md` (committé avant calcul). Script : `scripts/ml_meta_labeling_logitl2_ndx_backtest.py`.

## 1. Mécanisme (figé au PREREG, n_trials local = 1)

- **Primaire inchangé** : LogitL2 de l'Étape B (LogisticRegression C=0.5), features causales `build_features`, labels triple barrier H=5 / ±1,5σ (ewm 20 j).
- **Secondaire** : LogisticRegression C=0.5 sur les mêmes features + `primary_conf`=|p_up−0,5|×2 + `primary_p_up`. Cible binaire : le pari primaire coïncide-t-il avec le signe du label triple barrier ?
- **Position finale** = signe(p_up−0,5) × clip(2·(p_win−0,5), 0, 1) — filtre à seuil (p_win ≤ 0,5 → mise nulle) ET dimensionnement continu borné [0,1].
- Walk-forward T0=750, refit 21 j, **purge/embargo 5 j appliqué aussi au secondaire**, coûts 5 bps aller-retour sur |Δposition| (les Δ fractionnaires sont facturés au même tarif).
- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au PREREG §4 (Règle 10), conservatrice pour l'hypothèse testée.
- OOS = 500 séances (10/07/2024 → 09/07/2026), fenêtre strictement identique à l'Étape B officielle.

## 2. Avant / après meta-labeling (net de coûts)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.78 | +1.03 | +0.62 | +18.9 % | -24.3 % | 1.15 | 0.000 | 1.00 |
| Momentum | -0.33 | -0.43 | -0.19 | -7.1 % | -32.8 % | 0.94 | 0.304 | 1.00 |
| LogitL2 | -0.68 | -0.99 | -0.26 | -14.0 % | -43.8 % | 0.88 | 0.276 | 1.00 |
| HistGB | +0.03 | +0.05 | +0.02 | +0.7 % | -28.6 % | 1.01 | 0.528 | 1.00 |
| Meta | -0.54 | -0.59 | -0.37 | -6.4 % | -16.2 % | 0.80 | 0.112 | 0.18 |

*`Meta` = LogitL2 filtré/dimensionné par le méta-modèle. `LogitL2` = le même signal primaire nu (référence avant meta-labeling).*

## 3. Accuracy directionnelle et coût de rupture

| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|
| Momentum | 53.80 % | -4.66 |
| LogitL2 | 52.00 % | -16.57 |
| HistGB | 49.80 % | +5.56 |
| Meta | 49.01 % | -18.33 |

## 4. Deflated Sharpe Ratio

σ²(SR quotidiens des 5 signaux) = 1.3538e-03. Deux lectures :

| Signal | Sharpe quot. | DSR (n_trials=405, campagne ML entière) | DSR (n_trials=4, échelle Étape B) |
|---|---|---|---|
| BuyHold | +0.0493 | **0.086** | 0.594 |
| Momentum | -0.0210 | **0.002** | 0.089 |
| LogitL2 | -0.0427 | **0.000** | 0.037 |
| HistGB | +0.0021 | **0.008** | 0.206 |
| Meta | -0.0337 | **0.002** | 0.071 |

*La colonne de gauche est celle qui compte : n_trials=405 = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite n'est là que pour comparer aux chiffres publiés de `etape_B_ndx100.md`.*

## 5. Verdict (critère chiffré du PREREG §5)

- **(A)** Sharpe Meta (-0.54) > Sharpe BuyHold (+0.78) **ET** rendement Meta (-6.4 %) > rendement BuyHold (+18.9 %) → **NON satisfait**.
- **(B)** Calmar Meta (-0.37) > Calmar BuyHold (+0.62) → **NON satisfait**.

### FAIL

Effet du meta-labeling sur le signal primaire : Sharpe -0.68 → -0.54 (+0.14), turnover 0.276 → 0.112 (-0.164/j), MDD -43.8 % → -16.2 %, exposition moyenne 1.00 → 0.18.

Le critère pré-enregistré n'est pas atteint : le meta-labeling **ne suffit pas** à faire passer LogitL2 au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans ajustement du mécanisme ni du critère a posteriori (Règle 1).

## 6. Notes de traçabilité (Règle 6)

- **Baseline recalculée, pas recopiée.** Le LogitL2 mesuré ici (-0.68 de Sharpe) diffère du chiffre publié dans `results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t) au lieu d'un ewm expansif ; les deux versions sont causales, mais les labels diffèrent, cf. `results/etape_B_phase1_fixed.md`). Les 5 lignes du tableau §2 proviennent **du même run, du même code et des mêmes labels** : la comparaison avant/après est donc interne et cohérente, ce qui est ce dont dépend le verdict.
- **Sharpe invariant d'échelle.** L'exposition moyenne du candidat (0.18) est faible, mais appliquer un levier uniforme ne changerait ni le Sharpe (invariant d'échelle, hors coûts) ni le Calmar (rendement et drawdown se multiplient par le même facteur) : le verdict du §5 ne dépend pas du niveau de levier retenu. Aucune variante avec levier n'a donc été évaluée (cela aurait ajouté un essai sans changer la conclusion).
- **σ²(SR essais)** utilisée par les deux colonnes DSR du §4 est calculée sur les 5 signaux de ce run (BuyHold, Momentum, LogitL2, HistGB, Meta) ; la colonne « échelle Étape B » n'est donc pas strictement identique au tableau publié (qui l'estimait sur 4 signaux) — elle sert d'ordre de grandeur, pas de verdict.
- Fichier de positions sauvegardé pour audit : `results/ml_meta_labeling_logitl2_composite_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).
