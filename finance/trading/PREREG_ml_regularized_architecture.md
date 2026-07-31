# PRÉ-ENREGISTREMENT — ML-3 : architecture unique bien régularisée (NDX)

Date de rédaction : 31/07/2026. **Committé AVANT tout calcul** (Règle 1 de
`PROTOCOLE_ANTI_SNOOPING.md`, section 2.1 de `ML_STRATEGY_BACKLOG.md`).
Cycle ML-3 du backlog ML relancé. Gabarit identique à
`PREREG_ml_meta_labeling_logitl2_ndx.md` (ML-1) et
`PREREG_ml_exogenous_features_rates_crossmarket.md` (ML-2).

## 1. Hypothèse testée

L'univers figé de l'Étape B contient un modèle non linéaire, `HistGB`
(`HistGradientBoostingClassifier`, `max_depth=3`, `max_iter=150`,
`learning_rate=0.05`, `l2_regularization=1.0`, `min_samples_leaf=40`), qui
sous-performe le modèle linéaire `LogitL2` (Sharpe +0,23 contre +0,30) et reste
loin de Buy & Hold (+0,52) — `results/etape_B_ndx100.md`.

Une explication classique de cet écart est le **sur-apprentissage** : sur des
données financières à rapport signal/bruit très faible, une capacité fixée
*a priori* (ici 150 itérations de boosting, valeur choisie arbitrairement en
Étape B et jamais ajustée) est presque sûrement mauvaise — trop grande dans les
régimes calmes, trop petite dans les régimes riches en structure. Le remède
standard n'est pas de chercher la « bonne » capacité par grille (ce serait du
data-snooping et ferait exploser `n_trials`), mais de laisser un **arrêt
précoce (early stopping) sur une fenêtre de validation purgée** choisir la
capacité, à chaque ré-estimation, **avec les seules données d'entraînement**.

**Hypothèse ML-3** : une architecture non linéaire UNIQUE, dont la capacité est
régularisée par early stopping sur folds purgés au lieu d'être figée
arbitrairement, améliore suffisamment la qualité directionnelle pour franchir le
critère de succès du §6 contre Buy & Hold.

**Hypothèse nulle** : le rapport signal/bruit directionnel quotidien est trop
faible pour qu'une meilleure régularisation de la capacité suffise ; le candidat
peut améliorer `HistGB` sans pour autant battre Buy & Hold.

## 2. Choix de l'architecture — UN SEUL modèle, justifié AVANT calcul

Le backlog (§3, axe ML-3) autorise **soit** un gradient boosting avec early
stopping sur folds purgés, **soit** un MLP à forte régularisation L2/dropout, et
impose d'en choisir **un seul** — tester les deux serait déjà 2 essais.

**Choix retenu : GRADIENT BOOSTING avec early stopping sur folds purgés.**
Justification, arrêtée avant toute exécution :

1. **Implémentabilité exacte du mécanisme demandé.** L'early stopping purgé se
   code de bout en bout et se vérifie ligne à ligne (§3). À l'inverse, le
   « dropout » n'existe pas dans `sklearn.neural_network.MLPClassifier` (seule
   la pénalité L2 `alpha` y est disponible) et `torch` **n'est pas installé**
   dans cet environnement (`ModuleNotFoundError: No module named 'torch'`,
   vérifié le 31/07/2026) : la variante MLP telle que décrite au backlog serait
   livrée amputée de la moitié de sa régularisation.
2. **Interprétabilité du résultat.** Le candidat ne diffère de `HistGB`
   (déjà publié, déjà compté dans l'univers figé de l'Étape B) que par **un seul
   degré de liberté : le nombre d'itérations de boosting**, choisi par early
   stopping purgé au lieu d'être fixé à 150. Le run fournit donc une ablation
   interne propre : tout écart de performance s'attribue à la régularisation de
   capacité, et à rien d'autre. Un MLP changerait simultanément la classe de
   fonctions, l'optimiseur, l'initialisation et la régularisation — un FAIL
   comme un PASS y serait ininterprétable.
