# PRÉ-ENREGISTREMENT — ML-4 : Cross-market pooling (entraînement conjoint 3 marchés)

**Date de rédaction : 31/07/2026. Committé AVANT tout calcul** (Règle 1 du
`PROTOCOLE_ANTI_SNOOPING.md`, §2.1 de `ML_STRATEGY_BACKLOG.md`).

Cycle **ML-4** du backlog ML relancé — **dernier axe fixé a priori** de la
section 3 de `ML_STRATEGY_BACKLOG.md`. Définition de l'axe reprise **mot pour
mot** du backlog, non modifiée :

> **ML-4 — Cross-market pooling.** Entraînement conjoint sur plusieurs marchés
> indépendants au sens de la Règle 3 (Russell 2000, S&P 500, DAX) pour
> augmenter la taille effective de l'échantillon d'apprentissage.

---

## 1. Hypothèse testée

Le modèle directionnel officiel de l'Étape B (`LogitL2`) est estimé, à chaque
ré-estimation walk-forward, sur l'historique d'**un seul** marché. Sur NDX cela
représente ~1 000 à 9 500 lignes selon la date. Hypothèse : l'edge directionnel
recherché est **partiellement commun aux marchés actions** (mêmes régimes de
volatilité, mêmes effets de momentum/retour à la moyenne à court terme), de
sorte qu'estimer les coefficients du logit sur un échantillon **poolé** de 3
marchés génétiquement indépendants réduit la variance d'estimation et améliore
la performance out-of-sample **de chaque marché pris séparément**.

Le pooling ne sert qu'à **l'entraînement**. L'évaluation walk-forward reste
**strictement séparée par marché** : aucune métrique de test n'est mélangée
entre marchés, aucune moyenne inter-marchés n'entre dans le verdict.

Hypothèse nulle implicite : le pooling n'apporte rien (ou nuit, si les
dynamiques sont trop hétérogènes et que les coefficients communs sont un
mauvais compromis), et le candidat ne franchit pas Buy & Hold sur son marché.

## 2. Enseignements des cycles précédents, explicitement intégrés

Conformément à la demande de report des enseignements ML-1/ML-2/ML-3
(§4 de `ML_STRATEGY_BACKLOG.md`) :

- **ML-1 (sizing)** — un dimensionnement proportionnel à une probabilité mal
  calibrée détruit l'exposition (exposition moyenne 0,10, rendement écrasé).
  → **Ce cycle n'utilise AUCUN sizing probabiliste.** La position est le signal
  directionnel simple `signe(p_up − 0,5) ∈ {−1, +1}`, identique à la baseline
  `LogitL2` de l'Étape B, 0 uniquement pendant le warmup walk-forward. Aucune
  calibration n'est en jeu ; l'effet mesuré est celui du pooling **seul**.
- **ML-2 (couverture historique)** — une feature à historique court met le
  candidat « à plat » sur une part de l'OOS (30,7 % pour le DAX pré-1999) et
  ampute mécaniquement son rendement annualisé.
  → **Contrôle de couverture pré-enregistré, à vérifier AVANT calcul du
  verdict** : chaque marché est évalué sur SA PROPRE fenêtre de test, définie
  par SON PROPRE historique (OOS = indices `[T0, n_marché − 1)`), donc couverte
  à 100 % par construction. Le contrôle opérationnel exigé est : **part des
  séances OOS à position 0 = 0,00 % hors warmup initial, pour CHACUN des 3
  marchés**. Toute valeur non nulle hors warmup est déclarée ici comme un
  **bug** à corriger et relancer avant tout commit de résultat, pas comme une
  caractéristique du candidat. Le caractère borné de l'historique DAX
  (01/11/1999) n'affecte QUE la composition du pool d'entraînement des autres
  marchés aux dates anciennes (§3.4), jamais la fenêtre de test d'un marché.
- **ML-3 (précision ≠ performance)** — un modèle contraint à ±1 ne peut
  qu'approcher asymptotiquement un Buy & Hold bruité ; l'accuracy, le turnover
  et le break-even se sont améliorés sur trois cycles consécutifs sans jamais
  franchir Buy & Hold.
  → **L'accuracy, le turnover et le break-even sont rapportés comme
  DIAGNOSTICS uniquement.** Ils n'entrent dans AUCUNE branche du critère de
  succès du §6. Une amélioration d'accuracy sans franchissement du critère
  chiffré est un **FAIL**, et sera rapportée comme tel.
