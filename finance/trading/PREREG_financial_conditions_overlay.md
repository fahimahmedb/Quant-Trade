# Pré-enregistrement — Indice des conditions financières NFCI (overlay défensif)

**Committé AVANT tout calcul.** Cycle #289 du backlog non-ML.

## Hypothèse

L'indice des conditions financières de la Fed de Chicago (FRED `NFCI`,
hebdomadaire) agrège ~105 indicateurs de marché (spreads de crédit,
volatilité, levier, liquidité interbancaire) en une jauge unique,
standardisée (moyenne nulle, écart-type unitaire sur la période de
calibrage), du degré de resserrement ou de relâchement des conditions
financières. **Distinct du CFNAI (#206, FAIL)** : le CFNAI agrège des
indicateurs d'ACTIVITÉ ÉCONOMIQUE RÉELLE (production, emploi,
consommation), le NFCI agrège des indicateurs de STRESS DES MARCHÉS
FINANCIERS EUX-MÊMES (spreads, volatilité, levier) — deux canaux
économiquement distincts malgré leur structure "composite" commune.
2e série HEBDOMADAIRE testée dans ce backlog après ICSA (#204, FAIL).

## Données

Série FRED `NFCI` récupérée le jour même (`data/nfci_weekly.csv`,
HEBDOMADAIRE, 1971-2026, 2900 observations, gratuite — l'historique le
plus long de toute la famille macro-externe de ce backlog).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- **Construction** : NIVEAU brut du NFCI (pas une croissance/variation)
  — même convention que le spread de crédit BAA10Y (#199) et les taux
  de défaut (#286/#288/#289) : l'indice est déjà construit comme une
  jauge de stress en unités standardisées, pas une quantité nécessitant
  une normalisation par croissance.
- **Décalage de publication** : le NFCI de la semaine se terminant le
  vendredi est publié le vendredi suivant (~7 jours). Décalage
  conservateur de 7 jours calendaires (`Timedelta(days=7)`), même
  convention exacte que l'ICSA (#204), Règle 7.
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `NFCI_lag(t-1)` est dans son tercile expanding le PLUS
  HAUT (conditions financières les plus TENDUES observées jusqu'à
  présent — valeurs NFCI positives = resserrement, direction cohérente
  avec #199/#286), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_financial_conditions_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#289), vérification dédiée du décalage de 7 jours, anti-
lookahead par troncature. Sortie :
`results/nonml_financial_conditions_overlay_result.md`.
