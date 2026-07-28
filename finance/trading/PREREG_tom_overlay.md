# Pré-enregistrement — Turn-of-Month en overlay de levier

**Committé AVANT tout calcul.** Cycle #8 du backlog non-ML. Corrige
directement le problème structurel identifié aux cycles #2/#6/#7 (une
stratégie flat hors fenêtre ne peut pas battre le rendement composé de
Buy&Hold, indépendamment de la qualité de l'edge Sharpe).

## Hypothèse

Le cycle #2 (tournant de mois, 4j/3j) a montré un edge Sharpe réel
(4/5 marchés) mais insuffisant en rendement absolu car la stratégie était
FLAT hors fenêtre. En restant investi 1x en permanence (comme Buy&Hold)
et en ajoutant du levier SEULEMENT pendant la fenêtre ToM déjà identifiée,
on capture l'edge ET le compounding complet de Buy&Hold.

## Définition (fixée ici, avant tout résultat)

- Position = **1.0x en permanence** (comme Buy & Hold), SAUF pendant la
  fenêtre ToM (4 derniers j. de bourse du mois + 3 premiers j. du mois
  suivant, même définition que le cycle #2) où position = **CAP = 2.0x**
  (levier fixé a priori, pas retuné — cohérent avec les analyses
  Kelly/vol-targeting déjà faites dans ce projet, jamais illimité).
- **Coûts** : 5 bps par unité de changement de position, à chaque entrée
  et sortie de la fenêtre ToM (~24 transactions/an).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0 fixé une fois, pas de grille).

Risque assumé (instruction utilisateur du 28/07) : le levier amplifie
aussi les pertes, signalé honnêtement via le MDD dans le rapport, pas
seulement Sharpe/rendement.

## Anti-cheat

Ce fichier committé avant `nonml_tom_overlay_backtest.py`, vérification
via `nonml_anti_cheat_check.py tom_overlay`.
