# Audit indépendant — réparation du candidat actionnable (#511)

Ce cycle a **modifié et committé** un script du dépôt. L'audit vérifie
ce que le backtest, **juge et partie**, ne peut pas établir seul.

## 1. La réparation est-elle réellement dans l'arbre ?

- `_hors` présent dans la version **committée** (`HEAD`) : **OUI**
- l'ancien littéral a **disparu** de `HEAD` : **OUI**
- commit qui introduit `_hors` : **079f153d**
- arbre propre hors ce cycle : **OUI**

> Une réparation **annoncée** et une réparation **déposée** sont deux
> choses différentes. Le #499 avait tout restauré ; ici l'arbre doit
> porter la trace, et `git show HEAD:` la porte.

## 2. Le rapport de la cible a-t-il bougé ?

- commits touchant `nonml_battery_backfill_lot_audit.md` : **1**
- diff du rapport entre `HEAD~1` et `HEAD` : **0** ligne(s)

> **Le rapport n'a pas bougé d'un octet.** C'est la preuve la plus
> forte que l'interpolation était **exacte** : le code calcule
> désormais ce qui était tapé, et produit **les mêmes caractères**.
> Une réparation visible dans le rapport aurait signifié que le
> littéral était faux.

## 3. La valeur dérivée, recalculée ici

Recalcul depuis `SET_ASIDE`, **lu par AST** dans la cible — sans
l'exécuter, sans lire le rapport du #511.

- entrées dans `SET_ASIDE` : **2**
- dont motif « panier » : **1**
- valeur publiée par le rapport de la cible : **1**
- accord : **OUI**

## 4. Le « 0,00 % » est-il toujours en dur, comme annoncé ?

- littéral `0,00 %` encore présent : **OUI**
- la cible ouvre-t-elle un `.npz` : **NON**

> **Confirmé sur les deux points.** Le chiffre reste en dur, et la
> cible n'ouvre toujours aucune donnée d'activation : la
> justification du #485 le concernant est bien **fausse**, et le
> #511 n'a pas prétendu le réparer.

## Ce que cet audit ne prouve pas

Il ne dit **pas** que la valeur **1** soit la bonne réponse à la
question posée dans la phrase — seulement qu'elle est désormais
**dérivée** de `SET_ASIDE` au lieu d'être tapée. Si `SET_ASIDE` est
lui-même incomplet, le nombre reste faux, **calculé mais faux**.

## Chiffres calculés

- nombres en gras dans le rapport : **15** ; dont **tapés en dur** : **0**

## Verdict

1. la réparation est présente dans `HEAD` — **OUI**.
2. le rapport de la cible n'a pas bougé — **OUI**.
3. la valeur dérivée concorde avec un recalcul indépendant — **OUI**.
4. le « 0,00 % » reste en dur et la cible n'ouvre pas de `.npz` — **OUI**.
5. arbre propre, aucun chiffre du rapport tapé en dur — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est la **vérification contre l'arbre `git`**, et non
contre la parole du cycle audité.
