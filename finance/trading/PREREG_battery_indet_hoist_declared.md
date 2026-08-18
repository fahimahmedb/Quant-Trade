# Pré-enregistrement — **hisser `indet`**, déclaré d'avance

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, première piste de la file ouverte au #490.

## Un aveu préalable, comme au #490

Le **#490** a mesuré que déplacer le témoin de `battery_coverage` exigeait de
**hisser l'affectation de `indet`**, que son propre pré-enregistrement
interdisait. Il a appliqué l'interdiction **tout en publiant que le hissage
aurait été anodin** — l'audit l'ayant vérifié : l'expression n'appelle que
`sum`, un builtin pur.

> **Je sais donc que ce hissage marchera.** Annoncer « prédiction vérifiée : la
> règle du #481 passe » serait prédire ce que le #490 a déjà établi. **Ce point
> est publié comme non informatif**, et **aucune prédiction ne porte dessus.**

Ce qui reste ouvert et que je n'ai pas regardé : **le hissage change-t-il le
rapport dans le cas limite**, et **le diff tient-il vraiment en deux lignes
déplacées** ?

## Le geste, fixé ici

Dans `nonml_battery_coverage_backtest.py` :

1. l'affectation `indet = sum(1 for _, _, c in executes if c and c[2] ==
   "indéterminé")` est **déplacée** du bloc `if executes:` vers le **niveau
   libre**, avant ce bloc ;
2. la ligne de témoin ajoutée au #489 est **déplacée** avec elle, au même
   niveau.

**Interdits, explicitement** : modifier l'expression, la garde, le contenu de la
section, un seuil, un verdict. **Le diff sera publié en entier.**

## Le changement de comportement, déclaré d'avance

**Le hissage n'est pas neutre dans un cas limite**, et il faut le dire avant de
le mesurer : si `executes` est **vide**, le bloc `if executes:` ne s'exécute pas
aujourd'hui, et **aucun compte n'est publié**. Après hissage, le témoin
paraîtra **quand même**, avec la valeur **0**.

**C'est l'effet recherché** — c'est même la définition d'un témoin
inconditionnel — mais c'est un **changement de sortie**, pas un simple
déplacement, et le rapport devra le présenter comme tel.

## Aucune exécution

`battery_coverage` **exécute la batterie de validation**. Il **n'est pas
lancé** : vérification **statique** uniquement, et son rapport publié restera
inchangé — comme aux #487, #489 et #490.

## Critère de succès — chiffré, il porte sur le procédé

1. **Diff publié en entier**, et **exactement 2 lignes déplacées** — soit
   **2 suppressions et 2 ajouts** d'instructions, aucune autre.
2. Le **changement de comportement dans le cas limite** énoncé, et **vérifié par
   AST** : le témoin est bien au niveau libre après le geste.
3. Le compte de « sans témoin » du **dépôt entier** publié **avant et après**.
4. `battery_coverage` **non exécuté**, vérifié par l'état git de son rapport.
5. Le résultat sur la règle du #481 présenté comme **non informatif**.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables, et **aucune ne porte sur la règle**

1. Le diff comporte **exactement 2 suppressions et 2 ajouts** d'instructions.
2. Le compte de « sans témoin » du dépôt **diminue exactement de 1**.
3. Les autres classes du script — « avec témoin », « garde non nommée » —
   **restent inchangées**.

Si la prédiction 1 est réfutée — le geste demande plus de deux lignes — alors le
#490 avait **sous-estimé** ce qu'il refusait, et son refus était **mieux fondé
qu'il ne le croyait**. Je devrai l'écrire.

## Ce que ce cycle ne fait pas

- Il ne **restructure** rien d'autre : pas de fonction extraite, pas d'autre
  calcul déplacé.
- Il n'**exécute** aucun script.
- Il ne **corrige pas** la règle du #481, dont les trois angles morts restent
  inscrits.
- Il ne **régénère** aucun rapport.

## Simulation 300 € et robustesse

**Sans objet** : aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le geste s'avère plus lourd que
   deux lignes.
2. Périmètre **inchangé** après mesure.
3. Le changement de comportement **présenté comme tel**, jamais comme un simple
   déplacement.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
