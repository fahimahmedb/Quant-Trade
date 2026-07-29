# Pré-enregistrement — Overlay de confirmation multi-marché INTERNATIONALE (NDX+DAX)

**Committé AVANT tout calcul.** Cycle #63 du backlog non-ML. Variante du
#52 (NDX confirmé par Russell 2000, marché domestique, PASS marginal)
avec le DAX (marché européen, corrélation structurellement différente)
comme marché de confirmation — teste si une confirmation cross-continent
apporte plus de valeur informative qu'une confirmation domestique.

## Hypothèse

Le #52 a montré qu'une confirmation domestique (NDX+Russell 2000, deux
marchés US fortement corrélés) apporte un edge Sharpe minuscule et
fragile. Un marché de confirmation international (DAX, exposé à un cycle
macroéconomique et une politique monétaire partiellement différents)
pourrait apporter une information plus indépendante : si NDX ET DAX sont
simultanément en régime de force, la conviction sur la solidité du
régime haussier global pourrait être mieux établie qu'avec deux marchés
domestiques très corrélés.

## Définition (fixée ici, avant tout résultat)

- Signal A = NDX ≥95% de son plus haut glissant 252j (identique au #37).
- Signal B = DAX ≥95% de son plus haut glissant 252j (identique au #37,
  mêmes paramètres, appliqués au DAX au lieu du Russell 2000).
- Alignement causal des deux séries par date (ffill sur le calendrier du
  marché primaire NDX si les dates ne coïncident pas exactement — jours
  fériés différents entre bourses US et allemande —, jamais de donnée
  future).
- Position sur NDX = **1,0x en permanence**, SAUF les jours où **A ET B
  sont simultanément actifs** (intersection stricte), où position =
  **CAP = 2,0x**. Décision prise à la clôture du jour t, appliquée au
  rendement NDX t→t+1. Mécanisme binaire simple, identique au #52 (PAS
  le mécanisme hiérarchique vol-targeting du #57, pour rester comparable
  directement au #52).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique sur NDX-100.

## Univers et période

`data/nasdaq100_daily.txt` et `data/dax_daily.txt`, déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold (NDX) **simultanément** en Sharpe
annualisé net de coûts ET en rendement total net de coûts. Un seul
marché testé (NDX), comme au #52, car le mécanisme nécessite un second
marché de confirmation. n_trials=1 (seuil 95%/252j et CAP=2,0x
identiques au #37/#52, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_intl_breadth_confirmation_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py intl_breadth_confirmation_overlay`.
