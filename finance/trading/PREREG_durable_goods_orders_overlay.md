# Pré-enregistrement — Nouvelles commandes de biens durables US (FRED DGORDER)

**Committé AVANT tout calcul.** Cycle #323 du backlog non-ML.

## Hypothèse

Les nouvelles commandes de biens durables (FRED `DGORDER`, mensuelle
depuis 1992) mesurent la DEMANDE MANUFACTURIÈRE AVANCÉE : les
entreprises passent commande avant de produire, ce qui en fait un
indicateur AVANT-COUREUR documenté du cycle industriel (contrairement
aux données de production qui constatent l'activité déjà réalisée).
Canal manufacturier jamais exploité dans ce backlog — l'équivalent
usuel (PMI/ISM manufacturier, série FRED `NAPM`) est indisponible
depuis le retrait de la licence ISM de FRED (constaté au #204). Une
contraction des commandes signale un ralentissement anticipé de la
production et de l'investissement des entreprises, documenté comme
précédant souvent les phases de faiblesse économique et actions.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `DGORDER` (gratuite, mensuelle,
1992-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/durable_goods_orders_monthly.csv`). Réutilisation intégrale de la
construction déjà établie pour les séries mensuelles de niveau/activité
(#203 M2 growth) : glissement annuel en log (`YOY_MONTHS=12`),
`expanding_tercile_cut_low` (tercile le plus BAS = défensif — une
contraction des commandes est un signal défavorable, même sens que la
contraction de M2), `CUT=0,5x` défensif, `COST_BPS=5,0`, décalage de
publication d'UN MOIS calendaire avant `ffill`+`shift(1)` (même
convention que #195/#203, les données manufacturières préliminaires du
Census Bureau sont publiées ~3-4 semaines après la fin du mois, la
marge d'un mois complet est conservatrice) — toutes les constantes et
la fonction de porte importées directement de
`nonml_m2_growth_overlay_backtest.py` (Règle 7), seule la série et la
transformation (biens durables au lieu de masse monétaire) changent.

## Définition (fixée ici, AVANT tout calcul)

- `DGOGrowth(t)` = `log(DGORDER(t)/DGORDER(t-12))` (glissement annuel,
  12 mois).
- `GateOrders(t)` = 1 si `DGOGrowth_lag(t-1)` (décalé d'un mois
  calendaire avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (contraction des commandes = défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateOrders(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — contraction des commandes = défensif —
pas de grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (#191/#195/#198/#199/#203/#320/#321/#322...), le design
purement défensif sans amplification limite structurellement le gain
de rendement même si le signal identifie un vrai régime de risque
(Sharpe amélioré mais rendement insuffisant) — schéma déjà observé sur
la quasi-totalité des cycles de cette famille, y compris sur les deux
cycles précédents (#321 profits d'entreprise, #322 chômage continu).
Par ailleurs, les commandes de biens durables sont documentées comme
une série VOLATILE d'un mois sur l'autre (dominée par les commandes
aéronautiques/défense de gros montants unitaires), ce qui peut
introduire du bruit dans le glissement annuel indépendamment de la
validité économique du signal — limite reconnue à l'avance, pas un
argument a posteriori. Rapporté honnêtement dans tous les cas, sans
retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/durable_goods_orders_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_durable_goods_orders_overlay_result.md`.
