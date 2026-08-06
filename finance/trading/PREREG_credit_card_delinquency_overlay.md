# Pré-enregistrement — Taux de défaut cartes de crédit US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #284 du backlog non-ML.

## Hypothèse

Le taux de défaut de paiement sur cartes de crédit (FRED `DRCCLACBS`,
trimestriel, "Delinquency Rate on Credit Card Loans, All Commercial
Banks") mesure la DÉTRESSE FINANCIÈRE RÉELLE des ménages (défauts de
paiement effectifs), distincte du sentiment PERÇU déjà testé (#205
UMCSENT, enquête d'opinion sur la confiance) et de l'activité composite
(#206 CFNAI, agrégat de production/emploi/consommation, pas de mesure
directe de stress d'endettement). Premier signal de STRESS
D'ENDETTEMENT DES MÉNAGES de ce backlog — canal microéconomique
(comportement de remboursement) plutôt que macro-agrégé.

## Données

Série FRED `DRCCLACBS` récupérée le jour même
(`data/credit_card_delinquency_quarterly.csv`, TRIMESTRIELLE,
1991-2026, 141 observations, gratuite). Limite déclarée à l'avance :
fréquence trimestrielle, la plus BASSE de ce backlog (contre mensuel
pour M2/CFNAI/UMCSENT/HOUST/cuivre, quotidien pour taux/VIX/dollar/
pétrole) — le signal se met à jour au maximum 4 fois par an.

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- **Construction** : NIVEAU brut du taux de défaut (pas une croissance/
  variation), même convention que le spread de crédit BAA10Y (#199) —
  un taux de défaut est déjà une mesure de stress en unités naturelles
  (%), pas une quantité nécessitant une normalisation par croissance
  comme M2/HOUST/cuivre.
- **Décalage de publication** : la Fed publie ces données bancaires
  agrégées avec un délai typique de 2-3 mois après la fin du trimestre.
  Décalage conservateur d'un trimestre calendaire complet (3 mois,
  `DateOffset(months=3)`) avant `ffill`, extension proportionnelle du
  principe déjà appliqué aux séries mensuelles (1 mois, #195/#203/#204/
  #205/#206/#283) à une fréquence trimestrielle.
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier (même fonction que le reste de la famille).
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `DRCCLACBS_lag(t-1)` est dans son tercile expanding le
  PLUS HAUT (défauts de paiement les plus élevés observés jusqu'à
  présent — direction cohérente avec #199 spread de crédit, stress
  financier = défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant
`nonml_credit_card_delinquency_overlay_backtest.py`. Vérification
prévue : recalcul indépendant par boucle+searchsorted manuel avec
`side="right"` (inclusif, méthode prouvée correcte au #203/#283/#284/
#285), vérification dédiée du décalage d'un trimestre, anti-lookahead
par troncature. Sortie :
`results/nonml_credit_card_delinquency_overlay_result.md`.
