# Pré-enregistrement — les 2 dictionnaires d'origine (#476, #478) sont-ils stales ?

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION**, deuxième piste de la file
ouverte au #528 (« nouveau candidat de balayage »).

## Deux dictionnaires jamais couverts par le screen du #522

Le #522 avait recensé 4 dictionnaires `V = {` écrits à la main, tous
**descendants** de deux cycles plus anciens : `nonml_hardcoded_figures_
sweep_backtest.py` (#476, variable `VERDICTS`) et `nonml_conditional_
sections_sweep_backtest.py` (#478, variable `VERDICTS`) — noms de
variable différents (`VERDICTS`, pas `V`), **hors du motif de recherche
du #522** (`grep -l "^V = {"`). Ce sont les **cycles d'origine** des
deux familles déjà réparées (#524/#525 pour les gardes, #526-#528 pour
les chiffres en dur) : s'ils portent eux-mêmes une staleness, elle
n'aurait jamais été détectée par le screen précédent.

## La population — 10 entrées, 2 dictionnaires

| Dictionnaire | Cycle | Effectif |
|---|---|---|
| `nonml_hardcoded_figures_sweep_backtest.py` | #476 | **5** |
| `nonml_conditional_sections_sweep_backtest.py` | #478 | **5** |

## Un examen préliminaire, déclaré avant mesure

Un balayage mécanique du texte du backlog entier (motifs `rétracté`,
`FAUSSE`, `n'est pas un défaut`, `contredit`, `réfuté` à proximité de
chaque radical) trouve des occurrences pour 3 des 10 noms
(`protocol_inventory_audit`, `marker_emitted_by_scripts`,
`reproducibility_sample_backtest`), mais un examen de leur contexte
montre, dans les trois cas, une **collision de proximité** — le
marqueur appartient à une phrase sur un **autre sujet** dans la même
section (le décompte du #485, une prédiction distincte du #493, la
datation des `PREREG_` du #486) — **pas une contradiction du verdict
`VERDICTS` cité ici**. Ce cycle vérifie mécaniquement, avec le même
garde-fou anti-collision que le #528, plutôt que de se fier à cette
lecture.

## Le protocole — même forme qu'au #528

1. **Extraire par script** les 10 entrées des deux dictionnaires
   `VERDICTS`, verdict actuel inclus.
2. **Test de rétractation** : marqueur trouvé à proximité du radical
   exact, **le radical le plus proche du marqueur** (parmi tous les
   radicaux connus du dépôt, comme au #528) devant être celui-ci —
   sinon collision écartée.
3. **Test de cohérence** : pour toute occurrence retenue par le test 1,
   vérifier si le verdict qu'elle porte **contredit** ou **confirme**
   le verdict `VERDICTS` cité ici.
4. **Si contradiction confirmée** : corriger l'entrée, diff borné,
   citant la source.
5. **Si aucune contradiction** : publié comme tel — les deux
   dictionnaires d'origine sont **à jour**.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **10** entrées listées, verdict actuel cité.
2. Résultat du test de rétractation publié pour chacune.
3. Toute occurrence retenue confrontée au verdict, verdict de
   compatibilité publié.
4. Toute contradiction confirmée corrigée avec diff borné.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **0** contradiction confirmée — les trois occurrences préliminaires
   (protocol_inventory_audit, marker_emitted_by_scripts,
   reproducibility_sample_backtest) sont des collisions de proximité,
   pas des contradictions.
2. Les **10** entrées restent donc **inchangées**.
3. Les deux dictionnaires d'origine (#476, #478) sont déclarés **à
   jour**, aucune dette héritée non détectée par le #522.

## Ce que ce cycle ne fait pas

- Il ne **réexamine** aucun des 32 candidats déjà tranchés (#523-#528).
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification de dépôt, aucune position,
aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si une contradiction est
   trouvée là où aucune n'était attendue.
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code ou de texte citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