3. **Déterminisme.** À `random_state` fixé, le pipeline est reproductible bit à
   bit ; un MLP (initialisation aléatoire + SGD/Adam) introduirait une variance
   d'exécution qui brouillerait la comparaison avec la baseline.

Le MLP n'est **pas** repoussé à un sous-cycle « au cas où » : le tester après
avoir vu le résultat du gradient boosting serait exactement le snooping que la
Règle 1 interdit. **n_trials local pour ce cycle = 1.**

## 3. Définition EXACTE du candidat `HistGB-ES` (FIGÉE — aucune variante)

### 3.1 Hyperparamètres, figés avant tout calcul

Identiques à ceux du `HistGB` de l'Étape B, **sauf** `max_iter` qui devient un
plafond au lieu d'une valeur :

| Hyperparamètre | Valeur | Origine |
|---|---|---|
| `learning_rate` | 0,05 | Étape B, inchangé |
| `max_depth` | 3 | Étape B, inchangé |
| `min_samples_leaf` | 40 | Étape B, inchangé |
| `l2_regularization` | 1,0 | Étape B, inchangé |
| `random_state` | 42 | Étape B, inchangé |
| `max_iter` | **plafond 400**, valeur effective choisie par early stopping | nouveau (Étape B : 150 fixe) |
| standardisation des features | non (invariance d'échelle des arbres) | Étape B, inchangé |

Reprendre les valeurs déjà publiées de l'Étape B est un choix délibéré : elles
n'ont pas été ajustées pour ce cycle, donc **aucun essai caché** ne se dissimule
dans ce tableau. Le plafond 400 n'est pas un hyperparamètre ajusté mais une
borne de calcul : c'est l'early stopping, et non ce plafond, qui détermine la
capacité (un diagnostic vérifiera *a posteriori* que la borne est rarement
atteinte — §5).

### 3.2 Mécanisme d'early stopping purgé (le cœur du cycle)

À **chaque** ré-estimation du walk-forward (tous les 21 jours), sur la fenêtre
d'entraînement `[0, tr − 5)` déjà purgée par `walk_forward_proba` (l'embargo de
5 jours de l'Étape B retire les labels qui chevauchent la période de test) :

1. **Découpe chronologique, jamais aléatoire.** Les `m` lignes d'entraînement
   (ordre chronologique strict) sont coupées en :
   - un bloc de **validation** = les **20 % les plus RÉCENTS** (`n_val = ⌊0,20·m⌋`),
   - un **purge interne de 5 lignes** (= H, l'horizon de la triple barrière)
     immédiatement avant le bloc de validation, **retirées de l'entraînement**,
   - un bloc d'**apprentissage** = tout ce qui précède ce purge.

   La découpe aléatoire par défaut de scikit-learn
   (`early_stopping=True` → `train_test_split` mélangé) est **explicitement
   refusée** : avec des labels triple-barrière qui chevauchent 5 séances, elle
   mettrait dans la validation des événements dont le chemin de prix recoupe
   celui d'événements d'apprentissage — une fuite. `early_stopping` interne de
   scikit-learn est donc désactivé (`early_stopping=False`) et le mécanisme est
   implémenté à la main.

2. **Sélection du nombre d'itérations.** Un modèle est ajusté sur le bloc
   d'apprentissage avec `max_iter=400`, puis la **log-loss** est évaluée sur le
   bloc de validation à chaque stade de boosting via `staged_predict_proba`.
   `k*` = nombre d'itérations minimisant cette log-loss, contraint à
   `k* ∈ [10, 400]`. (Prendre l'argmin sur tous les stades équivaut à un early
   stopping à patience infinie ; aucun paramètre de patience n'est donc à régler,
   ce qui supprime un degré de liberté.)

3. **Modèle déployé.** Un modèle est ré-ajusté sur la fenêtre d'entraînement
   **complète** (apprentissage + purge + validation) avec `max_iter=k*` et les
   mêmes hyperparamètres. C'est lui qui produit `p_up` sur le bloc de test des
   21 jours suivants. Ré-ajuster sur l'ensemble des données d'entraînement à la
   capacité sélectionnée est la pratique standard (analogue au `refit=True` de
   `GridSearchCV`) ; **aucune donnée de test n'intervient à aucun stade**.

4. **Garde-fou dégénéré, figé ici** : si la fenêtre d'entraînement contient
   moins de 300 lignes utilisables (impossible avec T0=750, mais spécifié pour
   que le code n'ait aucun comportement non pré-enregistré), le candidat
   retombe sur `max_iter=150` sans early stopping.

**Ce n'est PAS un grid-search.** Aucun `GridSearchCV`/`RandomizedSearchCV`
n'est utilisé ; aucun hyperparamètre n'est choisi en regardant une métrique de
trading ; la seule quantité sélectionnée (`k*`) l'est sur une log-loss de
validation **interne à la fenêtre d'entraînement**, jamais sur l'OOS. Le
chemin de régularisation d'un boosting fait partie intégrante de l'architecture
(López de Prado, AFML ch. 6 ; Hastie et al., ESL ch. 10), au même titre que le
`C` d'une régression pénalisée. **Une seule définition de candidat est évaluée,
une seule fois : n_trials local = 1.**

## 4. Features — aucune extension (enseignement ML-2)

Le candidat utilise **exactement** les 21 colonnes endogènes de
`build_features(df)` (`exog=None`), c'est-à-dire l'univers de features de
l'Étape B officielle, sans les 5 colonnes exogènes de ML-2.

Motif explicite : ML-2 a montré qu'une feature exogène dont l'historique ne
couvre pas toute la fenêtre OOS met le modèle à plat sur une part importante de
l'échantillon (30,7 %) et ampute mécaniquement son rendement annualisé. Ce
cycle porte sur l'**architecture**, pas sur les features : mélanger les deux
rendrait le verdict ininterprétable. **Contrôle exigé au rapport** : la part de
séances OOS où le candidat est à plat doit être limitée au seul warmup du
walk-forward — toute autre valeur signale un bug, à corriger et relancer avant
tout commit de verdict.

## 5. Aucun sizing probabiliste (enseignement ML-1, déclaré AVANT calcul)

ML-1 a montré qu'un dimensionnement proportionnel à une probabilité mal calibrée
écrase l'exposition (0,10 en moyenne) et détruit le rendement même quand
l'accuracy s'améliore.

**Décision pré-enregistrée : ce cycle n'introduit AUCUN mécanisme de sizing
basé sur une probabilité de modèle.** La position est celle de l'Étape B
officielle (`walk_forward_signals`) :

```
position(t) = +1 si p_up(t) > 0,5 ; −1 si p_up(t) ≤ 0,5 ; 0 si p_up(t) est NaN
```

soit exactement `signe(p_up − 0,5)`, sans rampe, sans seuil de confiance, sans
échelle continue. **Aucune calibration de probabilité n'est donc en jeu**, et
aucune ne pourra être ajoutée après coup : si le résultat déçoit, le verdict est
FAIL, pas un ajustement du sizing. L'effet mesuré est celui de l'architecture
seule, non confondu avec un effet de sizing.

**Diagnostics pré-enregistrés** (informatifs, sans effet sur le verdict) :
distribution de `k*` sur les ré-estimations (min / médiane / max, part des
blocs atteignant le plafond 400), accuracy directionnelle, turnover, exposition,
break-even en bps/trade.

## 6. Protocole (identique à l'Étape B officielle, non modifié)

- Données pilotées : `data/nasdaq100_daily.txt` (NDX, 10273 séances,
  01/10/1985 → 13/07/2026).
- Labels : triple barrier H=5 j, barrières ±1,5·σ (σ = écart-type glissant
  strict sur [t−20, t), implémentation courante de `triple_barrier_labels`).
- Walk-forward expansif : **T0=750**, ré-estimation tous les **21 j**,
  **purge/embargo 5 j** — valeurs de `results/etape_B_ndx100.md`, identiques à
  ML-1 et ML-2. Non modifiées.
- Coûts : **5 bps** aller-retour sur |Δposition| (`backtest()`).
- Fenêtre d'évaluation OOS : indices `[T0, n−1)` = **9522 séances**
  (19/09/1988 → 10/07/2026), strictement identique à l'Étape B, ML-1 et ML-2.
- Signaux calculés dans le même run (comparaison interne + `var_trials` du DSR,
  même convention que ML-1/ML-2) : `BuyHold`, `Momentum`, `LogitL2`, `HistGB`
  (capacité fixe 150, la baseline directe du candidat), **`HistGB-ES`** (le
  candidat). Ces 4 comparses ne sont PAS des essais supplémentaires : c'est
  l'univers figé de l'Étape B, déjà compté.

## 7. Critère de succès chiffré (FIGÉ)

Sur la fenêtre OOS NDX complète du §6, net de 5 bps, `HistGB-ES` doit satisfaire
**au moins une** des deux conditions (critère niveau 1 du §2.4 de
`ML_STRATEGY_BACKLOG.md`) :

- **(A)** Sharpe annualisé > Sharpe annualisé Buy & Hold **ET** rendement
  annualisé > rendement annualisé Buy & Hold ; **OU**
- **(B)** Calmar > Calmar Buy & Hold.

Repères Buy & Hold à battre (recalculés dans le script, valeurs de référence
`etape_B_ndx100.md`) : Sharpe **+0,52** · rendement **+14,5 %/an** ·
Calmar **+0,08**.

Tout autre résultat = **FAIL**, rapporté tel quel. Une amélioration par rapport
au `HistGB` à capacité fixe qui ne franchirait pas Buy & Hold n'est **pas** un
PASS — c'est précisément l'erreur de lecture que ML-1 et ML-2 ont évitée.

## 8. Règle 10 — fraction hors-marché

Le candidat détient du capital hors-marché uniquement les jours où il ne parie
pas, c'est-à-dire le **warmup** du walk-forward (aucun modèle encore entraîné).
**Hypothèse déclarée : rémunération 0 % (cash nu).** Justification : (i) la
référence Étape B (`LogitL2`/`HistGB` ±1, `BuyHold` 1,0×) est calculée sans taux
sans risque, la comparaison reste homogène ; (ii) 0 % est l'hypothèse
**conservatrice** pour l'hypothèse testée. Le candidat est ±1 hors warmup : il
n'y a pas de mécanisme défensif détenant durablement du cash ici.

## 9. Si PASS niveau 1 — batterie de validation renforcée (§2.4 du backlog ML)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ (seule condition
autorisant une notification Telegram) :

a. Stress de coûts ×3 et ×5 (15 bps, 25 bps) — critère du §7 maintenu.
b. Stress de crise (2000-2002, 2007-2009, 02-04/2020, 2022) : MDD du candidat
   pas pire que celui de Buy & Hold sur la fenêtre.
c. Stabilité temporelle : 4 folds non chevauchants + embargo 5 j ; le candidat
   doit battre Buy & Hold sur une **majorité** de folds.
d. SPA de Hansen à 1 candidat contre Buy & Hold (`spa_test`,
   `finance/src/volatility.py`), seuil p < 0,05.
e. DSR avec **n_trials = 407** = 400 (itérations brute-force ML 1-10 closes)
   + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ML-2) + 1 (ce cycle ML-3).
   Jamais 1. `var_trials` = variance (ddof=1) des Sharpe **quotidiens** des
   5 signaux du §6, même convention d'échelle que `run_etape_b.py`, ML-1 et
   ML-2. Seuil DSR > 0,95.

## 10. Lecture secondaire déclarée (sans effet sur le verdict)

Le même calcul sera exécuté sur `data/nasdaq_composite_daily.txt` et rapporté à
titre informatif. Le Composite n'est PAS un marché indépendant du NDX
(Règle 3) : il ne peut ni valider ni invalider le verdict.

## 11. Engagement

Aucune modification de l'architecture (1 modèle, hyperparamètres du §3.1,
mécanisme d'early stopping du §3.2), des features (§4), de la règle de position
(§5), du protocole walk-forward (§6), de la fenêtre de verdict ou du critère
(§7) après avoir vu le moindre résultat. En particulier : **aucun basculement
vers la variante MLP**, quel que soit le résultat du gradient boosting. Tout bug
détecté est corrigé ET les calculs affectés relancés avant tout commit de
verdict.
