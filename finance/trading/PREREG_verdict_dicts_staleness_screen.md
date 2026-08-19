# Pré-enregistrement — le défaut périmé du #485 est-il isolé, ou se retrouve-t-il ailleurs ?

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global. **Cycle de VÉRIFICATION** (pas de réparation), deuxième piste de
la file ouverte au #521.

## Ce que le #521 propose sans le cadrer

Le #520/#521 ont réparé un dictionnaire `V` de verdicts écrits à la main
(`nonml_irreparable_figures_census_backtest.py`, #485) qui n'avait
jamais suivi 4 cycles de corrections ultérieures. Le #521 suggérait,
sans le cadrer : « prochain candidat de réparation à identifier par un
balayage similaire sur d'autres scripts source-de-vérité ». **Ce cycle
cadre la question avant d'y répondre.**

## La population — 4 autres dictionnaires `V`, nommés et datés

Recensés par `grep -l "^V = {"` sur `scripts/*.py`, hors le script du
#485 déjà réparé :

| Script | Cycle d'origine | Effectif de `V` |
|---|---|---|
| `nonml_hardcoded_figures_remainder_backtest.py` | #479 | **61** |
| `nonml_guards_witness_remainder_backtest.py` | #484 | **23** |
| `nonml_guards_without_witness_backtest.py` | #481 | **14** |
| `nonml_orphan_audits_declared_reading_backtest.py` | #483 | **10** |

**108 entrées au total.** Une vérification manuelle exhaustive de
chacune, à la façon des #493/#511/#518, serait un projet à plusieurs
cycles — **hors de portée d'un seul cycle**. Ce cycle fait donc un
**écran mécanique déclaré faible d'avance** (même discipline que le
proxy du #485 lui-même), pas une vérification complète.

## Le protocole — un écran, pas un verdict

Pour chaque script cible nommé dans l'un des 4 dictionnaires, recherche
textuelle dans `NONML_STRATEGY_BACKLOG.md` :

1. **Toute section `## Backlog #N`** avec `N` **postérieur** au cycle
   d'origine du dictionnaire qui le contient ;
2. **contenant le nom du script cible** ;
3. **ET l'un des marqueurs** : `corrigé au #`, `verdict tombe`,
   `périmé`, `FAUSSE`, `contredit`, `réfuté`.

Un script qui satisfait les trois est un **candidat** — pas une
confirmation. **Aucun candidat ne sera classé IRRÉPARABLE/RÉPARABLE
faux dans ce cycle** : le screen ne fait que signaler où chercher.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **4** dictionnaires nommés, effectif et cycle d'origine publiés.
2. **108/108** noms de script passés à l'écran mécanique.
3. Chaque candidat trouvé **nommé avec la section source qui le
   contredit**, verbatim.
4. **Le screen est explicitement déclaré faible** : il ne peut ni
   confirmer une staleness (faux positif possible : mention du nom sans
   rapport avec son verdict) ni l'exclure (faux négatif possible : une
   contradiction jamais écrite avec ces mots-clés précis).
5. Si des candidats existent, ils sont **ajoutés à la file « à faire »**
   pour un cycle de vérification dédié — pas résolus ici.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 1** candidat trouvé — le défaut du #485 n'est probablement pas
   unique dans un dépôt de plus de 320 scripts.
2. Le dictionnaire le plus ancien (`hardcoded_figures_remainder`, #479,
   61 entrées) produit **proportionnellement plus** de candidats que les
   3 autres réunis, simplement parce qu'il a eu plus de cycles pour
   accumuler des contradictions.
3. **Aucun** candidat ne provient de `orphan_audits_declared_reading`
   (#483, 10 entrées) — c'est un cycle de **ratification**, pas de
   classification originale (déclaré dans son propre docstring), donc
   moins susceptible d'être contredit par construction.

## Ce que ce cycle ne fait pas

- Il ne **répare** ni ne **rejuge** aucun verdict des 4 dictionnaires.
- Il ne **vérifie pas manuellement** chacune des 108 entrées — seul un
  écran mécanique, explicitement faible, est appliqué.
- Il n'**exécute** aucun script de marché ni de dépôt.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification bibliographique, aucune position,
aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le nombre de candidats est
   nul ou très élevé.
2. Population et protocole **inchangés** après mesure.
3. **Chaque candidat cité avec la section source qui le contredit,
   jamais seulement compté.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
