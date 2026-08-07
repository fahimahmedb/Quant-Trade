# Pré-enregistrement — Panel élargi à 6 signaux (+ CPI), vote majoritaire ≥5/6

**Committé AVANT tout calcul.** Cycle #365 du backlog non-ML.

## 1. Contexte et hypothèse

Suite directe de la famille de portes combinées macro-externes, dont
chaque extension a jusqu'ici maintenu ou amélioré la généralisation
(#296 ET-2→PASS NET, #301 majorité 2/3→PASS NET, #303 sizing continu
→PASS, #304 panel à 4 signaux majorité 3/4→**PASS NET, Règle 9 3/5**,
#363 panel à 5 signaux +MOVE majorité 4/5→**PASS NET, Règle 9 3/5 avec
stabilité parfaite 4/4, meilleur profil de la famille**).

**Nouvelle extension** : ajouter le **CPI** (#338, inflation réalisée
US, PASS NET 5/5, robustesse plateau parfait 15/15, l'un des deux
meilleurs profils niveau 1 de toute la campagne macro-externe avec le
#200) au panel déjà validé à 5 signaux (défaut carte #286, NFCI #291,
BAA10Y #199, corrélation NDX-DAX #193, MOVE #357). **Justification
économique** : le CPI ajoute une **6e dimension catégoriellement
distincte** — l'INFLATION RÉALISÉE (fait statistique constaté,
BLS) — alors qu'aucun des 5 signaux déjà présents ne mesure directement
la stabilité des prix (endettement des ménages, conditions
financières, crédit obligataire, contagion internationale, volatilité
implicite des taux). Économiquement non redondant : l'inflation peut
monter en régime de croissance forte (pas nécessairement un signal de
stress selon les 5 autres dimensions) ou signaler une crise de
stagflation — teste si cette 6e dimension, orthogonale aux 5
premières, continue la tendance de généralisation déjà observée.

**Note de bornage explicite (Règle anti-snooping)** : cette famille de
portes combinées compte désormais **6 constructions distinctes**
(#296 ET-2, #298 OU-2, #301 majorité-2/3, #303 graduée-3, #304
majorité-3/4, #363 majorité-4/5) et cette 7e serait la 2e extension
consécutive de signal après le #363. **Engagement pris à l'avance** :
si cette extension à 6 signaux réussit (PASS niveau 1), ce sera la
**DERNIÈRE extension de signal testée sur ce panel sans nouvelle
motivation utilisateur explicite** — la famille sera alors considérée
comme suffisamment explorée (rendements marginaux décroissants
attendus sur la Règle 9/DSR, qui restera structurellement hors
d'atteinte quel que soit le nombre de signaux ajoutés, comme démontré
par l'investigation Piste A/C).

## 2. Données

Aucune nouvelle donnée. Réutilisation STRICTE (Règle 7) de toutes les
fonctions déjà validées, sans aucune modification :
`build_delinquency_series`/`load_delinquency_lag` (#286),
`build_nfci_series`/`load_nfci_lag` (#291), `load_baa10y_lag` (#199),
`build_corr_series`/`load_corr_lag` (#193),
`load_move_series`/`load_move_lag` (#357),
`build_cpi_growth_series`/`load_cpi_growth_lag` (#338),
`expanding_tercile_gate_high` (générique, #296).

**Fenêtre testable** : **vérifié avant calcul, AUCUNE réduction
supplémentaire** — le CPI (`CPIAUCSL`, disponible depuis 1947) est
beaucoup plus ancien que le MOVE (2002), donc n'est PAS le facteur
contraignant. La fenêtre reste strictement identique au panel à 5
signaux : 5951 séances sur NDX, débutant le 13/11/2002.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que toute la famille de portes combinées.

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `Votes(t)` = nombre de signaux (0 à 6) dans leur tercile expanding
  le plus HAUT parmi {défaut carte, NFCI, BAA10Y, corrélation NDX-DAX,
  MOVE, CPI}, chacun calculé avec sa fonction/décalage de publication
  propre déjà validée (aucune modification).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `Votes(t) ≥ 5` (**convention "n-1 sur n" du panel, réutilisée à
  l'identique des #301 [2/3], #304 [3/4] et #363 [4/5]**), `1,0x`
  sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (extension mécanique d'un panel déjà validé, aucun
nouveau paramètre, aucun balayage de seuil de vote).

## 6. Prédiction déclarée à l'avance (Règle 2)

**PASS anticipé** (même raisonnement qu'au #363) : 5 extensions
consécutives ont toutes maintenu ou amélioré la généralisation au
niveau 1. Le CPI lui-même est l'un des deux PASS niveau 1 les plus
robustes de tout le backlog (plateau parfait 15/15). Résultat rapporté
tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le seuil `Votes≥5` est encore plus strict en proportion (83,3%)
   que `Votes≥4` (80%) — un temps d'activation mécaniquement plus
   faible pourrait réduire la protection effective.
2. Le CPI est un signal MENSUEL avec un décalage de publication d'un
   mois — moins réactif que les signaux hebdomadaires/quotidiens du
   panel (NFCI hebdo, MOVE quotidien) — pourrait diluer la réactivité
   du panel combiné en période de choc rapide.
3. Le CPI a déjà PASS seul avec un edge très large (rendement NDX
   +6599,5%→+12687,9%) — rien ne garantit qu'un signal déjà très fort
   individuellement ajoute une valeur marginale au panel une fois
   combiné avec un seuil de vote aussi strict (comme observé pour le
   MOVE seul, solide niveau 1 mais Règle 9 2/5).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_backtest.py`,
`scripts/nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_audit.py`,
`results/nonml_delinquency_nfci_baa10y_corr_move_cpi_majority_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
