# Audit indépendant — réparation de la borne du lot 2 (#499)

Ce cycle a **modifié** puis **exécuté** un script du dépôt avant de tout
restaurer. Deux questions, posées par le #495 : la restauration est-elle
**réelle**, et la conclusion tient-elle **sans croire** le script modifié ?

## La restauration est-elle réelle ?

- fichiers de l'arbre modifiés hors ce cycle : **0**
- diff du script cible vs `HEAD` : **0** ligne(s)
- diff du rapport cible vs `HEAD` : **0** ligne(s)
- arbre propre : **OUI**

## La cible porte-t-elle encore ses littéraux ?

Si la réparation avait été committée en douce, ils auraient disparu.

- littéral du **titre** encore présent : **oui**
- littéral de la **phrase** encore présent : **oui**
- littéral **de contrôle** (l. 123) encore présent : **oui**
- littéral du **titre de section** (l. 132) encore présent : **oui**

- cible intacte : **OUI**

## La classe A, par une route indépendante

Le backtest **importe** la règle du #497. Cet audit la réapplique en
**déparsant** les nœuds `Call`, sans rien importer du #497.

- appels exécutant un tiers : **0**
- cibles d'écriture distinctes : **1** (OUT)
- classe A confirmée : **OUI**

## La borne, recalculée à la main

`bound(n) = 1 − 0,05^(1/n)`, **réécrite ici**, jamais importée de la
cible. Si les littéraux étaient exacts, cette arithmétique suffit à le
montrer — sans faire confiance au script réparé.

- dénominateur cumulé lu dans le rapport cible : **47** (**confirmé**)

| Grandeur | Publié dans la cible | Recalculé ici | Accord |
|---|---|---|---|
| borne actuelle | **6,2 %** | **6,2 %** | **oui** |
| borne projetée (+24) | **~4,1 %** | **~4,1 %** | **oui** |

> **Les deux littéraux étaient exacts.** Le défaut n'était donc pas
> une erreur de calcul mais une **duplication de source** — et le
> `~4,1 %`, que le #499 prédisait faux, ne l'était pas.

## L'imputation du diff, recontrôlée

- lignes imputées à la réparation par le rapport : **0**
- lignes imputées à la dérive : **28**

> L'imputation est **cohérente avec l'arithmétique** : des littéraux
> exacts réécrivent les mêmes caractères, donc la réparation ne
> pouvait produire **aucune** ligne de diff. Les deux mesures se
> confirment l'une l'autre par des chemins séparés.

## Chiffres calculés

- nombres en gras : **19** ; dont **tapés en dur** : **0**

## Verdict

1. la restauration est réelle — arbre et diffs vides — **OUI**.
2. la cible porte encore ses quatre littéraux — **OUI**.
3. la classe A est confirmée par une route indépendante — **OUI**.
4. la borne recalculée à la main confirme les deux littéraux — **OUI**.
5. l'imputation du diff est cohérente (**0** / **28**) — **OUI**.
6. les **2** dettes déclarées sont bien encore en place — **OUI**.
7. aucun chiffre du rapport tapé en dur — **OUI**.

**AUDIT OK** (7/7)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est la **restauration**, vérifiée ci-dessus contre
l'arbre `git` et non contre la parole du cycle audité.
