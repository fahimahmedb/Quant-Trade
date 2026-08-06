# Pré-enregistrement — Indice d'incertitude de politique économique US (FRED USEPUINDXD)

**Committé AVANT tout calcul.** Cycle #325 du backlog non-ML.

## Hypothèse

L'indice d'incertitude de politique économique US (FRED `USEPUINDXD`,
Baker-Bloom-Davis, QUOTIDIEN depuis 1985) est construit à partir de la
fréquence d'articles de presse mentionnant simultanément incertitude,
économie et politique — premier signal de ce backlog fondé sur
l'ANALYSE DE TEXTE/PRESSE plutôt que sur une donnée de marché, de
crédit ou une statistique économique officielle. Catégoriellement
distinct de tous les canaux déjà testés (taux, crédit, inflation,
dollar, matières premières, immobilier, activité réelle, endettement
des ménages, marché du travail, monétaire, fondamental entreprise). Une
hausse de l'incertitude de politique économique est documentée en
finance (Baker, Bloom & Davis 2016) comme précédant ou accompagnant des
phases de repli des marchés actions (chocs de politique commerciale,
crises budgétaires, incertitude électorale).

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `USEPUINDXD` (gratuite,
quotidienne, 1985-2026, disponibilité confirmée par fetch le
06/08/2026, `data/epu_daily.csv`, données quasi temps réel jusqu'au
05/08/2026). Réutilisation intégrale de deux conventions déjà établies
combinées : (a) le NIVEAU brut (pas une transformation en glissement/
variation) avec tercile expanding le plus HAUT, `expanding_tercile_cut_high`,
directement importée de `nonml_financial_conditions_overlay_backtest.py`
(#291, NFCI) — l'EPU est elle-même un indice construit pour être
interprété en niveau, comme le NFCI, BAA10Y (#199) ou STLFSI4 ; (b)
l'alignement causal `reindex(ffill)` + `shift(1)` SANS décalage
calendaire supplémentaire, déjà utilisé pour les séries quotidiennes
directement disponibles en temps quasi réel (VIX #130, pétrole WTI
#283, cuivre #284, dollar #198) — l'EPU étant publiée quotidiennement
par policyuncertainty.com/FRED avec un délai de traitement minime
(donnée disponible jusqu'à J-1 au moment du fetch). `CUT=0,5x`
défensif, `COST_BPS=5,0`, toutes constantes réutilisées.

## Définition (fixée ici, AVANT tout calcul)

- `GateEPU(t)` = 1 si `EPU_lag(t-1)` (décalée d'une séance via
  `reindex(ffill)`+`shift(1)`) est dans son tercile expanding le plus
  HAUT (incertitude de politique économique la plus élevée observée à
  ce jour), sinon 0.
- **Position** : `CUT=0,5x` si `GateEPU(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — incertitude élevée = défensif — pas de
grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée, le design purement défensif sans amplification limite
structurellement le gain de rendement même si le signal identifie un
vrai régime de risque (Sharpe amélioré mais rendement insuffisant) —
schéma dominant observé sur la quasi-totalité des cycles de cette
famille. Par ailleurs, l'EPU est documentée comme une série TRÈS
BRUITÉE jour à jour (elle dépend du volume d'articles publiés un jour
donné, avec des pics ponctuels autour d'événements médiatiques précis
plutôt qu'une évolution lisse d'un régime économique) — ce bruit élevé
pourrait dégrader la stabilité du signal indépendamment de sa validité
économique de fond. Rapporté honnêtement dans tous les cas, sans
retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de `data/epu_daily.csv`
est une simple vérification de disponibilité, aucun résultat n'existe
avant ce commit). Sortie : `results/nonml_epu_overlay_result.md`.