- **Règle 3 du protocole** — Composite et NDX-100 ne comptent pas comme marchés
  indépendants. Les 3 marchés de ce cycle sont **Russell 2000, S&P 500, DAX**,
  les seuls reconnus indépendants pour ce projet. **Aucune lecture secondaire
  NDX/Composite n'est prévue ni autorisée dans ce cycle** (ce serait ajouter des
  essais après coup ; par ailleurs elle n'apporterait rien puisque les 3 marchés
  du verdict sont déjà indépendants entre eux).

## 3. Définition EXACTE du candidat (figée, n_trials local = 1)

### 3.1 Modèle

`LogitL2Pooled` = `sklearn.linear_model.LogisticRegression(C=0.5,
max_iter=1000)` — **exactement** les hyperparamètres du `LogitL2` de l'Étape B
officielle (`finance/trading/scripts/run_etape_b.py`, ligne 68), repris tels
quels. **Aucun** hyperparamètre n'est réglé dans ce cycle, **aucun**
grid-search, **aucune** variante. La SEULE chose qui change par rapport à la
baseline est **la composition de l'échantillon d'entraînement**.

### 3.2 Features et labels (inchangés)

- Features : `build_features(df)` avec `exog=None` — les 21 colonnes endogènes
  de l'Étape B, calculées **indépendamment sur chaque marché** à partir de ses
  propres OHLC. Aucune feature exogène (enseignement ML-2), aucune feature
  cross-marché (ce cycle teste le pooling d'échantillons, pas l'ajout
  d'information contemporaine d'un marché dans un autre — cela a déjà été testé
  et a échoué en ML-2 via `exog_dax_ret_lag1`).
- Labels : `triple_barrier_labels(df, horizon=H=5, vol_span=20, mult=1.5)`,
  calculés **indépendamment sur chaque marché** (les barrières sont
  proportionnelles à la volatilité locale du marché concerné, donc
  automatiquement homogénéisées entre marchés de volatilité différente).
- Cible binaire : `(label > 0)`, comme dans `walk_forward_proba`.

### 3.3 Marchés (univers FIGÉ, 3 marchés, aucun ajout possible)

| Marché | Fichier | Période | Séances |
|---|---|---|---|
| Russell 2000 | `data/russell2000_daily.txt` | 10/09/1987 → 13/07/2026 | 9 782 |
| S&P 500 | `data/sp500_daily.txt` | 02/01/1970 → 13/07/2026 | 14 252 |
| DAX | `data/dax_daily.txt` | 01/11/1999 → 10/07/2026 | 6 777 |

Chaque fichier est validé par `data_loader.quality_report()` **avant** usage
(Règle 7 : vérification opérationnelle). Un fichier qui échoue la validation
interrompt le cycle et le fait est rapporté ; il n'est jamais « nettoyé » à la
volée pour faire passer le calcul.

### 3.4 Règle de pooling EXACTE (anti-fuite temporelle croisée)

C'est le cœur méthodologique du cycle. Le risque est qu'une ligne
d'entraînement issue d'un marché étranger porte de l'information postérieure
au début du bloc de test du marché évalué. La purge est donc définie **en dates
calendaires**, pas en indices (les calendriers de bourse diffèrent : jours
fériés US ≠ allemands).

Pour le marché évalué **m**, à chaque ré-estimation walk-forward d'indice `tr`
(`tr = T0, T0+21, T0+42, …`) :

1. **Date de début du bloc de test** : `D_test = date_m[tr]` (première séance de
   m sur laquelle le modèle ré-estimé décidera).
2. **Date de fin de label** d'une ligne `i` d'un marché `k` quelconque :
   `L_k[i] = date_k[min(i + H, n_k − 1)]` — la barrière verticale du label
   triple-barrière de la ligne `i` est atteinte au plus tard à cette date, dans
   le calendrier de bourse **du marché k**.
3. **Critère d'inclusion, appliqué identiquement aux 3 marchés** : la ligne `i`
   du marché `k` entre dans l'échantillon d'entraînement **si et seulement si**
   `L_k[i] < D_test`, et si ses features et son label sont finis.

   *Propriété vérifiée analytiquement et à re-vérifier en test unitaire dans le
   code* : pour `k = m` (le marché évalué lui-même), ce critère est
   **strictement équivalent** au masque de la baseline `walk_forward_proba`
   (`indice < tr − EMBARGO`, avec `EMBARGO = H = 5`) : `date_m[i+5] <
   date_m[tr] ⟺ i+5 ≤ tr−1 ⟺ i ≤ tr−6`. Le pooling est donc une **extension
   stricte** de la baseline : sur un pool réduit au seul marché m, il redonne
   exactement la baseline. Cette non-régression sera vérifiée numériquement.

