# Pré-enregistrement — Croissance des prêts commerciaux et industriels US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #294 du backlog non-ML.

## Hypothèse

La croissance des prêts commerciaux et industriels (FRED `BUSLOANS`,
mensuel, Réserve Fédérale) mesure la DISPONIBILITÉ DU CRÉDIT BANCAIRE
AUX ENTREPRISES — un ralentissement ou une contraction de cet
agrégat est le signal classique d'un "credit crunch" (resserrement du
crédit bancaire, indépendant du prix du risque observé sur les marchés
obligataires). Canal DISTINCT de tous les signaux de crédit déjà
testés dans ce backlog : le spread de crédit BAA10Y (#199) mesure le
PRIX du risque de crédit fixé par le MARCHÉ obligataire, les taux de
défaut de consommation (#286/#288/#289) mesurent le COMPORTEMENT DE
REMBOURSEMENT des ménages — ici la variable est la VOLONTÉ DES BANQUES
DE PRÊTER aux entreprises, un canal d'offre de crédit bancaire jamais
exploité dans ce backlog.

## Données

Série FRED `BUSLOANS` récupérée le jour même
(`data/business_loans_monthly.csv`, MENSUELLE, 1947-2026, 954
observations, gratuite — l'historique le plus long de toute série
utilisée dans ce backlog).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
STRICTE de la construction M2/HOUST/cuivre/Case-Shiller/ventes au
détail — indice nominal en croissance structurelle, nécessite une
normalisation YoY)

- `BusLoanGrowth(t) = log(BUSLOANS(t) / BUSLOANS(t-12))` (glissement
  annuel, fenêtre 12 mois réutilisée du #203/#283/#284/#294/#295).
- **Décalage de publication** : délai conservateur d'un mois calendaire
  complet (`DateOffset(months=1)`), même convention que M2/HOUST/CFNAI/
  UMCSENT/ventes au détail (#195/#203/#205/#206/#283/#295).
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `BusLoanGrowth(t-1)` est dans son tercile expanding le
  PLUS BAS (croissance du crédit bancaire aux entreprises la plus
  faible observée jusqu'à présent — direction cohérente avec
  #203/#204/#206/#283/#294/#295, faiblesse économique = défensif),
  `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_business_loans_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#295), vérification dédiée du décalage d'un mois, anti-
lookahead par troncature. Sortie :
`results/nonml_business_loans_overlay_result.md`.
