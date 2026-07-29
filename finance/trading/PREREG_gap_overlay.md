# Pré-enregistrement — Overlay levé après un gap d'ouverture extrême

**Committé AVANT tout calcul.** Cycle #49 du backlog non-ML. Dernier
item de la file actuelle. Première hypothèse de ce backlog à exploiter
le prix d'OUVERTURE (`open`) — tous les cycles précédents n'utilisaient
que les clôtures. Le gap d'ouverture (écart entre la clôture de la
veille et l'ouverture du jour) est un signal classique de la
littérature microstructure (réaction à une nouvelle information
survenue hors séance).

## Hypothèse

Un gap d'ouverture extrême (positif ou négatif) reflète une réaction
forte à une information survenue hors séance — la séance qui suit ce
gap pourrait présenter une volatilité/direction différente de la
normale, exploitable par un overlay de levier temporaire, à distinguer
explicitement du choc de clôture-à-clôture déjà testé et FAIL aux
cycles #22 (repli 3j) et #24 (choc 1 séance clôture-à-clôture).

## Définition (fixée ici, avant tout résultat)

- Gap(t) = **open(t) / close(t-1) − 1** (rendement log-équivalent
  approximé en simple, cohérent avec la convention de la littérature
  gap trading).
- Régime "gap extrême" = **|Gap(t)| ≥ 2%** (seuil fixé a priori, ordre
  de grandeur typique d'un gap significatif sur indices actions).
- Le cadre du projet ne modélise que des rendements clôture-à-clôture
  (pas de position intra-séance) : le signal Gap(t) est connu à
  l'ouverture du jour t (donc strictement avant la clôture du jour t),
  et sert à décider la position appliquée aux DEUX rendements
  clôture-à-clôture suivants, r(t) = close(t+1)/close(t) et
  r(t+1) = close(t+2)/close(t+1) — même convention "fenêtre de N
  séances après détection" que les cycles #13/#22/#24. Position =
  **1.0x en permanence**, SAUF sur cette fenêtre de 2 séances où
  position = **CAP = 2.0x**. Si un nouveau gap extrême survient pendant
  la fenêtre déjà active, la fenêtre est relancée à 2 séances (même
  logique de re-déclenchement que #13/#22/#24).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`), colonne `open`
déjà chargée par `data_loader.load_ohlc`.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (seuil 2%, fenêtre 2j et CAP=2.0x fixés a priori,
aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_gap_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py gap_overlay`.
