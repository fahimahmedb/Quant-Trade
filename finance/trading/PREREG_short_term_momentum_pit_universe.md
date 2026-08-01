# Pré-enregistrement — Cycle #164 : le #14 (momentum court terme « Winners ») sur l'univers POINT-IN-TIME réel

**Committé AVANT tout calcul.** Cycle #164 du backlog non-ML, application
directe de l'infrastructure construite au cycle #163.

## Contexte

Le #14 (`PREREG_short_term_momentum.md`,
`results/nonml_short_term_momentum_result.md`) est le résultat brut le plus
spectaculaire du backlog : Sharpe **+2,35** contre +0,63 pour la référence,
rendement **+1813 %** contre +87 %, sur 1391 séances (2021-01-11 →
2026-07-27). Il est flaggé **« prudence forte »** dans le backlog depuis sa
création, avec deux motifs explicitement énoncés à l'époque :

1. la fenêtre 2021-2026 est un marché haussier très concentré (IA /
   semi-conducteurs), potentiellement non généralisable ;
2. l'univers utilisé est la liste des membres du NDX-100 **de 2026**
   appliquée rétroactivement — le cycle #163 a mesuré que cette liste ne
   couvre que **68 % des vrais membres de l'indice en 2022** et 42 % en
   2015, les absents étant par construction des titres sortis de l'indice
   depuis, donc en moyenne des sous-performants.

Le motif 2 est particulièrement inquiétant **pour ce mécanisme précis** :
sélectionner chaque semaine le tercile des plus fortes hausses récentes
dans un univers composé uniquement de titres dont on sait *a posteriori*
qu'ils sont restés dans l'indice jusqu'en 2026 est très proche d'une
tautologie. Le cycle #163 a montré que l'edge du #38 survivait à la
correction ; rien ne garantit qu'il en aille de même ici, et le #14 est
justement le candidat pour lequel le risque est le plus élevé.

## Correction retenue (fixée ici, avant tout calcul)

Exactement la même que le #163, appliquée au mécanisme du #14 :

- **Univers point-in-time** : à chaque date de rebalancement (hebdomadaire),
  seuls les titres **réellement membres du NDX-100 ce jour-là** sont
  éligibles. Source : composition `nasdaq-100-ticker-history` v2026.7.0
  (MIT) vendorée dans `data/ndx100_history/`, rechargée par
  `scripts/ndx100_membership.py` (portage vérifié au cycle #163).
- **La référence subit exactement le même traitement** : le « Buy & Hold
  équipondéré (univers) » devient l'équipondéré des **membres réels** de
  l'indice à chaque date, et non plus des 99 titres de la liste de 2026.
  C'est une correction qui joue **contre** le candidat (la référence
  devient plus réaliste, donc probablement plus faible, mais l'univers du
  candidat s'appauvrit aussi de ses futurs gagnants garantis).
- **Fenêtre** : 2015-01-01 → fin des prix (≈ 2026-07-27), imposée par le
  début de couverture de la source de composition. Panneau de prix
  `data/pead/prices_pit/` (178 séries sur les 214 tickers ayant appartenu
  à l'indice ; 36 titres retirés de la cote restent indisponibles — biais
  résiduel déjà quantifié au #163 et re-quantifié ici).
- Panneau tronqué à **2014-01-01** pour le calcul (le signal ne demande que
  5 séances d'historique ; marge très large, sans effet sur aucune quantité
  évaluée à partir de 2015-01-01). Grille de rebalancement ancrée à la
  première séance ≥ 2015-01-01.

## Ce qui ne change PAS (aucun retuning)

`SIGNAL_WINDOW = 5`, `REBAL_EVERY = 5`, `TERCILE = 1/3` (tercile
**supérieur**), `COST_BPS = 5.0`. Aucune grille, aucune variante, aucun
second essai.

Comme au #163, le tercile est calculé sur le nombre de titres **réellement
investissables à la date de rebalancement** et non sur le nombre de
colonnes du panneau (178) — sans quoi la formule d'origine sélectionnerait
~59 titres, soit les deux tiers de l'univers réel, et ne serait plus le
mécanisme du #14. TERCILE reste 1/3.

## Critère de succès (identique au #14, règle renforcée)

**Sharpe annualisé du portefeuille Winners > Sharpe de la référence ET
rendement total net > rendement de la référence**, sur la fenêtre
point-in-time. `n_trials = 1` pour ce cycle.

Ce cycle ne lance PAS la batterie Règle 9 : le #14 n'a jamais passé cette
barre et l'objet du cycle est de savoir si son PASS de niveau 1 survit à la
correction d'univers. Si — et seulement si — il survit, la batterie Règle 9
deviendra la suite logique, comme cycle distinct et pré-enregistré à part.

## Hypothèse testée, et comment elle peut être réfutée

Hypothèse : le PASS du #14 survit à la correction du biais du survivant,
comme celui du #38 au cycle #163.

Réfutations possibles, toutes à rapporter telles quelles :

- **Le PASS disparaît** (Sharpe ou rendement passe sous la référence) → le
  #14 était en grande partie un artefact de survivorship, et le flag
  « prudence forte » doit devenir un **FAIL** reclassé. Ce serait le
  résultat le plus important du cycle, et le plus utile.
- **Le PASS tient mais l'edge s'effondre** (par ex. Sharpe +2,35 → +0,9) →
  le mécanisme existe mais son ampleur était très surestimée ; le flag
  « prudence forte » reste, avec un chiffre honnête à la place.
- **Le PASS tient avec un edge comparable** → le #14 est confirmé sur un
  univers défendable et sur un échantillon 2× plus long.

Aucun de ces cas ne déclenchera un second essai avec d'autres paramètres.

## Anti-cheat

Ce fichier est committé **avant** toute exécution. Vérification
automatisée : `python3 scripts/nonml_anti_cheat_check.py
short_term_momentum_pit_universe`. Les données de prix et de composition
sont celles déjà committées au cycle #163 — aucun nouveau fetch.
