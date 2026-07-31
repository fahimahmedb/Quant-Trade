# PRÉ-ENREGISTREMENT — ML-1 : meta-labeling sur le signal officiel Étape B (LogitL2, NDX)

Date de rédaction : 31/07/2026. **Committé AVANT tout calcul** (Règle 1 de
`PROTOCOLE_ANTI_SNOOPING.md`, section 2.1 de `ML_STRATEGY_BACKLOG.md`).
Cycle ML-1 du backlog ML relancé.

## 1. Hypothèse testée

Le signal directionnel officiel de l'Étape B sur NDX (LogitL2,
`finance/trading/results/etape_B_ndx100.md`) est **rentable net de coûts**
(Sharpe annualisé +0,30, accuracy 53,67 %, break-even 16,6 bps ≫ 5 bps réels)
mais reste **sous Buy & Hold** en base déflatée (DSR 0,372 vs 0,842).

Hypothèse (López de Prado, AFML ch. 3) : LogitL2 décide seul de la direction
ET de la mise (toujours ±1, donc toujours 100 % exposé). Un **second modèle**
(meta-label) qui apprend *quand faire confiance* au pari primaire — sans jamais
changer son sens — devrait couper les paris de faible conviction, réduire le
turnover/whipsaw, et donc rapprocher le Sharpe et le Calmar effectifs de ceux
de Buy & Hold.

Hypothèse nulle : le meta-label n'apporte rien d'exploitable ; la position
filtrée ne bat pas Buy & Hold sur le critère chiffré du §5.

## 2. Définition EXACTE du mécanisme (FIGÉE — aucune variante)

Le modèle **primaire est intouché** : il reste exactement le LogitL2 de
l'Étape B (`LogisticRegression(C=0.5, max_iter=1000)`, features
`build_features`, labels triple-barrier, standardisation calée sur la fenêtre
d'entraînement).

**Modèle secondaire (UNE seule définition, aucune grille) :**

