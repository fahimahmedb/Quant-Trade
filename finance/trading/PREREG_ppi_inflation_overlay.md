# Pré-enregistrement — Inflation à la production US (FRED PPIACO)

**Committé AVANT tout calcul.** Cycle #337 du backlog non-ML.

## Hypothèse

L'indice des prix à la production US (FRED `PPIACO`, tous produits,
mensuel depuis 1913) mesure l'inflation au niveau AMONT de la chaîne
de valeur (prix de gros/producteur), distinct de l'inflation
CONSOMMATEUR (CPI, #338, PASS NET 5/5) — un choc de coûts intrants
(matières premières, énergie, composants) documenté comme précédant
potentiellement sa transmission au consommateur final (délai de
répercussion), et mesurant directement la pression sur les MARGES des
entreprises avant que celle-ci n'affecte les prix finaux. 2e variante
du canal inflation réalisée après le CPI, teste si le signal identifié
au #338 se généralise à l'étage amont de la chaîne de prix ou est
spécifique au niveau consommateur.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `PPIACO` (gratuite, mensuelle,
1913-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/ppi_monthly.csv`). Réutilisation INTÉGRALE et À L'IDENTIQUE de
la construction du #338 (CPI) : glissement annuel en log
(`YOY_MONTHS=12` du #203), `expanding_tercile_cut_high` (tercile le
plus HAUT = défensif, du #291 NFCI), `CUT=0,5x`, `COST_BPS=5,0`,
décalage de publication d'UN MOIS calendaire avant `ffill`+`shift(1)`
(le PPI est publié à la mi-mois suivant, même délai que le CPI —
même convention conservatrice que #195/#203/#323/#326/#338).

## Définition (fixée ici, AVANT tout calcul)

- `PPIGrowth(t)` = `log(PPIACO(t)/PPIACO(t-12))` (glissement annuel,
  12 mois).
- `GatePPI(t)` = 1 si `PPIGrowth_lag(t-1)` (décalé d'un mois calendaire
  avant `ffill`+`shift(1)`) est dans son tercile expanding le plus
  HAUT (inflation producteur la plus élevée observée à ce jour =
  défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GatePPI(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — inflation producteur élevée = défensif —
pas de grille).

## Risque déclaré à l'avance

**Prédiction explicite testable** : étant donné la construction
IDENTIQUE au #338 (CPI, PASS NET 5/5, plateau de robustesse parfait),
et la corrélation économique généralement élevée entre inflation
producteur et inflation consommateur (les deux séries co-évoluent
largement sur le même cycle macro), un résultat PASS similaire au
#338 est plausible — mais PAS garanti : le PPI est documenté comme
PLUS VOLATIL que le CPI (davantage exposé aux chocs de matières
premières/énergie, composante moins lissée que le panier de
consommation final), ce qui pourrait dégrader le rapport signal/bruit
du tercile expanding par rapport au CPI. Comme toujours, le design
purement défensif limite structurellement le gain de rendement. Un
résultat proche mais légèrement inférieur au #338, ou au contraire un
résultat FAIL malgré la construction identique (démontrant que le
niveau AMONT ne porte pas le même signal que le niveau AVAL), sont
tous deux plausibles et seront rapportés honnêtement, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/ppi_monthly.csv` est une simple vérification de disponibilité,
aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_ppi_inflation_overlay_result.md`.
