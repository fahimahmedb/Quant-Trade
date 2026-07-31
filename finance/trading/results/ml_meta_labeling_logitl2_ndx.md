# ML-1 — Meta-labeling sur LogitL2 (nasdaq100_daily)

PREREG : `PREREG_ml_meta_labeling_logitl2_ndx.md` (committé avant calcul). Script : `scripts/ml_meta_labeling_logitl2_ndx_backtest.py`.

## 1. Mécanisme (figé au PREREG, n_trials local = 1)

- **Primaire inchangé** : LogitL2 de l'Étape B (LogisticRegression C=0.5), features causales `build_features`, labels triple barrier H=5 / ±1,5σ (ewm 20 j).
- **Secondaire** : LogisticRegression C=0.5 sur les mêmes features + `primary_conf`=|p_up−0,5|×2 + `primary_p_up`. Cible binaire : le pari primaire coïncide-t-il avec le signe du label triple barrier ?
- **Position finale** = signe(p_up−0,5) × clip(2·(p_win−0,5), 0, 1) — filtre à seuil (p_win ≤ 0,5 → mise nulle) ET dimensionnement continu borné [0,1].
- Walk-forward T0=750, refit 21 j, **purge/embargo 5 j appliqué aussi au secondaire**, coûts 5 bps aller-retour sur |Δposition| (les Δ fractionnaires sont facturés au même tarif).
- Fraction hors-marché rémunérée à **0 % (cash nu)** — hypothèse déclarée au PREREG §4 (Règle 10), conservatrice pour l'hypothèse testée.
- OOS = 9522 séances (19/09/1988 → 10/07/2026), fenêtre strictement identique à l'Étape B officielle.

## 2. Avant / après meta-labeling (net de coûts)

| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Turnover moy./j | Exposition moy. |
|---|---|---|---|---|---|---|---|---|
| BuyHold | +0.52 | +0.69 | +0.08 | +14.5 % | -82.9 % | 1.10 | 0.000 | 1.00 |
| Momentum | -0.28 | -0.38 | -0.02 | -7.1 % | -97.6 % | 0.95 | 0.275 | 1.00 |
| LogitL2 | +0.35 | +0.45 | +0.10 | +9.5 % | -59.6 % | 1.07 | 0.268 | 1.00 |
| HistGB | +0.46 | +0.63 | +0.11 | +12.6 % | -66.9 % | 1.09 | 0.376 | 1.00 |
| Meta | +0.28 | +0.28 | +0.06 | +1.4 % | -19.2 % | 1.10 | 0.039 | 0.10 |

*`Meta` = LogitL2 filtré/dimensionné par le méta-modèle. `LogitL2` = le même signal primaire nu (référence avant meta-labeling).*

## 3. Accuracy directionnelle et coût de rupture

| Signal | Accuracy (jours où la stratégie parie) | Break-even (bps/trade) |
|---|---|---|
| Momentum | 51.21 % | -5.60 |
| LogitL2 | 54.20 % | +18.42 |
| HistGB | 53.44 % | +17.56 |
| Meta | 55.81 % | +18.73 |

## 4. Deflated Sharpe Ratio

σ²(SR quotidiens des 5 signaux) = 4.0582e-04. Deux lectures :

| Signal | Sharpe quot. | DSR (n_trials=405, campagne ML entière) | DSR (n_trials=4, échelle Étape B) |
|---|---|---|---|
| BuyHold | +0.0328 | **0.004** | 0.871 |
| Momentum | -0.0178 | **0.000** | 0.000 |
| LogitL2 | +0.0219 | **0.000** | 0.529 |
| HistGB | +0.0288 | **0.001** | 0.772 |
| Meta | +0.0175 | **0.000** | 0.358 |

*La colonne de gauche est celle qui compte : n_trials=405 = 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ce cycle). Jamais réduit à 1 (Règle 2). La colonne de droite n'est là que pour comparer aux chiffres publiés de `etape_B_ndx100.md`.*

## 5. Verdict (critère chiffré du PREREG §5)

- **(A)** Sharpe Meta (+0.28) > Sharpe BuyHold (+0.52) **ET** rendement Meta (+1.4 %) > rendement BuyHold (+14.5 %) → **NON satisfait**.
- **(B)** Calmar Meta (+0.06) > Calmar BuyHold (+0.08) → **NON satisfait**.

### FAIL

