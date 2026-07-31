# Backlog ML relancé — état + règles

Ce fichier gouverne la **nouvelle** campagne de recherche ML, ouverte le
31/07/2026 à la demande explicite de l'utilisateur ("relancer l'angle ML en
réutilisant la rigueur développée sur le backlog non-ML"). Il coexiste avec
`NONML_STRATEGY_BACKLOG.md` (backlog non-ML, clos à 74 PASS niveau 1/160,
0 PASS RENFORCÉ) et réutilise explicitement `PROTOCOLE_ANTI_SNOOPING.md`.

## 0. Héritage — clôture honnête de l'ancienne campagne ML

Avant tout nouveau calcul (Règle 6 traçabilité, Règle 7 vérification
opérationnelle), état réel vérifié le 31/07/2026 par inspection directe de
`results/iterN/` (pas de confiance aveugle aux noms de fichiers commités) :

- `scripts/iterations/iter1.py` à `iter27.py` (univers sklearn brute-force,
  protocole T0=750/refit=21j/embargo=21j/H=5j/barrière 1,5σ/coûts 5bps,
  `scripts/ml_brute_force.py`) — **toutes committées le 27/07/2026**.
- **Itérations réellement exécutées : 1 à 10** (`results/iter4/` à
  `results/iter10/` confirmés, 50 fichiers `strategy_*.json` chacun).
  `results/iteration_9_summary.json` : `n_trials_pooled=358`, **0/50 PASS**
  à cette étape. **0 PASS sur l'ensemble des itérations exécutées.**
- **Itérations 11 à 27 : définies mais JAMAIS exécutées** (aucun
  `results/iter11/` … `results/iter27/`) — trouvé par vérification directe,
  pas par une note du code. Distinct de l'Étape B officielle (univers figé
  N=4, `results/etape_B_prediction.md` / `etape_B_ndx100.md`), qui reste la
  référence canonique citée dans `CLAUDE.md`.
- **Décision, prise ici avant tout nouveau calcul** : ne PAS exécuter les
  itérations 11-27. Reprendre un grind de 17×50 combinaisons sklearn
  quasi-aléatoires alourdirait le compteur `n_trials` (donc la pénalité DSR
  de tout futur candidat) sans discipline de conception claire — c'est
  exactement le travers que la Règle 9 (batterie renforcée) et toute la
  philosophie du backlog non-ML (petit N, grande rigueur) ont été conçues
  pour éviter. **Campagne 1-27 officiellement close, verdict : 0 PASS sur
  les 10 itérations réellement testées (~400 essais poolés), 17 itérations
  abandonnées sans exécution.**
- Cet historique reste dans le compteur `n_trials` cumulé (ligne suivante)
  car les résultats existent et ont influencé, même négativement, l'état
  des connaissances — ignorer ces essais parce qu'ils sont anciens serait
  une violation directe de la Règle 2.

## 1. Compteur n_trials cumulé (TOUTE l'histoire ML du repo)

