# Pré-enregistrement — Momentum 52-semaines (proximité du plus haut annuel)

**Committé AVANT tout calcul.** Cycle #4 du backlog non-ML. Soumis à la
**règle de succès renforcée** (Sharpe ET rendement absolu, cf.
`NONML_STRATEGY_BACKLOG.md`).

## Hypothèse

George & Hwang (2004) : les actions dont le prix est PROCHE de leur plus
haut sur 52 semaines ont tendance à continuer à surperformer — signal
différent du momentum classique (rendement passé), basé sur la distance
au plus haut. Règle déterministe, aucun paramètre appris (hors ML).

## Univers et période

Constituants ACTUELS du NASDAQ-100 (99 tickers avec prix déjà récupérés
dans `data/pead/prices/`, 2021-01-04 → 2026-07-27). **Même limite de
biais de survie que PEAD**, déjà documentée et assumée
(`PEAD_PREREGISTRATION.md`).

Fenêtre testable : à partir de 252 séances après le début de l'historique
(warmup nécessaire pour calculer le plus haut 52 semaines), soit à partir
d'environ janvier 2022.

## Définition du signal (fixée ici, avant tout résultat)

- Ratio à la date de rebalancement *t* : `close_t / max(close_{t-252:t})`
  (plus haut sur les 252 séances précédentes, INCLUANT le jour *t* — pas
  de fuite : c'est une information connue au moment de la décision).
- **Rebalancement mensuel** (tous les 21 jours de bourse, même cadence
  que le reste du projet).
- **Portefeuille "leaders"** : équipondéré sur le TERCILE SUPÉRIEUR de
  l'univers par ce ratio à chaque rebalancement (long-only, PAS long-short
  — pour rester comparable en exposition de marché à la référence
  Buy & Hold, conformément à la règle de succès renforcée).
- **Référence** : Buy & Hold équipondéré de l'univers COMPLET (mêmes 99
  titres, même fenêtre) — comparaison à univers identique, pas à l'indice
  NDX-100 pondéré par capitalisation.
- **Coûts** : 5 bps par unité de turnover à chaque rebalancement (titres
  qui entrent/sortent du tercile supérieur).

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille "leaders" doit battre le Buy & Hold équipondéré de
l'univers **simultanément** en :
1. Sharpe annualisé net de coûts, ET
2. Rendement total net de coûts sur toute la période testable.

n_trials=1 (une seule définition — pas de grille sur la largeur de
fenêtre 52 semaines ni sur la fréquence de rebalancement).

## Anti-cheat

Même processus que les cycles précédents : ce fichier committé avant
`nonml_momentum_52w_high_backtest.py`, vérification via
`nonml_anti_cheat_check.py momentum_52w_high`.
