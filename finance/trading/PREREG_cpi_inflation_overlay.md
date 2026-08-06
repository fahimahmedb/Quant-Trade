# Pré-enregistrement — Inflation réalisée US (FRED CPIAUCSL)

**Committé AVANT tout calcul.** Cycle #336 du backlog non-ML.

## Contexte et justification de non-redondance

Recherche complémentaire menée après le constat de saturation du
#335 : vérification directe (grep) que l'indice des prix à la
consommation (CPI, inflation RÉALISÉE) n'a **jamais** été testé dans
ce backlog, malgré son caractère canonique — seule l'inflation
ANTICIPÉE par le marché (breakeven, #200, seul PASS niveau 1
individuel de toute la famille macro-externe, T10YIE) a été testée à
ce jour. Ces deux séries mesurent des concepts DISTINCTS : le
breakeven reflète les ANTICIPATIONS du marché obligataire (un prix de
marché, forward-looking par construction), tandis que le CPI mesure
l'inflation EFFECTIVEMENT CONSTATÉE par le Bureau of Labor Statistics
(un fait statistique, backward-looking par nature, publié avec délai).
Un choc d'inflation réalisée peut avoir un effet distinct sur les
marchés actions (resserrement monétaire réactif de la Fed, compression
des marges) de celui des anticipations pures.

## Hypothèse

Une hausse marquée de l'inflation réalisée (CPI, glissement annuel) est
documentée comme un facteur de resserrement monétaire (la Fed réagit à
l'inflation constatée) et de compression des marges d'entreprise
(coûts intrants). Même direction défensive que le breakeven #200 (déjà
PASS) mais mesurée sur les FAITS plutôt que les anticipations de
marché.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `CPIAUCSL` (gratuite,
mensuelle, 1947-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/cpi_monthly.csv`). Réutilisation intégrale de la construction
mensuelle déjà établie (#203 M2 growth) : glissement annuel en log
(`YOY_MONTHS=12`), mais avec `expanding_tercile_cut_high` (tercile le
plus HAUT = défensif — inflation élevée est défavorable, DIRECTION
INVERSÉE par rapport au #203 qui utilise le tercile bas, cohérente
avec la direction déjà retenue pour le breakeven #200) importée
directement de `nonml_financial_conditions_overlay_backtest.py`
(Règle 7). `CUT=0,5x` défensif, `COST_BPS=5,0`, décalage de
publication d'UN MOIS calendaire avant `ffill`+`shift(1)` (le CPI est
publié à la mi-mois suivant — même convention conservatrice que
#195/#203/#323/#326).

## Définition (fixée ici, AVANT tout calcul)

- `CPIGrowth(t)` = `log(CPIAUCSL(t)/CPIAUCSL(t-12))` (glissement
  annuel, 12 mois).
- `GateCPI(t)` = 1 si `CPIGrowth_lag(t-1)` (décalé d'un mois calendaire
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus
  HAUT (inflation réalisée la plus élevée observée à ce jour =
  défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateCPI(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — inflation réalisée élevée = défensif —
pas de grille).

## Risque déclaré à l'avance

**Prédiction NON tranchée à l'avance** : contrairement au breakeven
(#200, PASS net), qui capture une composante anticipative/forward-
looking directement liée à la valorisation des actifs, le CPI mesure
un fait déjà constaté avec retard — il pourrait déjà être en grande
partie intégré dans les prix via les anticipations (donc redondant
avec l'information déjà capturée par #200), ou au contraire capturer
une dynamique distincte (chocs d'inflation surprise vs anticipations
lentes). Comme la quasi-totalité de la famille macro-externe
défensive (14 FAIL et 2 PASS sur ~27 constructions cette session), le
design purement défensif limite structurellement le gain de rendement
même en cas de signal valide. Rapporté honnêtement dans tous les cas,
sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/cpi_monthly.csv` est une simple vérification de disponibilité,
aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_cpi_inflation_overlay_result.md`.
