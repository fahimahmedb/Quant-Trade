# Pré-enregistrement — la couverture réelle de la convention « un `PREREG_` par entrée »

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #463.

## Pourquoi ce cycle existe

Les **deux** derniers cycles de vérification reposent sur une convention qu'ils
n'ont jamais éprouvée :

> chaque entrée de backlog cite **un** `PREREG_<nom>.md`, et le rapport du cycle
> est `results/nonml_<nom>_result.md`.

Le #461 s'en sert pour apparier entrée et rapport ; le #462 pour retrouver le
`<nom>` de chaque cycle. Et la robustesse du #462 a laissé passer un signal :
élargir la borne de #430 à #415 n'ajoutait **aucune** entrée. Des entrées
sortent du périmètre, sans qu'aucun cycle ait dit **combien** ni **lesquelles**.

**Une convention sur laquelle deux instruments s'appuient mérite d'être
mesurée**, pas supposée.

## L'univers — toutes les entrées, sans fenêtre

**Toutes** les entrées `## Backlog #N` du `NONML_STRATEGY_BACKLOG.md` à `HEAD`.
Pas de borne : le coût est celui d'une lecture de fichier, et une fenêtre
n'aurait ici aucune justification autre que la commodité.

## Ce qui est mesuré — quatre questions, décidées ici

Pour chaque entrée :

1. combien de `PREREG_<nom>.md` **distincts** son texte cite-t-il — **0**, **1**
   ou **plusieurs** ;
2. quand elle en cite **un**, ce fichier **existe-t-il** dans le dépôt ;
3. quand elle en cite **un**, le rapport `results/nonml_<nom>_result.md`
   **existe-t-il** ;
4. combien de `PREREG_*.md` du dépôt ne sont **cités par aucune** entrée.

Le texte d'une entrée va de son titre jusqu'au prochain `## `, comme aux #461 et
#462 — **même découpage, pour que les trois cycles se comparent**.

## Ce que ce cycle ne fera pas dire à ses chiffres

Une entrée qui ne cite aucun `PREREG_` **n'est pas nécessairement fautive** :
les premières entrées du backlog sont des lignes de tableau décrivant des
stratégies, pas des cycles de vérification, et la convention est née en cours de
route. **Un compte n'est pas un reproche**, et le rapport devra distinguer
« hors convention » de « en infraction » — sans quoi il fabriquerait une
accusation, comme le #462 l'a fait avec ses 9 fausses discordances.

## Critère de succès — chiffré, il porte sur le procédé

1. **100 %** des entrées classées dans l'une des trois catégories (0, 1,
   plusieurs).
2. **Toute** citation pendante (fichier absent) listée nominativement.
3. **Tout** `PREREG_` orphelin listé nominativement.
4. La distinction « hors convention » / « en infraction » **explicitée**, et
   aucune entrée qualifiée de fautive sans que la raison soit donnée.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Moins de la moitié** des entrées citent exactement un `PREREG_`.
   Fondement : la convention est née en cours de route, et le #462 a montré que
   l'intervalle #400-#460 n'en contenait qu'une trentaine d'exploitables.
2. **Zéro** citation pendante : un `PREREG_` cité mais absent du dépôt.
3. **Au moins un** `PREREG_` du dépôt n'est cité par aucune entrée.

Si la prédiction 2 est réfutée, c'est un défaut réel du dépôt et il se publie
tel quel. Si la 1 est réfutée **dans le sens flatteur** — la convention est
mieux suivie que je ne le crois —, je dois d'abord **douter de mon comptage**,
comme au #458 et au #462.

## Ce que ce cycle ne fait pas

- Il ne **corrige** aucune entrée ni aucun nom : publié et inscrit, pas réparé
  au passage — engagement tenu depuis le #450.
- Il ne **réécrit** aucun verdict.
- Il ne **rejoue** aucun script : lecture seule, donc **aucun effet de bord** à
  annuler, contrairement au #463.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que les #461 et #462
   s'appuyaient sur une convention peu suivie — ce qui **affaiblirait leurs
   propres conclusions**, et je le dirai.
2. Univers et questions **inchangés** après mesure.
3. La distinction « hors convention » / « en infraction » est maintenue même si
   elle rend le résultat moins spectaculaire.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
