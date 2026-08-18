# Audit indépendant — recensement des primitives d'exécution (#497)

Le backtest apparie des **nœuds** AST. Cet audit **déparse** chaque
`Call` (`ast.unparse`) et apparie du **texte normalisé** — les deux
routes partagent l'analyse syntaxique, **pas la logique d'appariement**,
qui est précisément ce qui avait faux au #496.

## Les 12 primitives, recomptées

| # | Rapport | Route déparsée | Accord |
|---|---|---|---|
| P1 | **23** | **23** | **oui** |
| P2 | **3** | **3** | **oui** |
| P3 | **0** | **0** | **oui** |
| P4 | **0** | **0** | **oui** |
| P5 | **0** | **0** | **oui** |
| P6 | **0** | **0** | **oui** |
| P7 | **0** | **0** | **oui** |
| P8 | **0** | **0** | **oui** |
| P9 | **1** | **1** | **oui** |
| P10 | **8** | **8** | **oui** |
| P11 | **0** | **0** | **oui** |
| P12 | **0** | **0** | **oui** |

- primitives en désaccord : **0**

## La réconciliation tient-elle l'addition ?

- exécutants publiés : **33**
- sous la règle du #496 reconstruite : **30**
- supplémentaires : **3** ; résidu : **0**
- l'addition ferme : **OUI**

## Les chiffres empruntés au #496 sont-ils les siens ?

Le backtest a **lu** trois chiffres dans le rapport du #496. Un lecteur
qui cherche le nombre **après** la phrase alors qu'il la **précède**
ramène un chiffre étranger — c'est arrivé dans ce cycle même. Ils sont
donc relus ici par une autre expression :

| Grandeur | Colonne #496 du rapport | Relu dans le #496 | Accord |
|---|---|---|---|
| scripts exécutants | **30** | **30** | **oui** |
| angle mort | **8** | **8** | **oui** |
| cibles | **11** | **11** | **oui** |

## Les témoins

- noms listés par le #497 : **4** ; par le #494 : **4**
- listes identiques : **OUI**

## Le backtest exécute-t-il quelque chose ?

- primitives d'exécution d'un tiers dans sa source : **0**
- fichiers de l'arbre git modifiés hors ce cycle : **0**

> **Rien n'a été exécuté.** Ses appels `subprocess` visent `git` et
> **ne passent pas par `sys.executable`** : aucune primitive ne se
> déclenche, sans qu'aucune ait été retirée à la main.

## Les chiffres du rapport sont-ils calculés ?

- nombres en gras : **56** ; dont **tapés en dur** : **0**

## Verdict

1. les deux routes donnent les mêmes 12 comptes — **OUI**.
2. la réconciliation ferme l'addition sans résidu — **OUI**.
3. les chiffres empruntés au #496 sont bien les siens — **OUI**.
4. les témoins du #497 sont exactement ceux du #494 — **OUI**.
5. le backtest n'exécute aucun tiers et ne salit pas l'arbre — **OUI**.
6. aucun chiffre du rapport n'est tapé en dur — **OUI**.

**AUDIT OK** (6/6)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est **l'inertie**, vérifiée ci-dessus.
