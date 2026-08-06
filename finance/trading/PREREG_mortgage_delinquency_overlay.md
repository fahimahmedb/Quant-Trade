# Pré-enregistrement — Taux de défaut hypothécaire US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #286 du backlog non-ML.

## Hypothèse

Le taux de défaut sur prêts hypothécaires résidentiels (FRED
`DRSFRMACBS`, trimestriel, "Delinquency Rate on Single-Family
Residential Mortgages, Booked in Domestic Offices, All Commercial
Banks") mesure la DÉTRESSE FINANCIÈRE liée au logement — canal
économique DISTINCT du #286 (crédit renouvelable/carte de crédit,
déclencheurs liés au revenu/emploi courant) : la crise de 2008 était
avant tout une crise HYPOTHÉCAIRE (subprimes), pas une crise de carte
de crédit, et les deux séries divergent historiquement (le cycle
immobilier — taux d'intérêt, prix des logements — n'est pas synchrone
avec le cycle de consommation générale).

## Données

Série FRED `DRSFRMACBS` récupérée le jour même
(`data/mortgage_delinquency_quarterly.csv`, TRIMESTRIELLE, 1991-2026,
141 observations, gratuite).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
STRICTE de la construction du #286 — seule la série change)

- **Construction** : NIVEAU brut du taux de défaut hypothécaire (même
  convention que #199 spread de crédit et #286 défaut carte de
  crédit — pas une croissance/variation).
- **Décalage de publication** : même délai conservateur d'un trimestre
  calendaire complet (`DateOffset(months=3)`) que le #286.
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `DRSFRMACBS_lag(t-1)` est dans son tercile expanding le
  PLUS HAUT (défauts hypothécaires les plus élevés observés jusqu'à
  présent — direction cohérente avec #199/#286, stress financier =
  défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Risque déclaré à l'avance

Construction quasi-identique au #286 (PASS 4/5) — un résultat similaire
est plausible du simple fait de la similarité méthodologique, mais la
série sous-jacente est économiquement distincte (mortgage vs crédit
renouvelable) et leur corrélation historique n'est pas parfaite
(cycles différents) : un résultat DIVERGENT du #286 est tout aussi
possible et serait tout aussi informatif. Rapporté tel quel, sans
retuning.

## Anti-cheat

Ce fichier committé avant `nonml_mortgage_delinquency_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283/#284/#285/#286), vérification dédiée du décalage d'un
trimestre, anti-lookahead par troncature. Sortie :
`results/nonml_mortgage_delinquency_overlay_result.md`.