- Architecture : `LogisticRegression(C=0.5, max_iter=1000)` — identique au
  primaire. Choix par parcimonie et par cohérence, PAS par comparaison de
  performances (aucune variante RandomForest/XGBoost/HistGB n'est évaluée dans
  ce cycle ; `SECONDARY_MODELS` de `finance/src/meta_labeling.py` contient
  d'autres entrées, elles ne sont PAS utilisées ici).
- Features (FIGÉES) : toutes les colonnes de `build_features(df)` (identiques
  au primaire) **+ 2 colonnes dérivées du primaire** :
  - `primary_conf` = |p_up − 0,5| × 2 (confiance du primaire, dans [0,1]),
  - `primary_p_up` = p_up brut du primaire.
- Cible (FIGÉE) : label binaire = 1 si `signe(label triple-barrier au jour t)`
  coïncide avec `signe(pari primaire au jour t)`, 0 sinon. NaN (donc exclu de
  l'entraînement) là où le primaire ne parie pas encore (warmup walk-forward).
- Sortie : `p_win` = probabilité OOS que le pari primaire soit gagnant.

**Règle de position finale (FIGÉE, une seule formule) :**

```
taille = clip( 2 * (p_win - 0.5), 0, 1 )        # 0 si p_win <= 0.5, 1 si p_win >= 1
taille = 0 si p_win est NaN (secondaire pas encore entraîné)
position_finale = signe(p_up - 0.5) * taille    # dans [-1, +1]
```

Cette formule est **à la fois** le filtre à seuil demandé (p_win ≤ 0,5 → mise
nulle) et un dimensionnement continu borné [0,1]. Elle correspond à
`meta_size(mode="continuous")` de `finance/src/meta_labeling.py`. Aucune autre
valeur de seuil, aucune autre rampe, aucun mode alternatif ne sera évalué dans
ce cycle : **n_trials local pour ce cycle = 1**.

## 3. Protocole (identique à l'Étape B officielle, non modifié)

- Données : `finance/trading/data/nasdaq100_daily.txt` (NDX, 10273 séances,
  01/10/1985 → 13/07/2026).
- Labels : triple barrier H=5 j, barrières ±1,5·σ (σ ewm 20 j).
- Walk-forward expansif : T0=750, ré-estimation tous les 21 j.
- **Purge/embargo = 5 j** (= H). Valeur retenue = celle de la référence
  canonique citée par `CLAUDE.md` et `results/etape_B_ndx100.md` (le résultat
  officiel Sharpe +0,30 / DSR 0,372 que ce cycle cherche à améliorer). Un
  variant embargo=21 j existe (`results/etape_B_phase1_fixed.md`,
  `run_etape_b.py` actuel) ; il n'est PAS utilisé ici pour rester comparable à
  la référence officielle. Justification théorique : avec H=5, le dernier
  label d'entraînement (indice tr−6) se résout en tr−1, strictement avant le
  début du bloc de test tr — l'embargo de 5 j suffit à supprimer le
  chevauchement. Le secondaire subit **exactement le même** purge/embargo
  (son label dérive du même triple barrier).
- Coûts : **5 bps** aller-retour sur |Δposition| (`backtest()` de
  `finance/src/prediction.py`). Le dimensionnement continu génère des Δposition
  fractionnaires : ils sont facturés au même tarif, sans remise.
- Fenêtre d'évaluation OOS : **identique à l'Étape B officielle**, indices
  [T0, n−1) (9522 séances). Pendant le warmup du secondaire (il lui faut
  ≥100 paris primaires étiquetés avant sa première estimation), `p_win` est
  NaN donc la taille est 0 : la stratégie est **à plat**, ce qui la pénalise.
  Cette pénalité est acceptée telle quelle pour garder la fenêtre de
  comparaison strictement identique à celle de l'Étape B.
- Pas de split design/test supplémentaire : le walk-forward OOS EST le jeu de
  test de l'Étape B officielle. Le verrou temporel de la Règle 8 (lockbox des
  derniers mois) est une étape distincte, hors périmètre de ce cycle.

## 4. Règle 10 — fraction hors-marché

Le mécanisme réduit l'exposition sous 1,0× en valeur absolue (taille ∈ [0,1]) :
il détient donc implicitement du capital hors-marché. **Hypothèse déclarée :
rémunération 0 % (cash nu).** Justification : (i) la référence Étape B
(LogitL2 ±1, BuyHold 1,0×) est elle aussi calculée sans taux sans risque, donc
la comparaison reste homogène ; (ii) 0 % est l'hypothèse **conservatrice** pour
l'hypothèse testée — un rendement de portage ne pourrait que gonfler
artificiellement le candidat. Si le résultat est PASS ou proche du seuil, la
décomposition portage/effet-prix du cycle #142 (backlog non-ML) ne s'impose
donc pas comme préalable, mais l'hypothèse 0 % sera rappelée dans le rapport.

## 5. Critère de succès chiffré (FIGÉ)

Sur la fenêtre OOS NDX ci-dessus, nette de 5 bps, la position meta-labellisée
doit satisfaire **au moins une** des deux conditions (critère niveau 1 du
§2.4 de `ML_STRATEGY_BACKLOG.md`) :

- **(A)** Sharpe annualisé > Sharpe annualisé Buy & Hold **ET** rendement
  annualisé > rendement annualisé Buy & Hold ; **OU**
- **(B)** Calmar > Calmar Buy & Hold.

Repères Buy & Hold à battre (recalculés dans le script, valeurs de référence
`etape_B_ndx100.md`) : Sharpe +0,52 · rendement +14,5 %/an · Calmar +0,08.

Tout autre résultat = **FAIL**, rapporté tel quel. Une amélioration par rapport
au LogitL2 nu qui ne franchirait pas Buy & Hold ne constitue **pas** un PASS.

## 6. Si PASS niveau 1 — batterie de validation renforcée (§2.4 du backlog ML)

Les 5 contrôles doivent TOUS passer pour un PASS RENFORCÉ (seule condition
autorisant une notification Telegram) :

a. Stress de coûts ×3 et ×5 (15 bps, 25 bps) — critère du §5 maintenu.
b. Stress de crise (2000-2002, 2007-2009, 02-04/2020, 2022) : MDD du candidat
   pas pire que celui de Buy & Hold sur la fenêtre.
c. Stabilité temporelle : 4 folds non chevauchants + embargo 5 j ; le candidat
   doit battre Buy & Hold sur une **majorité** de folds.
d. SPA de Hansen à 1 candidat contre Buy & Hold (`spa_test`,
   `finance/src/volatility.py`), seuil p < 0,05.
e. DSR avec **n_trials = 405** = 400 (itérations brute-force ML 1-10 closes,
   `n_trials_pooled`) + 4 (univers figé Étape B) + 1 (ce cycle ML-1). Jamais 1.
   `var_trials` = variance (ddof=1) des Sharpe **quotidiens** des 5 signaux
   calculés dans ce même script (BuyHold, Momentum, LogitL2, HistGB, Meta) —
   même convention d'échelle que `run_etape_b.py`. Seuil DSR > 0,95.

## 7. Lecture secondaire déclarée (sans effet sur le verdict)

Le même calcul sera exécuté sur `nasdaq_composite_daily.txt` et rapporté à
titre informatif. Le Composite n'est PAS un marché indépendant du NDX
(Règle 3) : il ne peut ni valider ni invalider le verdict, et n'entre pas
dans le critère du §5.

## 8. Engagement

Aucune modification de l'univers (1 modèle secondaire, 1 formule de taille),
des features, du protocole ou du critère après avoir vu le moindre résultat.
Tout bug détecté est corrigé ET les calculs affectés relancés avant tout
commit de verdict.
