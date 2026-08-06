# Pré-enregistrement — Mises en chantier de logements US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #281 du backlog non-ML.

## Hypothèse

Les mises en chantier de logements (FRED `HOUST`, mensuel) sont
documentées en analyse macro comme un indicateur AVANCÉ de cycle
économique : le secteur de la construction, très sensible aux taux
d'intérêt, ralentit typiquement AVANT le reste de l'économie lors d'un
resserrement monétaire, et une chute marquée du glissement annuel des
mises en chantier a historiquement précédé plusieurs récessions US
(2006-2007 avant 2008, par exemple). Premier signal SECTORIEL
(construction/immobilier) de ce backlog — distinct de tous les signaux
déjà testés (taux, crédit, inflation, dollar, sentiment, activité
composite CFNAI, marché du travail ICSA, masse monétaire M2).

## Données

Série FRED `HOUST` récupérée le jour même (`data/houst_monthly.csv`,
mensuelle, 1959-2026, 810 observations, gratuite). Limite déclarée à
l'avance : série MENSUELLE, publiée avec un délai (~3 semaines) — même
traitement causal (décalage d'un mois calendaire avant ffill) que
#195/#203/#204/#205/#206, Règle 7.

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- `HoustGrowth(t) = log(HOUST(t) / HOUST(t-12))` (glissement annuel,
  fenêtre 12 mois réutilisée du #203).
- Alignement causal : décalage d'un mois calendaire (publication) puis
  `ffill` + `shift(1)` sur le calendrier boursier (même fonction que
  #195/#203).
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `HoustGrowth(t-1)` est dans son tercile expanding le PLUS
  BAS (chute la plus marquée des mises en chantier observée jusqu'à
  présent — direction cohérente avec #203/#204/#206, faiblesse
  économique = défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_housing_starts_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel (même méthode que #195/#203/#204/#205/#206), vérification
dédiée du décalage d'un mois (même test que les cycles précédents).
Sortie : `results/nonml_housing_starts_overlay_result.md`.