4. **Contribution minimale** : un marché `k` ne contribue au pool que s'il
   fournit **≥ 100 lignes utilisables** à cette date (même garde-fou que le
   `mask.sum() < 100` de `walk_forward_proba`). Sinon son bloc est ignoré. En
   pratique cela retire mécaniquement le DAX du pool d'entraînement des
   ré-estimations antérieures à ~2000 et le Russell 2000 de celles antérieures
   à ~1991 — **c'est une caractéristique déclarée d'avance, pas un ajustement**,
   et elle n'affecte JAMAIS une fenêtre de test (§2, contrôle ML-2).
5. **Aucune pondération** : concaténation simple des blocs, pas de
   `class_weight`, pas de rééquilibrage par marché, pas de pondération par
   récence. Choix fixé ici pour ne pas introduire de degré de liberté
   supplémentaire.

### 3.5 Standardisation (fixée a priori)

La baseline `LogitL2` standardise sur la fenêtre d'entraînement
(`standardize=True`). En pooling, la statistique de standardisation est
calculée **par marché**, sur les lignes de CE marché présentes dans le pool
d'entraînement courant : le bloc du marché `k` est centré-réduit par
`(µ_k, σ_k)` estimés sur ses propres lignes d'entraînement, puis les blocs sont
concaténés. Les lignes de **test** du marché `m` sont standardisées par
`(µ_m, σ_m)` — les statistiques d'entraînement de leur propre marché.

