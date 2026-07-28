# Pré-enregistrement — Overlay levé pré/post jour férié

**Committé AVANT tout calcul.** Cycle #27 du backlog non-ML. Reprise du
cycle #7 (effet pré/post jour férié, détection data-driven, FAIL 0/5)
mais en design **overlay** (reste investi 1.0x en permanence, comme les
cycles #8/#17/#21, PAS flat hors fenêtre) — le #7 utilisait un design
flat, structurellement désavantagé en rendement absolu composé (même
limite déjà identifiée pour #2/#6, corrigée par le design overlay
justement introduit au #8).

## Hypothèse

L'effet "pré/post jour férié" documenté (rendements anormalement
positifs les séances entourant une fermeture de marché) existe peut-être
réellement (Sharpe positif isolé possible même si #7 était FAIL en flat),
mais seul un design overlay permet de le capter sans sacrifier le
rendement composé de la détention permanente.

## Définition (fixée ici, avant tout résultat)

- Détection des jours fériés **data-driven**, identique au cycle #7 :
  trou calendaire anormal entre deux séances consécutives (gap > 1
  jour, ou > 3 jours si veille de week-end).
- Fenêtre = jour PRÉ-férié **OU** jour POST-férié (union, même
  définition que #7).
- Position = **1.0x en permanence**, SAUF les jours dans la fenêtre où
  position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant `nonml_holiday_effect_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py holiday_effect_overlay`.
