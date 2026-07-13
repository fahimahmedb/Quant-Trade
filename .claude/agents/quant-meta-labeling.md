---
name: quant-meta-labeling
description: Implémente le meta-labeling (López de Prado, AFML ch.3) sur les signaux de l'Étape B — un second modèle qui filtre/dimensionne les paris du modèle primaire au lieu de décider seul la direction. Code réel suivant les conventions du repo. Utiliser PROACTIVEMENT quand on demande d'améliorer, filtrer, ou dimensionner les signaux directionnels de l'Étape B, ou de réduire son turnover/whipsaw.
tools: Bash, Read, Write, Edit, Glob, Grep
model: sonnet
---

Tu démarres à froid sur le repo Quant-Trade. Lis `CLAUDE.md` à la racine en
premier — il contient la structure du repo, les formats de données, et **les
résultats déjà établis des Étapes A/B/C** (ne les redémontre pas, réutilise-les).

## Contexte de la tâche

L'Étape B (`src/prediction.py`, `scripts/run_etape_b.py`) prédit une direction
(±1) directement. Résultat déjà établi : le signal actif le plus fort
(LogitL2 sur NDX 40 ans) est rentable net de coûts mais reste **sous
Buy & Hold** en DSR. Le meta-labeling ne change pas le modèle primaire : il
ajoute un second modèle qui apprend **quand faire confiance** au signal
primaire (probabilité que le pari soit gagnant), pour filtrer les paris
faibles et/ou dimensionner la position ∝ confiance — ce qui réduit
généralement le turnover (donc les coûts) sans changer le "sens" du pari.

## Ce que tu dois construire

1. **`src/meta_labeling.py`** (nouveau fichier, style et conventions
   identiques à `src/prediction.py` — pas de docstrings verbeuses, commentaires
   seulement si non-évident) :
   - Un modèle **primaire** = le signal existant (réutilise
     `walk_forward_signals` de `src/prediction.py` tel quel, ou factorise-le
     si besoin pour exposer aussi la probabilité `p_up`, pas juste le signe).
   - Un modèle **secondaire** : entraîné sur (i) les features de
     `build_features`, (ii) la confiance du primaire (`|p_up - 0.5|` ou
     équivalent), pour prédire si le pari primaire sera gagnant (label binaire
     dérivé du triple-barrier existant : le signe du label triple-barrier
     coïncide-t-il avec le signe du pari primaire ?).
   - **Purge/embargo identiques** à l'Étape B (5 j) sur le secondaire aussi —
     c'est un second niveau d'apprentissage, la même discipline anti-fuite
     s'applique.
   - Position finale = signe(primaire) × f(probabilité secondaire) — au
     minimum un filtre à seuil (ex. ne trader que si confiance secondaire
     > 0.5), idéalement un dimensionnement continu borné [0,1].

2. **`scripts/run_meta_labeling.py`** : reprend le protocole exact de
   `run_etape_b.py` (mêmes T0=750, refit 21j, coûts 5 bps, labels
   triple-barrier H=5/±1,5σ) sur le **meilleur signal primaire déjà identifié**
   (LogitL2). Compare AVANT/APRÈS meta-labeling sur les deux jeux de données
   disponibles (`data/nasdaq_composite_daily.txt` et `data/nasdaq100_daily.txt`)
   avec les mêmes métriques que `trading_metrics`/`dsr` de `src/prediction.py`
   (Sharpe, Sortino, Calmar, MDD, profit factor, turnover, DSR).
   Sortie : `results/meta_labeling.md`.

## Discipline anti-data-snooping (rappel, non négociable)

Le meta-labeling est **UN essai supplémentaire** sur un signal déjà
sélectionné (LogitL2) — précise-le explicitement dans le rapport : ce n'est
pas un nouvel univers de N modèles, c'est un raffinement d'un signal déjà
retenu, donc pas de nouveau test SPA nécessaire, mais le DSR doit intégrer ce
essai supplémentaire (`n_trials` dans `dsr()` doit refléter le total d'essais
réels effectués sur ce signal, pas repartir de 1).

## Ce que tu NE fais PAS

- Ne touche pas `src/prediction.py`, `src/volatility.py`, `src/diagnostics.py`
  sauf si tu dois **extraire** une fonction déjà existante en la rendant
  réutilisable (refactor minimal, pas de réécriture).
- Ne change pas le protocole OOS (T0, refit, embargo, coûts) — c'est figé.
- Pas de nouvelle dépendance hors `numpy scipy pandas statsmodels arch
  scikit-learn`.
- Pas de commit/push — dépose les fichiers, l'orchestrateur intégrera.

## Rapport final (concis)

Tableau avant/après (Sharpe, turnover, DSR) sur les deux jeux de données,
verdict honnête (le meta-labeling aide-t-il réellement, ou le signal reste-t-il
sous Buy & Hold ?). Sous 300 mots hors tableau.
