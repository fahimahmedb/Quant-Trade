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
| **Nouvelle campagne (ce fichier, à partir du cycle ML-1)** | **0 au départ, incrémenté à chaque cycle** | 0 |

**Total actuel pour tout DSR futur sur cette campagne : n_trials ≥ 404**
(400 brute-force + 4 cycles à venir minimum). Ce total sera mis à jour à
chaque cycle et cité dans chaque calcul DSR — jamais réduit.

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

*(à faire : ML-1, ML-2, ML-3, ML-4 — dans cet ordre, un cycle par firing de
la boucle autonome dédiée)*
