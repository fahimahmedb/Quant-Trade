# Pré-enregistrement — Taux d'épargne des ménages US (FRED PSAVERT)

**Committé AVANT tout calcul.** Cycle #328 du backlog non-ML.

## Hypothèse

Le taux d'épargne personnel des ménages US (FRED `PSAVERT`, % du revenu
disponible, mensuel depuis 1959) mesure directement le COMPORTEMENT
D'ÉPARGNE/PRÉCAUTION des ménages — distinct de l'endettement des
ménages déjà testé et clos (#284-#289, délinquance sur prêts carte de
crédit/hypothécaire/auto, 3/3, épargne et endettement étant les deux
faces opposées du bilan des ménages, jamais testé sous cet angle). Une
HAUSSE marquée du taux d'épargne est documentée comme un comportement
de précaution typique en période d'incertitude économique — l'épisode
le plus spectaculaire de l'historique (pic à >30 % en 2020) a coïncidé
avec le choc COVID. Une épargne élevée/en hausse rapide signale un
ménage qui restreint sa consommation par prudence, ce qui peut à la
fois refléter et anticiper un ralentissement économique.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `PSAVERT` (gratuite,
mensuelle, 1959-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/savings_rate_monthly.csv`). Réutilisation intégrale de la
construction NIVEAU BRUT + tercile expanding le plus HAUT (comme NFCI
#291, BAA10Y #199) — le taux d'épargne étant déjà un ratio directement
interprétable en niveau (contrairement aux masses monétaires ou indices
qui nécessitent un glissement), pas de transformation en croissance
nécessaire. `expanding_tercile_cut_high` importée directement de
`nonml_financial_conditions_overlay_backtest.py` (Règle 7). `CUT=0,5x`
défensif, `COST_BPS=5,0`, décalage de publication d'UN MOIS calendaire
avant `ffill`+`shift(1)` (le taux d'épargne fait partie du rapport
"Personal Income and Outlays" du BEA, publié ~1 mois après la fin du
mois — même convention conservatrice que #195/#203/#323/#324).

## Définition (fixée ici, AVANT tout calcul)

- `GateSavings(t)` = 1 si `PSAVERT_lag(t-1)` (décalé d'un mois
  calendaire avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus HAUT (taux d'épargne le plus élevé observé à ce jour =
  comportement de précaution), sinon 0.
- **Position** : `CUT=0,5x` si `GateSavings(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — épargne élevée = défensif — pas de
grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (8 FAIL sur les 9 derniers cycles #320-#327, 1 seul PASS sur
toute la famille, #200 inflation breakeven), le design purement
défensif sans amplification limite structurellement le gain de
rendement même si le signal identifie un vrai régime de risque. Par
ailleurs, le taux d'épargne est directement mécaniquement lié au choc
COVID de 2020 (pic historique isolé et transitoire, retombé rapidement)
— un tercile expanding ancré sur cet épisode pourrait produire un
comportement dégénéré (porte jamais réactivée après ce pic isolé une
fois qu'il devient un point de référence historique extrême) plutôt
qu'un signal de régime réellement récurrent — limite reconnue à
l'avance, à vérifier explicitement par audit dédié plutôt que
supposée. Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/savings_rate_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_savings_rate_overlay_result.md`.
