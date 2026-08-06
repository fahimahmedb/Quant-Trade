# Pré-enregistrement — Porte combinée (ET) défaut carte de crédit + NFCI

**Committé AVANT tout calcul.** Cycle #296 du backlog non-ML.

## Hypothèse

Le #286 (taux de défaut cartes de crédit DRCCLACBS, PASS net 4/5) et
le #291 (indice des conditions financières NFCI, PASS net 4/5) sont
les deux SEULS PASS niveau 1 de toute la campagne macro-externe
étendue de cette session (#276-297), avec respectivement le meilleur
(3/5) et le 2e meilleur (2/5) score Règle 9. Ils mesurent deux canaux
de stress ÉCONOMIQUEMENT INDÉPENDANTS : le comportement de
remboursement RÉEL des ménages (#286) et l'état AGRÉGÉ des marchés
financiers (#291, ~105 indicateurs de risque/crédit/levier). Même
esprit que la porte combinée kurtosis+ν du #240 (PASS 4/5) : deux
mesures indépendantes convergeant simultanément vers le même
diagnostic de régime devraient constituer un signal plus précis
(moins de faux positifs) qu'une seule prise isolément.

## Adaptation technique : réutilisation stricte, Règle 7

Aucune nouvelle donnée, aucune modification des deux définitions
propres déjà validées et committées :
- `build_delinquency_series()` / `load_delinquency_lag()` du #286
  (`nonml_credit_card_delinquency_overlay_backtest.py`) — décalage
  trimestriel, tercile expanding le plus haut du niveau DRCCLACBS.
- `build_nfci_series()` / `load_nfci_lag()` du #291
  (`nonml_financial_conditions_overlay_backtest.py`) — décalage de
  7 jours, tercile expanding le plus haut du niveau NFCI.

## Définition (fixée ici, AVANT tout calcul)

- `GateDelinq(t)` = 1 si `DRCCLACBS_lag(t-1)` est dans son tercile
  expanding le plus haut (identique au #286), sinon 0.
- `GateNFCI(t)` = 1 si `NFCI_lag(t-1)` est dans son tercile expanding
  le plus haut (identique au #291), sinon 0.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier, réutilisé des deux composantes) si `GateDelinq(t) AND
  GateNFCI(t)` (les DEUX signaux indiquent un stress simultanément),
  `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule combinaison ET testée, pas de grille).

## Risque déclaré à l'avance

L'intersection (ET) de deux portes déjà actives 18-30% (#286) et
20-40% (#291) du temps chacune réduira mécaniquement le temps actif
combiné — un risque de "porte trop rare pour être informative" (déjà
observé au #89, breadth de faiblesse) est possible et sera rapporté
honnêtement si constaté, sans retuning.

## Anti-cheat

Ce fichier committé avant `nonml_delinquency_nfci_combined_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_delinquency_nfci_combined_overlay_result.md`.
