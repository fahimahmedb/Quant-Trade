# Pré-enregistrement — Positionnement spéculatif net CFTC sur l'or (COT, futures COMEX), overlay défensif

**Committé AVANT tout calcul.** Cycle #361 du backlog non-ML.

## 1. Contexte et hypothèse — 2e construction de la sous-famille "positionnement CFTC"

Suite directe du #360 (positionnement spéculatif net sur futures
NASDAQ-100, FAIL 2/5, 1re catégorie de mécanisme "positionnement"
testée dans ce backlog). Ce cycle teste la **2e construction** de
cette sous-famille naissante, sur une **classe d'actif sous-jacente
entièrement différente** : l'or (matière première refuge), pas un
indice actions.

**Distinction explicite avec le #360** : le NASDAQ-100 est un indice
actions (positionnement = pari directionnel sur la croissance/tech) ;
l'or est un actif refuge dont le positionnement spéculatif net est
l'un des signaux COT **les plus documentés et étudiés de la
littérature** ("Large Speculator Index" appliqué à l'or, cf. la
pratique COT popularisée par Larry Williams précisément sur ce
marché). **Même hypothèse contrariante et même direction que le #360**
(net-long extrême = trade "crowded" = risque de dénouement = défensif)
— **aucun changement de direction/interprétation entre les deux
cycles**, pour éviter tout risque de "tester plusieurs interprétations
jusqu'à ce qu'une fonctionne" (Règle anti-snooping).

**Distinction avec le momentum de l'or déjà testé (#348, FAIL 3/5,
famille valeur-refuge)** : le #348 testait le PRIX de l'or (ETF GLD,
momentum). Ce cycle teste le POSITIONNEMENT des spéculateurs sur les
futures or (COT) — même actif sous-jacent, mécanisme totalement
distinct (prix vs positionnement, déjà établi comme catégorie
mécanique différente au #360).

**Engagement de bornage explicite** : la sous-famille "positionnement
CFTC" sera bornée à **3 constructions maximum** (NASDAQ-100 #360 +
or ce cycle + au plus 1 autre actif sous-jacent structurellement
distinct, ex. pétrole ou taux, à trancher explicitement si retenue) —
aucune 4e ne sera testée sans hypothèse matériellement nouvelle,
conformément à la discipline déjà appliquée aux autres sous-méthodes.

## 2. Données

**Nouvelle donnée** : rapport COT "Legacy" combiné (futures seuls),
série `GOLD - COMMODITY EXCHANGE INC.` (contrat standard COMEX,
distinct de "MICRO GOLD" plus récent, non inclus — pas de
consolidation nécessaire, la dénomination est identique et continue
sur toute la période). **Historique nettement plus long que le #360**
: 1927 observations de 1986-01-15 à 2026-07-28 (40 ans), vérifié sur
41 fichiers annuels CFTC 1986-2026, aucun doublon, aucune valeur d'open
interest nulle ou négative.

**Limite reconnue à l'avance — fréquence de publication variable dans
le temps** : le rapport COT était publié **deux fois par mois environ
jusqu'au début des années 1990**, puis à fréquence croissante, pour
devenir **strictement hebdomadaire à partir de 2000** (confirmé sur
l'échantillon : écart médian entre observations = 7 jours, mais écarts
allant jusqu'à 18 jours dans les années 1986-1994). **Conséquence
directe** : le signal est structurellement plus "figé" (stale) dans
les années 1986-1994 que dans le reste de l'échantillon — accepté
comme caractéristique réelle de l'époque (pas un bug), mais déclaré à
l'avance comme risque de dilution de l'edge sur cette sous-période.

**Décalage de publication** : **délai conservateur de 10 jours
calendaires** (`PUBLICATION_LAG_DAYS=10`, DÉLIBÉRÉMENT plus large que
les 5 jours du #360) — la justification récente "vendredi 15h30 ET,
~3j après le mardi" ne peut pas être supposée valide sur 40 ans
d'historique administratif (délais d'acheminement/publication papier
probablement plus longs avant l'ère électronique) ; ce choix est pris
AVANT tout calcul de signal, sur la seule base de cette incertitude
documentée, pas après avoir vu un résultat. Puis alignement causal
quotidien standard `ffill+shift(1)` (Règle 7).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que le #360 et tout signal macro-externe/positionnement
appliqué uniformément comme jauge systémique.

## 4. Mécanisme (figé, IDENTIQUE au #360, PUREMENT DÉFENSIF, jamais de levier)

- Seuil : **tercile EXPANDING** de `net_pct_lag(t) = 100 × (NC_Long(t)
  − NC_Short(t)) / OpenInterest(t)`, sur le NIVEAU BRUT (construction
  réutilisée à l'identique du #360/#357/#291, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `net_pct_lag(t)` est dans son tercile expanding le PLUS HAUT
  (positionnement spéculatif net-long le plus extrême sur l'or =
  défensif, même direction contrariante que le #360). **Jamais de
  levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (même construction que le #360, un seul actif
sous-jacent nouveau, aucun balayage de direction/interprétation).

## 6. Prédiction déclarée à l'avance (Règle 2)

**FAIL anticipé, mais pas exclu** : le #360 (même mécanisme, actif
différent) a FAIL à 2/5. Historique 2,5× plus long ici (40 ans vs 16
ans) pourrait donner une meilleure puissance statistique au tercile
expanding, mais la fréquence de publication variable en début
d'échantillon (risque #7.1) pourrait au contraire diluer l'edge.
Résultat rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. **Fréquence de publication variable 1986-1994** (voir §2) — dilution
   potentielle de l'edge sur le début de l'échantillon.
2. **Délai de publication conservateur de 10j** (vs 5j au #360) réduit
   davantage la fraîcheur effective du signal.
3. Le lien entre positionnement spéculatif sur l'or et stress des
   indices actions n'est pas garanti ni instantané — l'or est un actif
   refuge, mais son positionnement spéculatif reflète d'abord des vues
   sur l'or lui-même (inflation, dollar, taux réels), pas nécessairement
   un stress actions généralisé — risque de transmission similaire à
   celui déjà documenté pour le pétrole (#359).
4. Le mécanisme contrariant identique au #360 a déjà FAIL 2/5 — rien
   ne garantit qu'un actif différent avec le même mécanisme généralise
   mieux (déjà observé : MOVE PASS puis OVX FAIL avec le même
   mécanisme de volatilité implicite).
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`data/gold_cot_positioning_weekly.csv` (déjà committé avec ce
PREREG — donnée brute, aucun calcul de signal dedans),
`scripts/nonml_gold_cot_positioning_overlay_backtest.py`,
`scripts/nonml_gold_cot_positioning_overlay_audit.py`,
`results/nonml_gold_cot_positioning_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
