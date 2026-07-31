# PRÉ-ENREGISTREMENT — ML-2 : features exogènes taux / cross-marché (LogitL2, NDX)

Date de rédaction : 31/07/2026. **Committé AVANT tout calcul** (Règle 1 de
`PROTOCOLE_ANTI_SNOOPING.md`, section 2.1 de `ML_STRATEGY_BACKLOG.md`).
Cycle ML-2 du backlog ML relancé. Gabarit identique à
`PREREG_ml_meta_labeling_logitl2_ndx.md` (cycle ML-1).

## 1. Hypothèse testée

L'univers de features de l'Étape B (`build_features`, `finance/src/prediction.py`)
est **strictement endogène** : tout y est dérivé de l'OHLC de l'indice lui-même
(rendements retardés, momentum, volatilité, RSI/MACD/Bollinger/ATR/Stochastic,
différenciation fractionnaire). Le signal LogitL2 qui en résulte est rentable net
de coûts sur NDX (Sharpe +0,30, accuracy 53,67 %) mais reste sous Buy & Hold en
base déflatée (DSR 0,372 vs 0,842, `results/etape_B_ndx100.md`).

Hypothèse : une part de la structure directionnelle des actions est portée par
des variables **exogènes** — le niveau et la pente de la courbe des taux US
(régime monétaire, coût d'actualisation) et le momentum d'un marché actions
étranger clôturant avant la séance américaine (spillover DAX→NDX, déjà exploré
côté non-ML aux cycles #110/#140/#148-160). Ajouter ces variables aux features
du LogitL2, **sans rien changer d'autre**, devrait améliorer sa qualité
directionnelle et le rapprocher — voire le faire passer au-dessus — de
Buy & Hold.

Hypothèse nulle : l'information taux/cross-marché est déjà incorporée dans les
prix (efficience semi-forte) ; le LogitL2 enrichi ne bat pas Buy & Hold sur le
critère chiffré du §6.

## 2. Définition EXACTE des features ajoutées (FIGÉE — aucune variante)

Le modèle est **inchangé** : `LogisticRegression(C=0.5, max_iter=1000)`,
standardisation calée sur la fenêtre d'entraînement uniquement, labels
triple-barrier. **Seule la matrice de features change** : les 21 colonnes
actuelles de `build_features(df)` + **exactement 5 colonnes exogènes**, listées
ci-dessous et jamais modifiées après le premier résultat.

Sources (toutes déjà en local, aucun téléchargement) :
`data/dgs10_daily.csv` (FRED DGS10, taux 10 ans US, 1962→2026),
`data/dgs3mo_daily.csv` (FRED DGS3MO, taux 3 mois US, 1981→2026),
`data/dax_daily.txt` (DAX, OHLC quotidien, 01/11/1999→2026).

### 2.1 Règle d'alignement temporel causal (UNIQUE, appliquée aux 3 sources)

Pour une date de séance NDX `t`, et pour chaque série exogène `S` :

- `τ₁(t)` = **dernière date d'observation de `S` strictement antérieure à `t`**
  (`obs_date < t`, comparaison stricte) ;
- `τ₂(t)` = l'observation immédiatement précédente de `S` (avant-dernière
  strictement antérieure à `t`).

Aucun `ffill` d'une observation future, aucune interpolation, aucune
utilisation de l'observation du jour `t` lui-même. Si `τ₁` ou `τ₂` n'existe pas
(début d'historique de la série exogène), la feature vaut **NaN** — et
`walk_forward_proba` refuse alors la ligne (train comme test), ce qui met la
stratégie **à plat** (position 0). C'est la conséquence acceptée du §5.

Justification du décalage strict `< t`, reprise telle quelle des cycles non-ML
`PREREG_dax_ndx_spillover_overlay.md` (#110) et suivants : le Xetra (DAX) ouvre
~09:00 CET et **clôture ~17:30 CET, soit APRÈS l'ouverture du Nasdaq**
(09:30 ET = ~15:30 CET). La clôture DAX du jour `t` tombe donc PENDANT la
séance NDX du jour `t` : l'utiliser pour prédire le jour `t` serait une fuite
partielle (bug effectivement rencontré et corrigé au cycle #110). Le rendement
DAX du **jour de bourse précédent** est en revanche connu sans ambiguïté de
fuseau horaire. Le même raisonnement, en plus conservateur encore, s'applique
aux séries FRED (publiées en fin de journée, après clôture US) : on n'utilise
que l'observation de la veille ou antérieure.

### 2.2 Les 5 features (FIGÉES)

| Colonne | Formule | Unité |
|---|---|---|
| `exog_dgs10_level` | `DGS10(τ₁)` | % |
| `exog_slope_10y_3mo` | `DGS10(τ₁) − DGS3MO(τ₁)` (pente de courbe) | % |
| `exog_dgs10_chg` | `DGS10(τ₁) − DGS10(τ₂)` (variation quotidienne) | points de % |
| `exog_dgs3mo_chg` | `DGS3MO(τ₁) − DGS3MO(τ₂)` (variation quotidienne) | points de % |
| `exog_dax_ret_lag1` | `log(close_DAX(τ₁) / close_DAX(τ₂))` (spillover décalé d'une séance) | log-rendement |

`τ₁`/`τ₂` sont calculés **indépendamment pour chaque série** (chaque série a son
propre calendrier de publication et ses propres jours fériés). Les valeurs
non numériques des CSV FRED (`.` pour les jours fériés) sont supprimées au
chargement, avant tout calcul de `τ`.

**Aucune autre transformation** : pas de z-score exogène, pas de moyenne
mobile de taux, pas de niveau 3 mois seul, pas d'autres marchés (S&P 500,
Russell 2000 sont réservés au cycle ML-4), pas de VIX (`vixcls_daily.csv`
existe mais n'est PAS utilisé ici), pas de `t10y2y_daily.csv` (la pente est
recalculée à la main pour contrôler l'alignement). **n_trials local pour ce
cycle = 1** : un seul jeu de features, un seul modèle, une seule exécution
qui compte.

### 2.3 Implémentation

`build_features(df, exog=None)` reçoit un paramètre **optionnel** ; comportement
strictement inchangé (mêmes 21 colonnes, mêmes valeurs) quand `exog` n'est pas
fourni, afin de ne casser aucun script existant (Étape B, D, ML-1…). Les
features exogènes sont produites par une fonction dédiée
`build_exogenous_features(dates, ...)` de `finance/src/prediction.py`.

## 3. Aucun sizing probabiliste (enseignement ML-1, déclaré AVANT calcul)

Le cycle ML-1 a montré qu'un dimensionnement proportionnel à une probabilité
mal calibrée écrase l'exposition (0,10 en moyenne) et détruit le rendement même
quand l'accuracy s'améliore.

**Décision pré-enregistrée : ce cycle n'introduit AUCUN mécanisme de sizing
basé sur une probabilité de modèle.** La position est celle de l'Étape B
officielle, `walk_forward_signals` :

```
position(t) = +1 si p_up(t) > 0.5 ; −1 si p_up(t) ≤ 0.5 ; 0 si p_up(t) est NaN
```

soit exactement `signe(p_up − 0,5)`, sans rampe, sans seuil de confiance, sans
échelle continue. Aucune calibration de probabilité n'est donc nécessaire, et
aucune ne pourra être ajoutée après coup : si le résultat déçoit, le verdict est
FAIL, pas un ajustement du sizing (ce serait exactement le snooping que la
Règle 1 interdit).

## 4. Protocole (identique à l'Étape B officielle, non modifié)

- Données pilotées : `data/nasdaq100_daily.txt` (NDX, 10273 séances,
  01/10/1985 → 13/07/2026).
- Labels : triple barrier H=5 j, barrières ±1,5·σ (σ = écart-type glissant strict
  sur [t−20, t), implémentation courante de `triple_barrier_labels`).
- Walk-forward expansif : **T0=750**, ré-estimation tous les **21 j**,
  **purge/embargo 5 j** — valeurs de la référence canonique
  `results/etape_B_ndx100.md`, identiques à celles du cycle ML-1. Non modifiées.
- Coûts : **5 bps** aller-retour sur |Δposition| (`backtest()`).
- Fenêtre d'évaluation OOS : indices `[T0, n−1)` = **9522 séances**
  (19/09/1988 → 10/07/2026), strictement identique à l'Étape B officielle et à
  ML-1.
- Signaux calculés dans le même run (pour la comparaison interne et pour
  `var_trials` du DSR, même convention que ML-1) : `BuyHold`, `Momentum`,
  `LogitL2` (baseline nue, features endogènes seules), `HistGB`,
  **`LogitL2Exog`** (le candidat). Ces 4 comparses ne sont PAS des essais
  supplémentaires : ce sont l'univers figé de l'Étape B, déjà compté.

## 5. Conséquence assumée de la disponibilité des données exogènes

Le DAX ne commence qu'au **01/11/1999**. Le candidat ne peut donc pas parier
avant ~2000 (ni s'entraîner : `walk_forward_proba` exige toutes les features
finies en train comme en test) et reste **à plat, position 0**, sur environ le
premier tiers de la fenêtre OOS.

**Décision prise ici, avant tout calcul** : la fenêtre de verdict reste la
fenêtre OOS complète de l'Étape B, sans raccourci — exactement le choix fait au
cycle ML-1 pour le warmup du méta-modèle ("pénalité acceptée telle quelle pour
garder la fenêtre de comparaison strictement identique"). C'est le choix
**conservateur** : il pénalise lourdement le candidat en rendement annualisé.

Deux garde-fous d'interprétation, également pré-enregistrés :

- **Lecture secondaire déclarée (aucun effet sur le verdict)** : les mêmes
  métriques seront rapportées sur la **fenêtre restreinte** commençant à la
  première séance où les 5 features exogènes sont finies ET où le candidat a un
  modèle entraîné, avec **Buy & Hold recalculé sur exactement la même
  fenêtre**. Cette lecture répond à la question scientifique « les features
  exogènes aident-elles ? » ; elle ne peut ni créer ni annuler un PASS.
- **Alerte anti-artefact** : si le critère est atteint uniquement par la
  branche (B) Calmar, le rapport devra explicitement examiner si le gain vient
  du fait que le candidat est **à plat pendant le krach dot-com** (donc d'un
  trou de données, pas d'un edge). Cet examen est obligatoire et pré-enregistré ;
  il ne modifie pas le verdict niveau 1 mais devra figurer dans le rapport, et
  la batterie renforcée (§7, contrôles b et c) tranchera.

## 6. Critère de succès chiffré (FIGÉ)

Sur la fenêtre OOS NDX complète du §4, net de 5 bps, `LogitL2Exog` doit
satisfaire **au moins une** des deux conditions (critère niveau 1 du §2.4 de
`ML_STRATEGY_BACKLOG.md`) :

- **(A)** Sharpe annualisé > Sharpe annualisé Buy & Hold **ET** rendement
  annualisé > rendement annualisé Buy & Hold ; **OU**
- **(B)** Calmar > Calmar Buy & Hold.

Repères Buy & Hold à battre (recalculés dans le script, valeurs de référence
`etape_B_ndx100.md`) : Sharpe **+0,52** · rendement **+14,5 %/an** ·
Calmar **+0,08**.

Tout autre résultat = **FAIL**, rapporté tel quel. Une amélioration par rapport
au LogitL2 nu qui ne franchirait pas Buy & Hold n'est **pas** un PASS.

## 7. Règle 10 — fraction hors-marché

Le candidat détient du capital hors-marché les jours où il ne parie pas
(position 0 : warmup walk-forward et absence de features exogènes avant 2000).
**Hypothèse déclarée : rémunération 0 % (cash nu).** Justification : (i) la
référence Étape B (LogitL2 ±1, BuyHold 1,0×) est calculée sans taux sans
risque, la comparaison reste donc homogène ; (ii) 0 % est l'hypothèse
**conservatrice** pour l'hypothèse testée — un portage ne pourrait que gonfler
artificiellement le candidat sur la longue période où il est à plat.
Remarque de cohérence : les taux servent ici de **features prédictives**,
jamais de rendement de portage — aucune confusion possible avec le cycle #142
du backlog non-ML.

## 8. Si PASS niveau 1 — batterie de validation renforcée (§2.4 du backlog ML)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ (seule condition
autorisant une notification Telegram) :

a. Stress de coûts ×3 et ×5 (15 bps, 25 bps) — critère du §6 maintenu.
b. Stress de crise (2000-2002, 2007-2009, 02-04/2020, 2022) : MDD du candidat
   pas pire que celui de Buy & Hold sur la fenêtre.
c. Stabilité temporelle : 4 folds non chevauchants + embargo 5 j ; le candidat
   doit battre Buy & Hold sur une **majorité** de folds.
d. SPA de Hansen à 1 candidat contre Buy & Hold (`spa_test`,
   `finance/src/volatility.py`), seuil p < 0,05.
e. DSR avec **n_trials = 406** = 400 (itérations brute-force ML 1-10 closes)
   + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ce cycle ML-2). Jamais 1.
   `var_trials` = variance (ddof=1) des Sharpe **quotidiens** des 5 signaux du
   §4, même convention d'échelle que `run_etape_b.py` et que ML-1.
   Seuil DSR > 0,95.

## 9. Lecture secondaire déclarée (sans effet sur le verdict)

Le même calcul sera exécuté sur `data/nasdaq_composite_daily.txt` et rapporté à
titre informatif. Le Composite n'est PAS un marché indépendant du NDX
(Règle 3) : il ne peut ni valider ni invalider le verdict.

## 10. Engagement

Aucune modification de l'univers (5 features exogènes, 1 modèle, 1 règle de
position), du protocole walk-forward, de la fenêtre de verdict ou du critère
après avoir vu le moindre résultat. Tout bug détecté est corrigé ET les calculs
affectés relancés avant tout commit de verdict.
