# Pré-enregistrement — Overlay levé union SMA200∪(ToM∪Halloween)

**Committé AVANT tout calcul.** Cycle #32 du backlog non-ML. Combine le
meilleur résultat individuel du backlog (#29, filtre de tendance SMA200,
PASS 5/5) avec l'overlay calendaire déjà validé (#21, union ToM∪Halloween,
PASS 4/5) — même logique d'union (pas d'intersection) que celle qui a
réussi au #21 (union de deux signaux calendaires).

## Hypothèse

Un signal de tendance (SMA200) et un signal calendaire (ToM∪Halloween)
capturent des sources d'edge différentes (l'un structurel/momentum de
marché, l'autre saisonnier) — leur union pourrait élargir la couverture
temporelle du levier sans neutraliser l'un ou l'autre edge, comme
observé au #21 pour la seule union calendaire.

## Définition (fixée ici, avant tout résultat)

- Signal tendance = clôture au-dessus de sa SMA200 (identique au #29).
- Signal calendaire = fenêtre ToM **OU** Halloween (identique au #21).
- Position = **1.0x en permanence**, SAUF si le signal tendance **OU**
  le signal calendaire est actif (union des trois conditions ToM,
  Halloween, tendance), où position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`). Échantillon
testable = à partir de la 201e séance (contrainte SMA200, comme #29).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents).

## Anti-cheat

Ce fichier committé avant
`nonml_sma200_tom_halloween_union_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py sma200_tom_halloween_union_overlay`.