Justification fixée d'avance : (i) c'est ce qui rend les features réellement
comparables entre marchés de niveaux de volatilité différents (Russell 2000 est
structurellement plus volatil que le S&P 500), donc ce qui donne au pooling une
chance de fonctionner ; (ii) c'est une **extension stricte** de la baseline —
avec un seul marché dans le pool, elle est identique au comportement de
`walk_forward_proba` ; (iii) aucune statistique n'est calculée sur des données
de test (`σ` est toujours estimée sur les lignes d'entraînement). Les `σ` nulles
sont remplacées par 1,0, comme dans le code existant.

### 3.6 Protocole walk-forward (identique à ML-1/ML-2/ML-3)

- `T0 = 750`, `refit_every = 21` séances, `purge/embargo = 5` séances
  (= H, sous la forme calendaire du §3.4), `H = 5`, `vol_span = 20`,
  `barrier_mult = 1,5`.
- Coûts **5 bps** aller-retour prélevés sur `|Δposition|` (`backtest()`).
- OOS du marché m : `oos = [T0, n_m − 1)` (la dernière ligne n'a pas de
  rendement futur). Chaque marché a donc SA fenêtre OOS, jamais mélangée.
- Position : `signe(p_up − 0,5) ∈ {−1, +1}`, 0 pendant le warmup.

### 3.7 Comparateurs calculés dans le même run

Pour chaque marché, sur SA fenêtre OOS :

- **`BuyHold`** — position +1 constante. **C'est le benchmark du critère.**
- **`LogitL2Solo`** — le MÊME modèle, entraîné sur le seul marché évalué,
  recalculé dans CE run avec le même code, les mêmes labels, la même graine :
  c'est le contraste interne qui isole l'effet du pooling et **rien d'autre**.
- **`Momentum`** — signe du rendement 10 j, référence de l'univers Étape B.

Ces comparateurs ne sont pas des candidats : le candidat unique est
`LogitL2Pooled`. **n_trials local du cycle = 1.**

## 4. Règle 10 (fraction hors-marché)

Le candidat est ±1 en permanence hors warmup : il ne détient jamais de fraction
« hors-marché » significative. L'hypothèse de rémunération retenue est donc
**0 % (cash nu)** sur les seules séances de warmup, hypothèse explicitement
déclarée ici et sans effet matériel sur le verdict.

## 5. Critère de succès chiffré — PAR MARCHÉ

Pour chaque marché `m ∈ {Russell 2000, S&P 500, DAX}`, sur sa fenêtre OOS, net
de coûts 5 bps, `LogitL2Pooled` **passe le niveau 1 sur ce marché** si :

- **(A)** `Sharpe_ann(LogitL2Pooled) > Sharpe_ann(BuyHold)` **ET**
  `rendement_ann(LogitL2Pooled) > rendement_ann(BuyHold)` ;
- **OU (B)** `Calmar(LogitL2Pooled) > Calmar(BuyHold)`.

Le benchmark est **toujours le Buy & Hold du MÊME marché sur la MÊME fenêtre
OOS** — jamais celui d'un autre marché, jamais une moyenne inter-marchés.

## 6. Règle d'agrégation — FIXÉE AVANT TOUT CALCUL

**Verdict global du cycle ML-4 = PASS niveau 1 si et seulement si AU MOINS
2 marchés sur 3 passent le critère du §5.** Sinon **FAIL niveau 1**.

Justification, écrite avant d'avoir vu le moindre chiffre :

- Évaluer 3 marchés, c'est se donner **3 chances**. Une règle « 1 sur 3 suffit »
  transformerait un tirage favorable isolé en PASS et contredirait frontalement
  la Règle 2 (correction pour essais multiples) — c'est exactement le travers
  que ce backlog est conçu pour éviter.
- Une règle « 3 sur 3 » serait à l'inverse excessivement sévère : le DAX ne
  dispose que de 6 777 séances (OOS ~6 000) et son pool d'entraînement est
  amputé du Russell 2000 pré-1991 et de lui-même pré-1999 ; un échec DAX seul
  ne réfuterait pas l'hypothèse.
- L'hypothèse testée est que le pooling **généralise** ; la majorité stricte
  (2/3) est la traduction fidèle de cette hypothèse.

**Clause complémentaire, également fixée ici** : la batterie de validation
renforcée (§2.4 du backlog ML / Règle 9) est exécutée sur **chaque marché qui
passe individuellement le §5**, y compris si le verdict global est FAIL (cas
1/3). Cela ne change PAS le verdict global — un seul marché passant reste un
FAIL niveau 1 pour le cycle — mais permet de documenter honnêtement la
robustesse du cas isolé. La batterie est **séparée par marché** : `spa_test`
compare un candidat à UN SEUL benchmark partagé (limite mécanique déjà
rencontrée aux cycles non-ML #150/#159), donc **aucun test SPA joint
multi-marchés n'est tenté** ; un SPA et un DSR distincts sont calculés sur
chaque marché concerné.

## 7. Notification

**Notification Telegram émise UNIQUEMENT si les 5 contrôles a-e de la batterie
renforcée passent TOUS pour au moins un marché** (PASS RENFORCÉ complet sur ce
marché). Jamais pour un PASS niveau 1 seul, jamais pour un « le pooling améliore
l'accuracy ».

## 8. DSR — n_trials

Tout DSR de ce cycle est calculé avec **`n_trials = 408`** = 400 (brute-force ML
1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1) + 1 (ML-2) + 1 (ML-3) + 1
(ce cycle ML-4), conformément à la section 1 de `ML_STRATEGY_BACKLOG.md`
(407 avant ce cycle). **Jamais réduit à 1** (Règle 2). `var_trials` est estimée
sur la dispersion des Sharpe quotidiens des signaux évalués du marché concerné,
comme dans ML-1/2/3. Le DSR est calculé **séparément par marché**, jamais
sur une série poolée.

## 9. Engagements anti-snooping

1. Ni les 3 marchés, ni les hyperparamètres, ni la règle de pooling (§3.4), ni
   la standardisation (§3.5), ni le critère (§5), ni la règle d'agrégation (§6)
   ne seront modifiés après avoir vu un résultat, même partiel.
2. Aucune fenêtre de test ne sera « recadrée » après coup (piège explicite de
   ML-2, où le recadrage aurait aussi déplacé le benchmark).
3. Aucun marché supplémentaire ne sera ajouté, aucun marché ne sera retiré du
   verdict après calcul.
4. Un bug détecté en cours de route est corrigé ET tous les calculs affectés
   sont relancés avant tout commit de résultat définitif.
5. Le résultat sera rapporté honnêtement, FAIL compris, avec le même niveau de
   détail que ML-1/ML-2/ML-3.
6. Aucune lecture secondaire NDX/Composite (§2).

## 10. Artefacts attendus

- `scripts/ml_crossmarket_pooling_backtest.py` (candidat + comparateurs, 3
  marchés, test de non-régression du §3.4/§3.5).
- `results/ml_crossmarket_pooling.md` (verdict par marché + verdict global).
- `results/ml_crossmarket_pooling_<marché>_pnl.npz` (positions OOS pour audit).
- `scripts/ml_crossmarket_pooling_battery.py` (batterie renforcée, exécutée
  seulement si au moins un marché passe le §5).
