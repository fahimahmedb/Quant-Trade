# Pré-enregistrement — Overlay levé sur pullback court terme (niveau indice)

**Committé AVANT tout calcul.** Cycle #22 du backlog non-ML. Variante
court-terme du choc extrême déjà testé au cycle #13 (drawdown ≤-10% sur
20j -> FAIL net) : ici un repli beaucoup plus modeste et beaucoup plus
rapide, sur un horizon de rebond également plus court.

## Hypothèse

Un repli court (2-3 séances) de quelques % au niveau de l'INDICE (pas
d'un titre individuel) est suivi statistiquement d'un léger rebond à très
court terme (mean-reversion de marché à haute fréquence documentée dans
la littérature microstructure) — un overlay qui augmente temporairement
l'exposition juste après ce repli devrait capter ce rebond.

## Définition (fixée ici, avant tout résultat)

- Repli = rendement log cumulé sur les **3** dernières séances de clôture
  ≤ **-3%**.
- Dès qu'un repli est détecté au jour t (décision prise avec les données
  disponibles à la clôture de t, appliquée au rendement t→t+1, même
  convention causale que tous les cycles précédents), position =
  **CAP = 2.0x** pendant les **5** séances suivantes (fenêtre de rebond),
  1.0x sinon. Si un nouveau repli survient pendant la fenêtre déjà
  active, la fenêtre est relancée à 5 séances (même logique de
  re-déclenchement que le cycle #13).
- Horizon volontairement différent du cycle #13 (repli 3j/-3% + rebond 5j
  ici, vs choc 20j/-10% + rebond 20j au #13) — il s'agit d'une hypothèse
  distincte (micro-pullback) et non d'un retuning du #13.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_short_pullback_rebound_backtest.py`,
vérification via `nonml_anti_cheat_check.py short_pullback_rebound`.