| Source | n_trials | PASS |
|---|---|---|
| Itérations brute-force 1-10 (closes) | ~400 (voir `n_trials_pooled` par itération) | 0 |
| Étape B officielle (N=4, univers figé) | 4 (déjà comptés dans son propre DSR, ne s'ajoute pas au pool brute-force — protocole distinct) | 0 (aucun signal actif ne bat BuyHold à DSR>0,95) |
| **Nouvelle campagne (ce fichier, à partir du cycle ML-1)** | **2** (ML-1 et ML-2 : 1 essai local chacun) | 0 |

**Total actuel pour tout DSR futur sur cette campagne : n_trials = 406**
= 400 (brute-force ML 1-10, closes) + 4 (univers figé Étape B) + 1 (ML-1)
+ 1 (ML-2). Ce total est mis à jour à chaque cycle et cité dans chaque calcul
DSR — jamais réduit. Valeurs effectivement utilisées dans
`results/ml_meta_labeling_logitl2_ndx.md` §4 (405) et
`results/ml_exogenous_features_rates_crossmarket.md` §4 (406).

## 2. Discipline appliquée (réutilisée du backlog non-ML)

Chaque cycle de ce backlog suit EXACTEMENT le protocole qui a produit
74 PASS niveau 1 / 160 sur le non-ML :

1. **PREREG committé avant tout calcul** (`PREREG_ml_<nom>.md`) : hypothèse,
   univers de features/modèles FIGÉ, protocole (walk-forward purge/embargo
   déjà standard de `finance/src/prediction.py`), critère de succès chiffré.
2. Construction (build_features / modèle / walk_forward_signals / backtest),
   exécution, correction de tout bug AVANT commit d'un résultat.
3. Commit du résultat PASS ou FAIL, honnêtement.
4. **Si le critère niveau 1 est atteint** (Sharpe ET rendement > Buy&Hold,
   OU Calmar > Buy&Hold, n_trials=1 local) : batterie de validation
   renforcée ADAPTÉE ML avant toute déclaration PASS :
   a. Stress de coûts ×3/×5 (15bps/25bps).
   b. Stress de crise sur fenêtres historiques disponibles.
   c. Stabilité temporelle : le walk-forward purge/embargo est DÉJÀ le
      mécanisme natif ici (contrairement au non-ML où il a fallu l'ajouter) ;
      on exige en plus une découpe en folds non chevauchants explicite.
   d. SPA à 1 candidat contre Buy&Hold (`spa_test`).
   e. **DSR avec n_trials = total cumulé de la Section 1** (≥404 dès le
      premier cycle) — jamais réduit à 1 sous prétexte de nouveauté.
5. Mise à jour de ce backlog (statut, verdict, n_trials cumulé), commit.
6. **Règle 10** appliquée à tout mécanisme qui détient du capital
   "hors-marché" (ex. un filtre meta-labeling qui met certains paris à 0).
7. **Notification Telegram réservée exclusivement à un PASS RENFORCÉ**
   (les 5 contrôles a-e passent) — jamais pour un PASS niveau 1 seul,
   exactement comme sur le non-ML.

## 3. Axes de recherche fixés a priori (avant tout calcul, cycle par cycle)

Univers volontairement PETIT (rigueur > volume) :

- **ML-1 — Meta-labeling sur le signal officiel Étape B.** Réutilise
  l'agent `quant-meta-labeling` déjà construit pour ce repo (López de
  Prado, AFML ch.3) : un second modèle qui filtre/dimensionne les paris de
  LogitL2 (meilleur signal actif connu, NDX Sharpe +0,30 / accuracy 53,7 %
  net de coûts mais DSR 0,372 < BuyHold 0,842) au lieu de décider seul la
  direction. Hypothèse : réduire le turnover/whipsaw peut rapprocher le
  DSR de BuyHold sans changer le modèle primaire.
- **ML-2 — Features exogènes taux/cross-marché.** Ajouter à
  `build_features` des variables dérivées de `data/dgs10_daily.csv`,
  `data/dgs3mo_daily.csv` (niveau, pente, variation) et un terme de
  spillover NDX/DAX (déjà exploré côté non-ML aux cycles #140, #148-160)
  au modèle LogitL2 existant — sans changer le protocole walk-forward.
- **ML-3 — Architecture unique bien régularisée.** UN seul modèle non
  linéaire (gradient boosting avec early-stopping sur folds purgés, ou MLP
  à forte régularisation L2/dropout) évalué une fois, pas une grille —
  pour garder l'ajout de n_trials minimal et le résultat interprétable.
- **ML-4 — Cross-market pooling.** Entraînement conjoint sur plusieurs
  marchés indépendants au sens de la Règle 3 (Russell 2000, S&P 500, DAX)
  pour augmenter la taille effective de l'échantillon d'apprentissage.

Chaque axe peut se scinder en sous-cycles si un premier résultat mérite
un test de robustesse — mais aucun axe n'est ajouté à cette liste après
avoir vu un résultat (Règle 1).

## 4. État

| # | Nom | Statut | Verdict | n_trials cumulé après ce cycle |
|---|---|---|---|---|
| ML-0 | Clôture honnête campagne brute-force 1-27 | fait | 10 itérations exécutées, 0 PASS ; 17 abandonnées sans exécution | ~400 |
| ML-1 | Meta-labeling sur LogitL2 (NDX) | fait | **FAIL niveau 1** — Meta Sharpe +0,28 / rdt +1,4 %/an / Calmar +0,06 contre BuyHold +0,52 / +14,5 % / +0,08 : aucune branche du critère satisfaite. Le méta-modèle informe réellement (accuracy 54,20 %→55,81 %, turnover 0,268→0,039/j, MDD −59,6 %→−19,2 %) mais ses p_win restent serrées autour de 0,5 (médiane 0,562) → exposition moyenne 0,10, rendement écrasé sans gain de Sharpe. Batterie renforcée non déclenchée. Composite (lecture secondaire, Règle 3) : FAIL aussi. | **405** |
| ML-2 | Features exogènes taux/cross-marché (NDX) | fait | **FAIL niveau 1** — `LogitL2Exog` (21 features endogènes + 5 exogènes : `exog_dgs10_level`, `exog_slope_10y_3mo`, `exog_dgs10_chg`, `exog_dgs3mo_chg`, `exog_dax_ret_lag1`) : Sharpe +0,32 / rdt +7,4 %/an / Calmar +0,07 contre BuyHold +0,52 / +14,5 % / +0,08 — aucune branche du critère satisfaite. Les features exogènes **informent réellement** le modèle (accuracy 54,20 %→55,08 %, break-even 18,4→23,0 bps/trade, turnover 0,268→0,157/j) mais le candidat est **à plat sur 30,7 % de l'OOS** faute d'historique DAX avant le 01/11/1999, ce qui écrase son rendement annualisé (+9,5 %→+7,4 %) ; à Sharpe quasi inchangé (+0,35→+0,32), il ne peut pas franchir BuyHold. **Lecture secondaire déclarée AVANT calcul (aucun effet sur le verdict)** : sur la fenêtre restreinte où il est opérationnel (06/04/2000→10/07/2026), il bat BuyHold sur les deux branches (Sharpe +0,38 vs +0,28 ; rdt +10,8 % vs +7,8 % ; Calmar +0,10 vs +0,05) — mais cette fenêtre **affaiblit aussi le benchmark** (BuyHold −0,24 de Sharpe, elle s'ouvre juste avant le krach dot-com), biais explicitement documenté au §5.1 du rapport ; le PREREG lui refusait d'avance tout effet sur le verdict, et ce refus est maintenu. Batterie renforcée non déclenchée, aucune notification. Composite (lecture secondaire, Règle 3) : FAIL nettement (candidat −1,24 de Sharpe, les exogènes y **dégradent** le modèle, accuracy 52,0 %→48,0 %). | **406** |

*(à faire : ML-3, ML-4 — dans cet ordre, un cycle par firing de la
boucle autonome dédiée)*

**Enseignement ML-2 à reporter sur les cycles suivants** : une feature exogène
peut améliorer la *qualité* des paris (accuracy, break-even, turnover) sans
améliorer la performance, dès lors que sa **disponibilité historique** est plus
courte que la fenêtre d'évaluation — le modèle reste alors à plat sur une part
importante de l'échantillon et son rendement annualisé est mécaniquement
amputé. Corollaire de discipline : la fenêtre de verdict doit être fixée AVANT
de constater cet effet (ici elle l'a été, avec la lecture restreinte déclarée
d'avance comme informative), sinon la tentation de « recadrer » la fenêtre sur
la période opérationnelle transformerait un FAIL en PASS apparent — d'autant
plus dangereusement que ce recadrage déplace *aussi* le benchmark. Pour ML-4
(cross-market pooling), privilégier des marchés dont l'historique couvre la
fenêtre complète, ou pré-enregistrer explicitement une fenêtre commune ET son
benchmark recalculé.

**Enseignement ML-1 à reporter sur les cycles suivants** : sur ce signal, le
filtrage améliore la *qualité* des paris mais pas le Sharpe, parce que le
dimensionnement proportionnel à une probabilité mal calibrée détruit
l'exposition. Tout futur mécanisme de sizing devra pré-enregistrer sa
calibration (ou une normalisation d'échelle) AVANT calcul — pas après avoir
constaté une exposition trop faible, ce qui serait du snooping.

**PREREG et artefacts du cycle ML-1** :
`PREREG_ml_meta_labeling_logitl2_ndx.md`,
`scripts/ml_meta_labeling_logitl2_ndx_backtest.py`,
`scripts/ml_meta_labeling_logitl2_ndx_battery.py` (prêt, smoke-testé, non
applicable faute de PASS niveau 1),
`results/ml_meta_labeling_logitl2_ndx.md`,
`results/ml_meta_labeling_logitl2_composite.md`.

**PREREG et artefacts du cycle ML-2** :
`PREREG_ml_exogenous_features_rates_crossmarket.md`,
`scripts/ml_exogenous_features_rates_crossmarket_backtest.py`,
`results/ml_exogenous_features_rates_crossmarket.md` (NDX, verdict),
`results/ml_exogenous_features_rates_crossmarket_composite.md` (Règle 3),
`results/ml_exogenous_features_rates_crossmarket_pnl.npz` (positions OOS pour
audit). Extension de code réutilisable : `build_exogenous_features()` et
`build_features(df, exog=None)` dans `finance/src/prediction.py` — alignement
causal strict `obs_date < t` via `_asof_prev()`, non-régression du chemin
`exog=None` prouvée bit à bit (hash des features identique avant/après).
