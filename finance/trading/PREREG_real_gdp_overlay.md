# Pré-enregistrement — Croissance du PIB réel US (FRED GDPC1)

**Committé AVANT tout calcul.** Cycle #339 du backlog non-ML.

## Contexte et justification de réouverture explicite du canal "activité économique réelle"

Le canal "activité économique réelle" a été déclaré clos à 0/4
constructions (#206 CFNAI, #204 ICSA, #205 UMCSENT, #295 RSXFS — voir
narratif du #320). **Réouverture explicite et justifiée** ici, dans le
même esprit que la réouverture du canal marché du travail pour
#332/#337 : le PIB réel (FRED `GDPC1`, comptabilité nationale
trimestrielle, depuis 1947) n'est PAS une nouvelle variante du même
type que les 4 déjà testées — c'est la MESURE OFFICIELLE ET
COMPRÉHENSIVE de l'activité économique elle-même (la synthèse
comptable complète de la production), alors que les 4 constructions
déjà closes sont toutes des PROXYS PARTIELS : CFNAI est un indice
composite synthétique construit à partir de nombreuses séries
(approximation), ICSA est spécifique au marché du travail, UMCSENT
est une enquête de sentiment (perception, pas un fait comptable),
RSXFS ne couvre que la consommation (une composante du PIB, pas le
total). Le PIB réel est la série macro la plus canonique et la plus
citée de toute la littérature de cycle économique — sa découverte
tardive dans ce backlog (jamais testée malgré ~30 constructions
macro-externes cette session) constitue une lacune de couverture
authentique, dans la même veine que la découverte du CPI/PPI au
#336/#337.

## Hypothèse

Un ralentissement de la croissance du PIB réel (en glissement annuel)
est le signal de récession le plus canonique en macroéconomie —
documenté comme accompagnant ou précédant systématiquement les phases
de repli des marchés actions.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `GDPC1` (gratuite,
trimestrielle, 1947-2026, disponibilité confirmée par fetch le
06/08/2026, `data/real_gdp_quarterly.csv`). Réutilisation intégrale de
la construction trimestrielle déjà établie (#320 M2V, #321 profits
d'entreprise) : glissement annuel en log sur 4 trimestres
(`YOY_QUARTERS=4`), `expanding_tercile_cut_low` (tercile le plus BAS =
défensif — ralentissement de la croissance = défavorable, même
direction que #203/#321/#323/#326) importée directement de
`nonml_m2_growth_overlay_backtest.py` (Règle 7), `CUT=0,5x` défensif,
`COST_BPS=5,0`, décalage de publication de TROIS MOIS calendaires
avant `ffill`+`shift(1)` (le PIB fait l'objet d'une estimation avance
~1 mois après la fin du trimestre puis de révisions successives sur
plusieurs mois — même convention conservatrice que M2V #320/DRCCLACBS
#286/profits d'entreprise #321).

## Définition (fixée ici, AVANT tout calcul)

- `GDPGrowth(t)` = `log(GDPC1(t)/GDPC1(t-4))` (glissement annuel, 4
  trimestres).
- `GateGDP(t)` = 1 si `GDPGrowth_lag(t-1)` (décalé de 3 mois
  calendaires avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (croissance du PIB la plus faible observée à ce jour =
  défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateGDP(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — croissance PIB faible = défensif — pas
de grille).

## Risque déclaré à l'avance

**Prédiction NON tranchée à l'avance** : le succès inattendu du CPI
(#338, PASS NET 5/5) après la découverte d'une lacune de couverture
similaire encourage un optimisme prudent, mais rien ne garantit que ce
schéma se reproduise pour le PIB — les 4 proxys d'activité déjà
testés ont TOUS échoué (0/4), ce qui pourrait indiquer que le canal
"activité économique réelle" lui-même (quel que soit l'angle de
mesure) ne porte pas de signal exploitable pour ce protocole, y
compris via la mesure officielle. Par ailleurs, la fréquence
trimestrielle très basse (comme M2V #320, profits d'entreprise #321,
FAIL tous les deux) et le fort lissage saisonnier déjà appliqué aux
données GDPC1 (CVS-CVA) pourraient limiter la réactivité du signal.
Rapporté honnêtement dans tous les cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/real_gdp_quarterly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_real_gdp_overlay_result.md`.
