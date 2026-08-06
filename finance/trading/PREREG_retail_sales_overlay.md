# Pré-enregistrement — Ventes au détail US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #293 du backlog non-ML.

## Hypothèse et nature du test

Les ventes au détail (FRED `RSXFS`, mensuel, US Census Bureau) mesurent
directement la consommation EFFECTIVE des ménages — des données de
TRANSACTIONS RÉELLES, pas une enquête d'opinion (UMCSENT, #205, FAIL),
pas un agrégat composite multi-secteurs (CFNAI, #206, FAIL), pas un
indicateur du marché du travail (ICSA, #204, FAIL). **Dernière
construction du canal "activité économique réelle"** testée dans ce
backlog — après ce cycle, ce canal (4 constructions distinctes :
composite, marché du travail, enquête, consommation directe) sera
considéré comme suffisamment exploré quel que soit le résultat
(déclaré à l'avance, Règle 2 : pas de 5e variante sans nouvelle
justification spécifique).

## Données

Série FRED `RSXFS` récupérée le jour même
(`data/retail_sales_monthly.csv`, MENSUELLE, 1992-2026, 414
observations, gratuite).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
STRICTE de la construction M2/HOUST/cuivre/Case-Shiller — indice
nominal en croissance structurelle, nécessite une normalisation YoY)

- `RetailGrowth(t) = log(RSXFS(t) / RSXFS(t-12))` (glissement annuel,
  fenêtre 12 mois réutilisée du #203/#283/#284/#294).
- **Décalage de publication** : ~2-3 semaines après la fin du mois
  (US Census Bureau, Advance Monthly Retail Trade). Décalage
  conservateur d'un mois calendaire complet (`DateOffset(months=1)`),
  même convention que M2/HOUST/CFNAI/UMCSENT (#195/#203/#205/#206/#283).
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `RetailGrowth(t-1)` est dans son tercile expanding le
  PLUS BAS (consommation la plus faible observée jusqu'à présent —
  direction cohérente avec #203/#204/#206/#283/#294), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_retail_sales_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#294), vérification dédiée du décalage d'un mois, anti-
lookahead par troncature. Sortie :
`results/nonml_retail_sales_overlay_result.md`.
