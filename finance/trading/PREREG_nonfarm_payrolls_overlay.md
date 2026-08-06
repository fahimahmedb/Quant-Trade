# Pré-enregistrement — Emplois non-agricoles US (FRED PAYEMS)

**Committé AVANT tout calcul.** Cycle #324 du backlog non-ML.

## Hypothèse

Les emplois non-agricoles totaux (FRED `PAYEMS`, enquête établissement
BLS, mensuelle depuis 1939) mesurent directement le NIVEAU d'emploi
dans l'économie US — 3e variante du canal marché du travail après les
demandes d'allocations chômage déjà testées et FAIL (#204 `ICSA`, flux
de nouveaux licenciements ; #322 `CCSA`, stock de chômeurs indemnisés).
PAYEMS est méthodologiquement DISTINCT des deux précédents : c'est une
enquête ÉTABLISSEMENT (comptage direct des emplois salariés déclarés
par les employeurs) plutôt qu'une donnée ADMINISTRATIVE dérivée des
demandes d'allocations (dépôts UI auprès des agences d'État), et
mesure le NIVEAU total d'emploi plutôt qu'un flux ou un stock de
chômage. Une contraction de l'emploi total (croissance négative en
glissement annuel, ou a fortiori une baisse absolue mensuelle) est
l'un des signaux de récession les plus documentés et les plus suivis
par les marchés ("NFP" est la publication macro la plus surveillée du
calendrier US).

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `PAYEMS` (gratuite, mensuelle,
1939-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/nonfarm_payrolls_monthly.csv`). Réutilisation intégrale de la
construction mensuelle déjà établie (#203 M2 growth, #323 DGORDER) :
glissement annuel en log (`YOY_MONTHS=12`), `expanding_tercile_cut_low`
(tercile le plus BAS = défensif — une contraction/ralentissement de
l'emploi est un signal défavorable), `CUT=0,5x` défensif,
`COST_BPS=5,0`, décalage de publication d'UN MOIS calendaire avant
`ffill`+`shift(1)` (même convention conservatrice que #195/#203/#323 —
le rapport NFP du mois M est en réalité publié le premier vendredi du
mois M+1, la marge d'un mois complet est conservatrice) — toutes les
constantes et la fonction de porte importées directement de
`nonml_m2_growth_overlay_backtest.py` (Règle 7), seule la série et la
transformation changent.

## Définition (fixée ici, AVANT tout calcul)

- `PayrollsGrowth(t)` = `log(PAYEMS(t)/PAYEMS(t-12))` (glissement
  annuel, 12 mois).
- `GatePayrolls(t)` = 1 si `PayrollsGrowth_lag(t-1)` (décalé d'un mois
  calendaire avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (ralentissement/contraction de l'emploi = défavorable),
  sinon 0.
- **Position** : `CUT=0,5x` si `GatePayrolls(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — ralentissement de l'emploi = défensif —
pas de grille).

## Risque déclaré à l'avance

**Prédiction explicite testable** : comme pour les deux variantes
précédentes du canal marché du travail (#204 ICSA FAIL net, #322 CCSA
FAIL 1/5), et conformément au schéma dominant de toute la famille
macro-externe défensive (Sharpe/MDD parfois améliorés, rendement
structurellement insuffisant faute d'amplification), un résultat FAIL
est plausible. Par ailleurs, PAYEMS en glissement annuel est une série
TRÈS LISSE (la croissance de l'emploi total change lentement, contrairement
aux séries plus réactives déjà testées) — cela pourrait soit réduire le
bruit (avantage), soit réduire la réactivité du signal aux points de
retournement (désavantage), effet non tranché à l'avance. Rapporté
honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/nonfarm_payrolls_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_nonfarm_payrolls_overlay_result.md`.
