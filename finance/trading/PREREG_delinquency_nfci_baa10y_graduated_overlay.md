# Pré-enregistrement — Position graduée par nombre de votes (défaut carte + NFCI + BAA10Y)

**Committé AVANT tout calcul.** Cycle #301 du backlog non-ML.

## Hypothèse

Les trois constructions déjà testées sur ce trio de signaux (ET #296,
OU #298, majorité ≥2/3 #301) sont toutes des PORTES BINAIRES : la
position ne prend que deux valeurs (0,5x ou 1,0x), quel que soit le
nombre exact de signaux actifs au-delà du seuil. Ce cycle teste un
mécanisme structurellement différent : un **SIZING CONTINU**
proportionnel au nombre de votes actifs, sans seuil dur. L'hypothèse
est qu'une réponse graduée (0 vote → 1,0x, 1 vote → 0,83x, 2 votes →
0,67x, 3 votes → 0,5x) capture mieux l'INTENSITÉ du stress détecté
qu'un seuil binaire, qui traite un régime à 2 signaux actifs
identiquement à un régime à 3, alors que 3 signaux simultanés
représentent objectivement un stress plus sévère que 2.

## Adaptation technique : réutilisation stricte, Règle 7

Aucune nouvelle donnée, aucune modification des définitions déjà
validées et committées :
- `build_delinquency_series()` / `load_delinquency_lag()` du #286.
- `build_nfci_series()` / `load_nfci_lag()` du #291.
- `load_baa10y_lag()` du #199.
- `expanding_tercile_gate_high()` du #296, appliquée aux trois séries
  exactement comme au #301.

## Définition (fixée ici, AVANT tout calcul)

- `GateDelinq(t)`, `GateNFCI(t)`, `GateBAA10Y(t)` = identiques au #301
  (booléens, tercile expanding le plus haut de chaque série).
- `Votes(t) = GateDelinq(t) + GateNFCI(t) + GateBAA10Y(t)` ∈ {0,1,2,3}.
- **Position** : `position(t) = 1,0 − 0,5×Votes(t)/3` (0 vote → 1,0x,
  1 vote → 0,833x, 2 votes → 0,667x, 3 votes → 0,5x). Le plancher à
  0,5x (3/3 votes) est identique à CUT=0,5x déjà utilisé dans TOUTE la
  famille de portes défensives de ce backlog — aucun nouveau paramètre
  de risque introduit, seule la fonction reliant `Votes` à `position`
  change (linéaire au lieu d'un saut).

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.
Même fenêtre testable que le #301 (bornée par DRCCLACBS, 1991+).

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule fonction de sizing testée, pas de grille de pondérations).

## Risque déclaré à l'avance

Le sizing continu implique des changements de position à CHAQUE
transition de `Votes(t)` (4 niveaux possibles au lieu de 2), donc un
turnover potentiellement plus élevé que les portes binaires — un
risque de coûts de transaction cumulés plus importants est possible et
sera rapporté honnêtement si constaté. Par ailleurs, il est possible
que le résultat soit très proche de celui du #301 (majorité ≥2/3) si
les régimes à 1 ou 3 votes sont rares comparés au régime à 2 votes,
auquel cas le sizing continu n'apporterait rien de neuf — rapporté tel
quel, sans retuning de la fonction linéaire après observation.

## Anti-cheat

Ce fichier committé avant `nonml_delinquency_nfci_baa10y_graduated_overlay_backtest.py`.
Aucune nouvelle donnée. Sortie :
`results/nonml_delinquency_nfci_baa10y_graduated_overlay_result.md`.
