# Pré-enregistrement — Prix du cuivre ("Dr. Copper", overlay défensif)

**Committé AVANT tout calcul.** Cycle #282 du backlog non-ML.

## Hypothèse

Le prix du cuivre (FRED `PCOPPUSDM`, mensuel) est documenté en analyse
macro comme un indicateur avancé de la demande industrielle mondiale
("Dr. Copper a un doctorat en économie") — le métal entre dans la
quasi-totalité des biens manufacturés, de la construction et des
infrastructures, ce qui en fait un baromètre de croissance globale
distinct de tout signal financier (taux, crédit, sentiment) déjà testé.
Premier signal de MATIÈRE PREMIÈRE de ce backlog — canal entièrement
distinct de tous les signaux déjà testés (taux #44/#134/#149/#175/#178/
#186/#187/#195, crédit #199, inflation #200/#202, dollar #198,
sentiment #205, activité composite #206, marché du travail #204, masse
monétaire #203, immobilier #283).

## Données

Série FRED `PCOPPUSDM` récupérée le jour même (`data/copper_monthly.csv`,
mensuelle, 1992-2026, 414 observations, gratuite). Limite déclarée à
l'avance : historique plus court que les autres séries macro de ce
backlog (démarre en 1992, contre 1959 pour HOUST/M2) — restreint
d'autant l'échantillon testable sur NDX (40 ans). Publication ~1 mois
après la fin du mois (prix de marché agrégé mensuellement par FRED) —
même décalage causal d'un mois que #195/#203/#283, Règle 7.

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- `CopperGrowth(t) = log(PCOPPUSDM(t) / PCOPPUSDM(t-12))` (glissement
  annuel, fenêtre 12 mois réutilisée du #203/#283).
- Alignement causal : décalage d'un mois calendaire (publication) puis
  `ffill` + `shift(1)` sur le calendrier boursier (même fonction que
  #195/#203/#283).
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `CopperGrowth(t-1)` est dans son tercile expanding le PLUS
  BAS (chute la plus marquée de la demande industrielle mondiale
  proxée par le cuivre — direction cohérente avec #203/#204/#206/#283,
  faiblesse économique = défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_copper_price_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode déjà prouvée correcte au
#203 et re-confirmée au #283 après correction d'un bug d'audit),
vérification dédiée du décalage d'un mois, anti-lookahead par
troncature. Sortie : `results/nonml_copper_price_overlay_result.md`.
