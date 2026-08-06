# Pré-enregistrement — Durée hebdomadaire moyenne du travail, secteur manufacturier US (FRED AWHMAN)

**Committé AVANT tout calcul.** Cycle #330 du backlog non-ML.

## Hypothèse

La durée hebdomadaire moyenne du travail dans le secteur manufacturier
US (FRED `AWHMAN`, mensuelle depuis 1939) mesure la MARGE INTENSIVE de
l'emploi (heures travaillées par salarié en poste) — réouverture
EXPLICITE et JUSTIFIÉE du canal marché du travail, clos à 0/3 au #326
(ICSA #204, CCSA #322, PAYEMS #326, tous mesurant la marge EXTENSIVE :
flux de licenciements, stock de chômeurs, nombre total d'emplois).
L'AWHMAN est une composante historique de l'indice avancé du
Conference Board (LEI), documentée comme PLUS précoce que le niveau
d'emploi lui-même : les entreprises réduisent les heures de leurs
salariés existants AVANT de procéder à des licenciements (coût
d'ajustement plus faible), et les augmentent avant d'embaucher de
nouveaux salariés. Une baisse des heures travaillées est donc un
signal potentiellement avant-coureur d'un ralentissement de la demande
de main-d'œuvre, distinct dans son mécanisme économique des 3 variantes
déjà testées.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `AWHMAN` (gratuite, mensuelle,
1939-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/manufacturing_hours_monthly.csv`). Réutilisation intégrale de la
construction NIVEAU BRUT + tercile expanding le plus BAS (même famille
"bas = défavorable" que #203/#323/#326/#331 — l'AWHMAN étant déjà un
ratio directement interprétable en niveau, pas de transformation en
croissance nécessaire). `expanding_tercile_cut_low` importée
directement de `nonml_m2_growth_overlay_backtest.py` (Règle 7).
`CUT=0,5x` défensif, `COST_BPS=5,0`, décalage de publication d'UN MOIS
calendaire avant `ffill`+`shift(1)` (l'AWHMAN fait partie du même
rapport "Employment Situation" du BLS que PAYEMS #326, publié le
premier vendredi du mois suivant — même convention conservatrice).

## Définition (fixée ici, AVANT tout calcul)

- `GateHours(t)` = 1 si `AWHMAN_lag(t-1)` (décalé d'un mois calendaire
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus BAS
  (durée hebdomadaire la plus faible observée à ce jour = signal
  avant-coureur de ralentissement de la demande de main-d'œuvre),
  sinon 0.
- **Position** : `CUT=0,5x` si `GateHours(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — heures faibles = défensif — pas de
grille).

## Risque déclaré à l'avance

**Prédiction explicite testable** : bien que le mécanisme économique
soit distinct des 3 variantes du canal marché du travail déjà FAIL
(#204/#322/#326), la construction technique (niveau brut, tercile
expanding, décalage causal) est identique et s'inscrit dans une
famille macro-externe défensive qui a échoué sur 10 des 11 derniers
cycles (#320-#331, 1 seul PASS net sur toute la session, #200). Un
résultat FAIL reste donc plausible malgré la distinction économique
du mécanisme. Par ailleurs, l'AWHMAN est une série relativement peu
volatile et à bande étroite (33-42h historiquement), ce qui pourrait
soit produire un signal peu discriminant, soit au contraire un effet
de tendance séculaire (baisse structurelle de la durée du travail sur
très long terme documentée dans la littérature du travail) similaire
au risque déjà rencontré au #331 (TCU) — à vérifier explicitement par
audit dédié. Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/manufacturing_hours_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_manufacturing_hours_overlay_result.md`.
