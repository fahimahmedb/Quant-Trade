# Pré-enregistrement — **déplacer** le témoin de `battery_coverage`

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #489.

## Un aveu préalable

Le #489 a ajouté un témoin à `battery_coverage`, **mais dans un bloc englobant**
(profondeur mesurée `[1, 2]`), si bien que la règle du #481 — qui ne cherche
qu'au niveau non gardé — ne le voit pas. Il a conclu **FAIL** et **refusé de
déplacer la ligne après coup**, en inscrivant le déplacement comme piste à
déclarer d'avance. **C'est ce cycle.**

> **Je sais déjà qu'une ligne placée au niveau libre satisferait la règle.**
> Annoncer « prédiction vérifiée : la règle passe » serait prédire une
> tautologie. **Ce point sera publié comme non informatif**, et aucune
> prédiction ne portera dessus.

Ce qui est réellement ouvert est **ailleurs, et je ne l'ai pas regardé** : la
variable `indet` est calculée **à l'intérieur** d'un bloc. **Est-elle seulement
disponible au niveau libre ?**

## Volet A — le déplacement est-il possible en une ligne ?

Établi par **AST**, avant toute modification :

1. à quelle profondeur `indet` est-elle **affectée** ?
2. les noms dont elle dépend (`executes`) sont-ils **liés au niveau libre** ?
3. le déplacement exige-t-il de **hisser un calcul**, ou seulement une ligne
   d'écriture ?

## Volet B — la modification, et sa borne

**Si et seulement si** le témoin peut être écrit au niveau libre **sans hisser
aucun calcul**, la ligne est déplacée. Forme fixée ici :

```python
L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")
```

**Si le déplacement exige de hisser `indet` ou `executes`**, il **n'est pas
fait**. Restructurer un script pour satisfaire une règle de lecture serait
**changer le code pour plaire à la métrique** — exactement ce que ces cycles
refusent depuis le #480. Le rapport publiera alors que **la réparation coûte
plus qu'une ligne** et sort du périmètre déclaré.

## Volet C — aucune exécution

`battery_coverage` **exécute la batterie de validation**
(`subprocess.run([sys.executable, BATTERIE, …])`). **Il n'est pas exécuté**, et
son témoin restera **dans le code, pas dans son rapport** — comme au #487 et au
#489. Vérification **statique** par la règle du #481, avant et après.

## Critère de succès — chiffré, il porte sur le procédé

1. Profondeur d'affectation de `indet` et portée de ses dépendances
   **publiées**.
2. Décision de déplacer **ou non** prise **par le volet A**, jamais par le
   résultat de la règle.
3. Si déplacement : **diff publié en entier**, une ligne déplacée, **zéro ligne
   ajoutée ou supprimée par ailleurs**.
4. Règle du #481 ré-appliquée avant/après, et le résultat **présenté comme non
   informatif** s'il est favorable.
5. `battery_coverage` **non exécuté**, vérifié par l'état git de son rapport.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables, et **aucune ne porte sur la règle**

1. `indet` est affectée **à une profondeur > 0**.
2. Le déplacement **exige de hisser un calcul** — donc il **n'aura pas lieu**.
3. **Aucune autre section** du script ne change de classe.

Si la prédiction 2 est réfutée — le déplacement tient en une ligne — alors le
#489 avait **la réparation à portée** et ne l'a pas vue. Je devrai l'écrire :
son refus de retoucher était juste sur le principe, **mais il aurait pu déclarer
le bon geste dès le départ**.

## Ce que ce cycle ne fait pas

- Il ne **restructure** aucun script : pas de calcul hissé, pas de fonction
  extraite.
- Il n'**exécute** rien.
- Il ne **corrige pas** la règle du #481, dont les trois angles morts restent
  inscrits — c'est elle qui a créé ce travail, et elle n'est pas jugée ici.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si la réparation s'avère impossible
   dans le périmètre.
2. Décision du volet B **inchangée** après avoir vu la règle.
3. Le résultat favorable sur la règle **présenté comme non informatif**.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
