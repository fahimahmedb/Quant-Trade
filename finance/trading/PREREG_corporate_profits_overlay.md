# Pré-enregistrement — Profits des entreprises US (FRED CP)

**Committé AVANT tout calcul.** Cycle #321 du backlog non-ML.

## Hypothèse

Les profits des entreprises après impôts (FRED `CP`, comptabilité nationale
NIPA, trimestrielle depuis 1947) mesurent directement la RENTABILITÉ
AGRÉGÉE réelle des entreprises US — un canal FONDAMENTAL jamais exploité
dans ce backlog. Tous les signaux macro-externes testés à ce jour
(taux/pente/inversion, spreads de crédit, conditions financières
composites, inflation, dollar, matières premières, immobilier, activité
économique réelle, endettement des ménages, marché du travail) mesurent
le STRESS DES MARCHÉS ou des CONDITIONS MACRO-FINANCIÈRES, jamais la
PROFITABILITÉ DES ENTREPRISES elles-mêmes — le déterminant fondamental
ultime de la valorisation actions. Une contraction ou une croissance
négative des profits en glissement annuel est documentée en finance
(concept de "earnings recession") comme précédant ou accompagnant
fréquemment les phases de faiblesse actions, indépendamment des
conditions de crédit ou de taux.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `CP` (gratuite, trimestrielle,
1947-2026, disponibilité confirmée par fetch de test le 06/08/2026,
`data/corporate_profits_quarterly.csv`). Réutilisation intégrale des
conventions déjà établies : glissement annuel en log (`YOY_QUARTERS=4`,
analogue à `YOY_MONTHS=12` du #203), `expanding_tercile_cut_low` (tercile
le plus BAS = défensif, réutilisé directement de `nonml_m2_growth_overlay_backtest.py`,
import direct, Règle 7), CUT=0,5x défensif, COST_BPS=5,0. Décalage de
publication d'UN TRIMESTRE (3 mois calendaires avant ffill+shift(1)),
même convention que les séries trimestrielles déjà testées (DRCCLACBS
#286, M2V #320) — les profits font partie de la publication du PIB,
estimée avance disponible ~1 mois après fin de trimestre mais souvent
révisée ; le délai de 3 mois est une marge conservatrice cohérente avec
le protocole déjà appliqué aux autres séries basées sur le PIB.

## Définition (fixée ici, AVANT tout calcul)

- `CPGrowth(t)` = `log(CP(t)/CP(t-4))` (glissement annuel, 4 trimestres).
- `GateProfits(t)` = 1 si `CPGrowth_lag(t-1)` (décalé de 3 mois calendaires
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus BAS
  (croissance des profits faible/négative = signal défavorable), sinon 0.
- **Position** : `CUT=0,5x` (design purement défensif, jamais de levier,
  réutilisé de toute la famille macro-externe) si `GateProfits(t)`,
  `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — profits en contraction = défensif — pas de
grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (#191/#195/#198/#199/#203/#286/#320...), le design purement
défensif sans amplification limite structurellement le gain de rendement
même si le signal identifie un vrai régime de risque (Sharpe amélioré
mais rendement insuffisant) — schéma déjà observé sur la majorité des
cycles de cette famille. Par ailleurs, la fréquence trimestrielle très
basse (comme #286/#320) pourrait limiter la robustesse et la
significativité statistique, indépendamment de la validité du signal.
Enfin, les profits agrégés NIPA incluent des ajustements comptables
(inventaires, dépréciation) qui peuvent diverger temporairement des
bénéfices par action réellement perçus par les marchés actions — limite
reconnue à l'avance, pas un argument a posteriori. Rapporté honnêtement
dans tous les cas, sans retuning.

## Idées additionnelles proposées ce cycle (non exécutées, ajoutées au backlog "à faire")

Recherche de conformité anti-doublon menée (grep systématique + fetch de
test HTTP 200) avant proposition, en plus de la CP :
- **Demandes continues d'allocations chômage** (FRED `CCSA`, hebdomadaire) :
  DISTINCT des demandes initiales déjà testées et FAIL (#204, ICSA) —
  les demandes initiales mesurent le FLUX de nouveaux licenciements
  (réactif), les demandes continues mesurent le STOCK de chômeurs
  encore indemnisés (persistance/durée du chômage, indicateur
  généralement plus retardataire mais économiquement distinct).
- **Nouvelles commandes de biens durables** (FRED `DGORDER`, mensuel) :
  mesure la DEMANDE manufacturière avancée (les entreprises commandent
  avant de produire), distinct de tous les signaux déjà testés — canal
  manufacturier jamais exploité (le PMI/ISM équivalent, `NAPM`, est
  indisponible sur FRED depuis 2015, cf. #204 note).
- Permis de construire (`PERMIT`) explicitement ÉCARTÉ : redondant avec
  le canal immobilier déjà clos à 0/2 (#283 HOUST activité, #294
  Case-Shiller valorisation) — pas de nouvelle hypothèse économique
  distincte à son sujet (Règle 2).

## Anti-cheat

Ce fichier committé avant tout fetch et tout calcul. Sortie :
`results/nonml_corporate_profits_overlay_result.md`.
