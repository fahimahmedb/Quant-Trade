# Pré-enregistrement — régénérer les six rapports laissés en écart au #449

**Écrit et committé AVANT toute régénération et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, sixième après les #445 → #449.

## La dette, créée sciemment et inscrite

Le #449 a converti six scripts à la règle de verdict du #448 **sans régénérer
leurs rapports**. C'était délibéré et déclaré : régénérer six rapports d'un coup
aurait mélangé l'effet de la règle et la **dérive du dépôt**, alors que le #445
avait montré que **9 lignes sur 10** d'un rapport régénéré ne venaient pas de la
modification.

Le prix en était un écart **réel** entre le code corrigé et les rapports
publiés. Ce cycle le résorbe.

## Les six, et la méthode — un par un

| Script |
|---|
| `nonml_capitulation_gate_floor_sweep_backtest.py` |
| `nonml_empty_pass_basket_extension_backtest.py` |
| `nonml_empty_pass_requalification_backtest.py` |
| `nonml_pnl_persistence_lot4_audit.py` |
| `nonml_protocol_inventory_backtest.py` |
| `nonml_sameday_timestamp_resolution_backtest.py` |

Pour **chacun**, séparément :

1. **Baseline épinglée** — le contenu de son rapport au **dernier commit l'ayant
   touché avant ce cycle**, résolu par `git log -1 -- <rapport>`. Lire le disque
   rendrait la mesure dépendante de l'ordre d'exécution ; le #445 s'y était
   déjà fait prendre.
2. **Régénération** par exécution du script.
3. **Diff réel** (`SequenceMatcher`, pas une comparaison par position — le #446
   a montré qu'une insertion décale tout et fabrique 44 fausses divergences).
4. **Attribution de chaque groupe de diff** : *effet de la règle* ou *dérive du
   dépôt*, par **groupe contigu** et non ligne à ligne (leçon du #446).

## Ce qui rend l'attribution possible ici

L'effet de la règle est **prédictible et vérifiable** : le #449 a publié les
**5 rapports** dont la classe change. Une ligne de diff est donc imputable à la
règle si elle mentionne l'un de ces cinq noms ou un compte de verdict ; tout le
reste est de la dérive.

**Cette règle d'attribution est déclarée ici, avant de voir un seul diff.**

## Critère de succès — chiffré, et il peut échouer

1. **6/6** rapports régénérés, ou tout échec **publié avec sa raison** (script
   qui plante, dépendance manquante, durée excessive).
2. **Chaque groupe de diff attribué** — effet ou dérive. Aucun changement
   inexpliqué.
3. **Aucun verdict de stratégie modifié.** Ces six scripts sont des
   diagnostics et des inventaires ; s'ils changeaient le verdict d'une
   **stratégie**, ce serait un effet de bord non désiré, et le cycle échouerait.
4. Après régénération, **l'écart code/rapport est nul** pour ces six : une
   seconde exécution ne doit plus rien changer **hors auto-inclusion** — le #447
   a établi qu'un rapport qui compte les rapports ne peut pas être idempotent, et
   ce cycle ne redemande donc pas l'impossible.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédiction — falsifiable

- J'attends que **la dérive domine largement l'effet**, comme au #445 : ces
  rapports datent de cycles anciens et le dépôt a beaucoup grossi depuis.
- J'attends **au moins un** rapport dont le diff ne contient **aucun** effet de
  la règle — un script dont le corpus ne croise aucun des cinq reclassés. Si les
  six montrent tous un effet, c'est ma prédiction qui aura tort.
- Je **n'exclus pas** qu'un script échoue à s'exécuter : plusieurs n'ont pas été
  lancés depuis longtemps, et le #449 n'a vérifié que leur **syntaxe**, pas leur
  exécution. Ce serait un résultat en soi, publié comme tel.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL**.
2. Aucun script modifié par ce cycle — il **exécute** et **compare**, il ne
   corrige pas. Tout défaut découvert est publié et inscrit, pas réparé au
   passage.
3. Aucun groupe de diff laissé sans attribution.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
