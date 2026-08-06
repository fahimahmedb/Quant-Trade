# Pré-enregistrement — Taux d'utilisation des capacités industrielles US (FRED TCU)

**Committé AVANT tout calcul.** Cycle #329 du backlog non-ML.

## Hypothèse

Le taux d'utilisation des capacités industrielles US (FRED `TCU`, % de
la capacité de production totale effectivement utilisée, mensuel
depuis 1967) mesure directement le SLACK INDUSTRIEL de l'économie —
premier canal de ce type jamais exploité dans ce backlog, distinct des
commandes de biens durables (#323, mesure la DEMANDE future anticipée,
FAIL) et des profits d'entreprise (#321, mesure la RENTABILITÉ, FAIL).
Un taux d'utilisation FAIBLE ou en baisse signale un excès de capacité
de production inutilisée relativement à la demande — un indicateur
classique et largement suivi du cycle industriel, souvent cité comme
proche coïncident/légèrement avant-coureur des phases de faiblesse
économique (contrairement aux commandes, plus prospectives).

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `TCU` (gratuite, mensuelle,
1967-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/capacity_utilization_monthly.csv`). Réutilisation intégrale de la
construction NIVEAU BRUT + tercile expanding le plus BAS (même famille
"bas = défavorable" que #203 M2 growth, #323 DGORDER, #326 PAYEMS,
#329 balance commerciale — le TCU étant déjà un ratio directement
interprétable en niveau, pas de transformation en croissance
nécessaire, même logique que #329). `expanding_tercile_cut_low`
importée directement de `nonml_m2_growth_overlay_backtest.py` (Règle
7). `CUT=0,5x` défensif, `COST_BPS=5,0`, décalage de publication d'UN
MOIS calendaire avant `ffill`+`shift(1)` (le TCU fait partie du
rapport G.17 de la Fed, publié ~2 semaines après la fin du mois — la
marge d'un mois complet est conservatrice, même convention que
#195/#203/#323/#324/#328).

## Définition (fixée ici, AVANT tout calcul)

- `GateCapacity(t)` = 1 si `TCU_lag(t-1)` (décalé d'un mois calendaire
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus BAS
  (taux d'utilisation le plus faible observé à ce jour = slack
  industriel élevé = défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateCapacity(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — utilisation faible = défensif — pas de
grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (9 FAIL consécutifs #320-#328, 1 seul PASS net sur toute la
famille, #200), le design purement défensif sans amplification limite
structurellement le gain de rendement même si le signal identifie un
vrai régime de risque. Par ailleurs, le TCU est documenté comme
présentant une TENDANCE BAISSIÈRE SÉCULAIRE de long terme aux US
(désindustrialisation relative depuis les années 1960-1980, l'économie
étant passée d'une base manufacturière à une base plus orientée
services) — un seuil expanding pourrait s'ancrer sur les valeurs
élevées historiques (années 1960-1970) et rester ensuite quasi
inatteignable par les données récentes structurellement plus basses,
symétrique au risque de tendance déjà rencontré au #327 (balance
commerciale) et #328 (taux d'épargne) — à vérifier explicitement par
audit dédié plutôt que supposé. Rapporté honnêtement dans tous les
cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/capacity_utilization_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_capacity_utilization_overlay_result.md`.
