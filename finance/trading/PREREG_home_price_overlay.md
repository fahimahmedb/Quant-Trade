# Pré-enregistrement — Indice des prix immobiliers Case-Shiller US (overlay défensif)

**Committé AVANT tout calcul.** Cycle #292 du backlog non-ML.

## Hypothèse

L'indice Case-Shiller US National Home Price Index (FRED `CSUSHPISA`,
mensuel) mesure la VALORISATION des logements existants — canal
économique distinct du #283 (mises en chantier HOUST, mesure
d'ACTIVITÉ/OFFRE de construction, FAIL). Une baisse des prix immobiliers
est documentée comme déclenchant un EFFET DE RICHESSE négatif sur la
consommation des ménages (perte de valeur du principal actif du
ménage américain moyen) et une dégradation de la valeur du collatéral
hypothécaire (resserrement du crédit disponible) — un canal
structurellement différent d'une baisse de l'activité de construction.

## Données

Série FRED `CSUSHPISA` récupérée le jour même
(`data/case_shiller_monthly.csv`, MENSUELLE, 1987-2026, 473
observations, gratuite).

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7
de la construction M2/HOUST/cuivre — indice de PRIX en croissance
nominale structurelle, nécessite une normalisation YoY, PAS un niveau
brut comme les indices de stress déjà stationnaires #199/#286/#291)

- `HomePriceGrowth(t) = log(CSUSHPISA(t) / CSUSHPISA(t-12))`
  (glissement annuel, fenêtre 12 mois réutilisée du #203/#283/#284).
- **Décalage de publication** : le Case-Shiller est publié avec un
  délai documenté de ~2 mois (l'indice du mois M est publié fin du
  mois M+2, S&P Dow Jones Indices). Décalage conservateur de 2 mois
  calendaires complets (`DateOffset(months=2)`) avant `ffill`,
  légèrement plus long que le délai d'1 mois des autres séries
  mensuelles de ce backlog (#195/#203/#204/#205/#206/#283/#284), délai
  spécifique déclaré ici avant tout calcul.
- Alignement causal final : `ffill` + `shift(1)` sur le calendrier
  boursier.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de
  levier) si `HomePriceGrowth(t-1)` est dans son tercile expanding le
  PLUS BAS (baisse des prix immobiliers la plus marquée observée
  jusqu'à présent — direction cohérente avec #203/#204/#206/#283,
  faiblesse économique = défensif), `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_home_price_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel avec `side="right"` (inclusif, méthode prouvée correcte au
#203/#283-#293), vérification dédiée du décalage de 2 mois, anti-
lookahead par troncature. Sortie :
`results/nonml_home_price_overlay_result.md`.
