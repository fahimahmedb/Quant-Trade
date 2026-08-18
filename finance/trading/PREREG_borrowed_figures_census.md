# Pré-enregistrement — recenser les **chiffres empruntés sans relecture**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #499.

## D'où vient la question

Au **#497**, ma prédiction reposait sur un « + 2 » **emprunté à l'audit du
#496 sans le recalculer**. Il valait **3**. La prédiction est tombée pour cette
seule raison.

> **L'emprunt est un canal d'erreur que le dépôt n'a jamais dénombré.** Les
> #479-#493 ont compté les chiffres **sans code qui les produise** ; personne
> n'a compté ceux qui sont **attribués à un autre cycle** et **retapés** au
> lieu d'être relus.

## Les deux définitions — **figées ici**, établies par AST

**Chaîne publiée** : un littéral de chaîne (`Constant`) ou une f-string
(`JoinedStr`) apparaissant, directement ou imbriqué, dans un appel à
`.append(`, `.write_text(` ou `print(`. Les commentaires et les docstrings en
sont exclus **par construction** — l'AST ne les voit pas comme arguments.

**Chiffre emprunté** : une chaîne publiée qui contient **à la fois**

- une **référence croisée** `#\d{3}` — le numéro d'un autre cycle ;
- un **nombre en gras** `\*\*…\*\*` présent **en texte littéral**, c'est-à-dire
  **hors** de tout champ interpolé d'une f-string.

Le second point est la distinction **porteur / citeur** du #473 : un
`f"… **{n}** …"` **calcule**, un `"… **3** …"` **recopie**.

**Relecteur** : un script qui appelle `.read_text(` **et** porte au moins un
littéral se terminant par `.md` **différent** de son propre rapport — il va
donc lire un rapport tiers au lieu d'en retaper les chiffres.

## Ce qui est mesuré

1. Le nombre de scripts **porteurs d'un chiffre emprunté**, et le nombre
   d'emprunts.
2. Le nombre de **relecteurs**.
3. Le **croisement** : porteurs qui sont aussi relecteurs, et porteurs qui ne
   le sont pas — **c'est le cœur de la question**.
4. Les **cycles cités** dans les emprunts, et combien de fois.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **trois définitions** citées verbatim, établies par **AST**.
2. Population, **porteurs**, **emprunts** et **relecteurs** publiés.
3. Le **croisement** publié, avec la part des porteurs **non relecteurs**.
4. Les **cycles cités** nommés avec leur compte.
5. **Aucun script exécuté** — AST uniquement, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les scripts **porteurs** d'au moins un chiffre emprunté sont **≥ 10**.
2. La **majorité** des porteurs **ne sont pas** relecteurs — ils retapent sans
   aller lire.
3. Mon propre `nonml_execution_primitives_census_backtest.py` (#497) est
   **relecteur** : il lit le rapport du #496 au lieu d'en retaper les chiffres.
   *(Le « + 2 » fautif était dans mon **pré-enregistrement**, pas dans mon
   code — ce cycle mesure les scripts, et cette prédiction dit exactement ce
   que la mesure peut et ne peut pas voir.)*

Si la prédiction 2 est réfutée — la majorité des porteurs lisent aussi —
alors l'emprunt cohabite avec la relecture, et le défaut n'est pas
« ne pas lire » mais **lire et retaper quand même**, ce qui est pire.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script : **AST uniquement**.
- Il ne **corrige** aucun emprunt, ne **régénère** aucun rapport — le #499
  vient de montrer qu'un rapport régénéré n'est pas committable.
- Il ne **juge pas** si un chiffre emprunté est **faux** : vérifier chaque
  emprunt contre sa source est un autre cycle, et il sera proposé.

Cette dernière limite est **importante** : ce recensement mesure une
**exposition**, pas une **erreur**.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que le canal est **rare**
   et que le #497 était un cas isolé.
2. Définitions et population **inchangées** après mesure.
3. Chaque classement adossé au motif AST qui le déclenche.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