Effet du meta-labeling sur le signal primaire : Sharpe +0.35 → +0.28 (-0.07), turnover 0.268 → 0.039 (-0.229/j), MDD -59.6 % → -19.2 %, exposition moyenne 1.00 → 0.10.

Le critère pré-enregistré n'est pas atteint : le meta-labeling **ne suffit pas** à faire passer LogitL2 au-dessus de Buy & Hold. La batterie de validation renforcée n'est pas déclenchée (elle ne s'applique qu'à un PASS niveau 1). Résultat rapporté tel quel, sans ajustement du mécanisme ni du critère a posteriori (Règle 1).

## 6. Notes de traçabilité (Règle 6)

- **Baseline recalculée, pas recopiée.** Le LogitL2 mesuré ici (+0.35 de Sharpe) diffère du chiffre publié dans `results/etape_B_ndx100.md` (+0,30) : `triple_barrier_labels` a été modifié depuis (σ locale = écart-type glissant strict sur [t−20, t) au lieu d'un ewm expansif ; les deux versions sont causales, mais les labels diffèrent, cf. `results/etape_B_phase1_fixed.md`). Les 5 lignes du tableau §2 proviennent **du même run, du même code et des mêmes labels** : la comparaison avant/après est donc interne et cohérente, ce qui est ce dont dépend le verdict.
- **Sharpe invariant d'échelle.** L'exposition moyenne du candidat (0.10) est faible, mais appliquer un levier uniforme ne changerait ni le Sharpe (invariant d'échelle, hors coûts) ni le Calmar (rendement et drawdown se multiplient par le même facteur) : le verdict du §5 ne dépend pas du niveau de levier retenu. Aucune variante avec levier n'a donc été évaluée (cela aurait ajouté un essai sans changer la conclusion).
- **σ²(SR essais)** utilisée par les deux colonnes DSR du §4 est calculée sur les 5 signaux de ce run (BuyHold, Momentum, LogitL2, HistGB, Meta) ; la colonne « échelle Étape B » n'est donc pas strictement identique au tableau publié (qui l'estimait sur 4 signaux) — elle sert d'ordre de grandeur, pas de verdict.
- Fichier de positions sauvegardé pour audit : `results/ml_meta_labeling_logitl2_ndx_pnl.npz` (positions OOS, rendements, dates, coût, σ², n_trials).

## 7. Diagnostic du méta-modèle et lecture secondaire (ajoutés après le run)

*Section ajoutée après l'exécution, à partir du fichier de positions
`results/ml_meta_labeling_logitl2_ndx_pnl.npz` produit par le run ci-dessus
(aucun re-calcul du verdict, aucune modification du mécanisme).*

**Le méta-modèle n'est pas dégénéré, il est mal calibré.** Distribution de la
taille de pari implicite sur les 9522 séances OOS :

| Statistique | Valeur |
|---|---|
| Séances à mise nulle (p_win ≤ 0,5 ou warmup du secondaire) | 2606 (27,4 %) |
| p_win médian quand la mise est non nulle | 0,562 |
| p_win max | 0,982 |
| Taille moyenne quand non nulle | 0,135 |
| Séances à taille ≥ 0,5 (p_win ≥ 0,75) | 81 |

Le méta-modèle **apporte bien de l'information** : l'accuracy directionnelle
monte de 54,20 % (LogitL2 nu) à 55,81 % sur les jours où il laisse parier, et
le break-even passe de 18,4 à 18,7 bps/trade. Mais ses probabilités restent
serrées autour de 0,5, donc la rampe linéaire pré-enregistrée
`clip(2·(p_win−0,5), 0, 1)` produit une exposition moyenne de 0,10 : le
rendement absolu s'effondre (+9,5 % → +1,4 %/an) alors que le Sharpe ne
s'améliore pas (+0,35 → +0,28, les coûts fixes pesant relativement plus sur
une petite mise). C'est un **échec de la thèse**, pas un artefact de calcul :
réduire le turnover (0,268 → 0,039/j) et le MDD (−59,6 % → −19,2 %) ne suffit
pas à rapprocher le Sharpe de Buy & Hold.

**Lecture secondaire déclarée (PREREG §7)** — mêmes calculs sur le NASDAQ
Composite : `results/ml_meta_labeling_logitl2_composite.md`. Verdict également
**FAIL** (Meta Sharpe −0,54 vs BuyHold +0,78 ; le primaire LogitL2 y est de
toute façon négatif, −0,68). Le Composite n'étant pas un marché indépendant du
NDX (Règle 3), cette lecture ne pèse pas sur le verdict.
