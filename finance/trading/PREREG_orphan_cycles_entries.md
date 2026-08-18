# Pré-enregistrement — les **13 cycles complets sans entrée de backlog**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle MIXTE** — vérification puis, sous condition, une seule écriture.
Première piste de la file ouverte au #476, inscrite au #474.

## La dette à traiter

Le **#474** a classé 23 `PREREG_` orphelins et en a trouvé **13 « cycles
complets »** : leur rapport **existe**, leur script **existe**, mais **aucune
entrée de backlog ne les mentionne**. Il avait conclu :

> Un `PREREG_` orphelin dont le rapport existe n'est **pas** du travail non
> fait : c'est une **anomalie de trace écrite**.

La tâche inscrite était : « **écrire les entrées manquantes, ou établir qu'elles
sont couvertes autrement** ». **L'ordre compte** : on établit d'abord, on écrit
ensuite — et seulement ce qui reste.

## Volet A — sont-ils couverts autrement ? (mesure)

Le #474 a cherché la mention sous la forme `PREREG_<nom>.md`. C'est **une** forme
de mention, pas la seule. Le #464 avait déjà buté là-dessus : « non cité sous
cette forme » n'est pas « jamais mentionné ».

Pour chacun des 13, on cherche donc dans le backlog entier :

- son **rapport** `nonml_<nom>*.md` cité nominativement ;
- son **script** `nonml_<nom>*.py` cité nominativement.

**Couvert autrement** = au moins l'un des deux apparaît. **Non couvert** =
aucun.

## Volet B — l'écriture, conditionnelle et unique

Pour les seuls **non couverts**, **une seule entrée collective** est ajoutée au
backlog, qui les nomme et pointe leurs rapports.

**Ce qui ne sera pas fait, et pourquoi.** Aucune entrée **rétro-datée** ne sera
créée, aucun numéro ne sera inséré dans la suite existante. Fabriquer treize
entrées à la place de cycles qui n'en ont jamais écrit reviendrait à **falsifier
la chronologie** du dépôt pour faire disparaître une lacune — exactement le
geste que ces cycles reprochent ailleurs. Une entrée qui **dit** la lacune vaut
mieux qu'une trace qui la **masque**.

Si le volet A trouve **zéro** non couvert, **le volet B n'a pas lieu** et le
cycle reste en lecture seule.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **13** re-dérivés par code, effectif publié, et tout écart au #474
   signalé.
2. **100 %** classés « couvert autrement » / « non couvert », **chacun nommé**,
   avec la **citation trouvée** pour les couverts.
3. Si des non couverts existent : **une** entrée collective, les nommant tous,
   sans rétro-datation — et le rapport le dit.
4. Aucun `PREREG_` supprimé, aucun rapport régénéré, aucune entrée existante
   réécrite.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 8 sur 13** sont **couverts autrement** — leur rapport ou leur script est
   nommé quelque part. *(Fondement : le #464 a montré que 206 des 230 « orphelins »
   bruts étaient mentionnés sous une autre forme ; la mention existe, la
   convention manque.)*
2. **Tous** les non couverts ont encore leur rapport présent — la lacune est de
   **trace**, jamais de travail. *(Réfutable : un rapport disparu depuis le #474.)*
3. **Aucun** des 13 n'est couvert par une entrée citant son `PREREG_<nom>.md` —
   sinon la population du #474 serait mal dérivée, et je devrais le dire.

Si la prédiction 1 est réfutée et que **la plupart ne sont couverts d'aucune
manière**, alors la lacune de trace est bien plus large que le #474 ne le
laissait croire, et l'entrée collective du volet B devra le dire sans
l'atténuer.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord** hors l'ajout éventuel d'**une** entrée de backlog.
- Il ne **réécrit** aucune entrée existante, ne **supprime** aucun `PREREG_`.
- Il ne juge pas la **qualité** des 13 cycles — seulement la présence de leur
  trace.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris si presque aucun n'est couvert.
2. Population et règle de couverture **inchangées** après mesure.
3. **Chacun des 13 nommé**, jamais seulement compté — leçon des #462, #464,
   #465, #469, #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
