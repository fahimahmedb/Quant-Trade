# Pré-enregistrement — Overlay de confirmation multi-marché (breadth)

**Committé AVANT tout calcul.** Cycle #52 du backlog non-ML. Dernier
item de la file actuelle. Premier signal de ce backlog basé sur une
CONFIRMATION CROISÉE entre deux marchés distincts (tous les cycles
précédents utilisaient un seul marché à la fois, éventuellement combiné
à un portefeuille de titres du même univers). Le signal 52w-high indice
(#37, meilleur signal de tendance du backlog) est déjà validé
séparément sur NDX ET sur Russell 2000 — ce cycle teste si l'EXIGER
SIMULTANÉMENT sur les deux marchés (intersection, pas union) améliore
la fiabilité du signal appliqué au marché primaire (NDX).

## Hypothèse

Un régime haussier confirmé par DEUX marchés indépendants (grandes
capitalisations technologiques via NDX ET petites capitalisations via
Russell 2000) pourrait être un signal de tendance de marché plus
large et plus fiable qu'un seul marché isolé, réduisant les faux
signaux propres à un secteur/style particulier (ex. NDX dominé par la
tech, Russell 2000 plus diversifié).

## Définition (fixée ici, avant tout résultat)

- Marché primaire (celui sur lequel l'overlay est appliqué et mesuré) =
  NDX-100 (`data/nasdaq100_daily.txt`).
- Marché de confirmation = Russell 2000 (`data/russell2000_daily.txt`).
- Signal A = NDX-100 ≥95% de son plus haut glissant 252j (identique au
  #37).
- Signal B = Russell 2000 ≥95% de son plus haut glissant 252j (identique
  au #37, mêmes paramètres).
- Alignement causal des deux séries par date (ffill sur le calendrier du
  marché primaire si les dates ne coïncident pas exactement, jamais de
  donnée future).
- Position sur NDX = **1.0x en permanence**, SAUF les jours où **A ET B
  sont simultanément actifs** (intersection stricte), où position =
  **CAP = 2.0x**. Décision prise à la clôture du jour t, appliquée au
  rendement NDX t→t+1.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/nasdaq100_daily.txt` et `data/russell2000_daily.txt`, déjà en
local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. n_trials=1
(seuil 95%/252j identique au #37, CAP=2.0x cohérent avec tous les
cycles précédents, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_breadth_confirmation_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py breadth_confirmation_overlay`.
