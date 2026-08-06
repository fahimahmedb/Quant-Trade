# Pré-enregistrement — Offres d'emploi US (FRED JTSJOL, JOLTS)

**Committé AVANT tout calcul.** Cycle #335 du backlog non-ML.

## Hypothèse

Les offres d'emploi non pourvues US (FRED `JTSJOL`, enquête JOLTS,
mensuelle depuis 2000) mesurent la DEMANDE DE MAIN-D'ŒUVRE des
employeurs (postes vacants) — 5e variante du canal marché du travail,
mais CONCEPTUELLEMENT DISTINCTE des 4 variantes déjà testées et
toutes FAIL (#204 ICSA flux de licenciements, #322 CCSA stock de
chômeurs, #326 PAYEMS niveau d'emploi réalisé, #332 AWHMAN heures
travaillées) : ces 4 constructions mesurent toutes un aspect de
l'emploi RÉALISÉ (résultat déjà survenu côté offre de travail), alors
que JTSJOL mesure l'INTENTION D'EMBAUCHE des employeurs (demande de
travail non encore satisfaite, encore prospective) — un indicateur
avancé documenté du cycle d'embauche, généralement cité comme
précédant les variations effectives de l'emploi (les entreprises
publient des offres avant d'embaucher réellement). Une baisse des
offres d'emploi signale un ralentissement anticipé de la demande de
main-d'œuvre, potentiellement plus précoce que les signaux déjà
testés sur l'emploi réalisé.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `JTSJOL` (gratuite,
mensuelle, 2000-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/job_openings_monthly.csv`). Réutilisation intégrale de la
construction mensuelle déjà établie (#203 M2 growth, #323 DGORDER,
#326 PAYEMS) : glissement annuel en log (`YOY_MONTHS=12`),
`expanding_tercile_cut_low` (tercile le plus BAS = défensif — une
baisse des offres d'emploi est un signal défavorable), `CUT=0,5x`
défensif, `COST_BPS=5,0`. Décalage de publication de DEUX MOIS
calendaires avant `ffill`+`shift(1)` (l'enquête JOLTS est publiée
~5-6 semaines après la fin du mois de référence — délai plus long que
la moyenne des séries mensuelles déjà testées, même convention
conservatrice que le Case-Shiller #294 et la balance commerciale
#327) — toutes les constantes et la fonction de porte importées
directement de `nonml_m2_growth_overlay_backtest.py` (Règle 7), seule
la série et la transformation changent.

## Définition (fixée ici, AVANT tout calcul)

- `JOLGrowth(t)` = `log(JTSJOL(t)/JTSJOL(t-12))` (glissement annuel,
  12 mois).
- `GateOpenings(t)` = 1 si `JOLGrowth_lag(t-1)` (décalé de 2 mois
  calendaires avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (contraction des offres d'emploi = défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateOpenings(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — baisse des offres d'emploi = défensif —
pas de grille).

## Risque déclaré à l'avance

**Prédiction NON tranchée à l'avance** (contrairement aux cycles
récents du canal marché du travail où un FAIL était systématiquement
anticipé) : ce signal étant conceptuellement distinct (demande
prospective vs offre réalisée), son issue n'est pas présumée suivre le
même schéma que les 4 variantes précédentes. Cela dit, comme la
quasi-totalité de la famille macro-externe défensive déjà testée (13
FAIL et 2 PASS sur ~25 constructions cette session), le design
purement défensif sans amplification limite structurellement le gain
de rendement même si le signal identifie un vrai régime de risque.
L'historique JTSJOL (2000+) est plus court que la plupart des autres
séries testées, ce qui tronquera l'échantillon testable sur NDX (40
ans) — signalé à l'avance, pas un argument a posteriori. Rapporté
honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/job_openings_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_job_openings_overlay_result.md`.
