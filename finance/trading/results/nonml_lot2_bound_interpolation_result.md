# Réparer le 13ᵉ réparable : interpoler la borne du lot 2 (pré-enregistré)

## La classe de la cible, établie par AST — non supposée

La règle des **12 primitives** du #497 est **importée**, jamais recopiée :
recopier une règle est le meilleur moyen de la faire diverger. L'import
n'appelle pas `main()` — ce n'est donc pas la primitive **P10**.

- primitives d'exécution d'un tiers dans la cible : **0** (aucune)
- classe : **A — exécutable sans danger**

> Ce script-ci, lui, **modifie et exécute** un tiers : il est de
> **classe C** au sens du #497, et le dire vaut mieux que feindre
> l'inertie.

## Le diff du `.py`

- lignes changées dans le script cible : **13**

```
TIRAGES_SUP = 24


def _fr(x):
    """Rend un nombre a la francaise -- la typographie deja publiee."""
    return f"{x:.1f}".replace(".", ",")


    L = ["# Audit — campagne v3, lot 2 : la borne tombe à 6,2 %", ""]
    L = [f"# Audit — campagne v3, lot 2 : la borne tombe à {_fr(100*bound(cum))} %", ""]
    L.append("24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** — de ~17 à")
    L.append(f"{TIRAGES_SUP} tirages de plus feraient passer la borne de **{_fr(100*bound(cum))} %** à "
             f"**~{_fr(100*bound(cum + TIRAGES_SUP))} %** — de ~17 à")
```

## Le diff du rapport

- lignes changées dans le rapport : **28**

```
- vivier recompté : **290**
- échantillon redérivé identique au publié : **oui** ✔
- vivier recompté : **348**
- échantillon redérivé identique au publié : **NON** ✘
| #438 seul | 23 | 12.2 % | ~35 |
| ce lot seul | 24 | 11.7 % | ~34 |
| **cumul** | 47 | 6.2 % | ~17 |
| #438 seul | 23 | 12.2 % | ~42 |
| ce lot seul | 24 | 11.7 % | ~40 |
| **cumul** | 47 | 6.2 % | ~21 |
Sur **290** rapports, la borne laisse place à **~17**
Sur **348** rapports, la borne laisse place à **~21**
| 47 | 6.2 % | ~17 |
| 71 | 4.1 % | ~11 |
| 100 | 3.0 % | ~8 |
| 150 | 2.0 % | ~5 |
| 200 | 1.5 % | ~4 |
| 47 | 6.2 % | ~21 |
| 71 | 4.1 % | ~14 |
| 100 | 3.0 % | ~10 |
| 150 | 2.0 % | ~6 |
| 200 | 1.5 % | ~5 |
| tirage reproductible et disjoint | oui | oui | ✔ |
| tirage reproductible et disjoint | oui | non | ✘ |
**Les quatre contrôles passent.** La correction du #439 a été reportée *avant*
le tirage plutôt qu'après en avoir vu les effets — c'est le seul point où ce
cycle fait mieux que les trois précédents, et il ne tient qu'à avoir vérifié
un script hérité au lieu de le supposer à jour.
```

## Ce qui, dans ce diff, vient de la réparation

- lignes du diff **imputables aux sites réparés** : **0**
- lignes du diff **étrangères à la réparation** : **28**

> **La réparation n'a produit aucun changement de texte.** Les deux
> littéraux étaient exacts : interpolés, ils réécrivent les mêmes
> caractères. **La totalité du diff est de la dérive du dépôt**, sans
> rapport avec ce cycle.

> Ce qui échoue n'est donc pas la réparation, c'est la **possibilité
> de la committer**. Le rapport cible n'est plus reproductible : le
> régénérer réécrit son vivier, son échantillon et l'un de ses
> contrôles. **Un chiffre dérivable n'est pas pour autant réparable
> par un geste borné** — le #493 comptait la dérivabilité, pas la
> committabilité, et les deux ne coïncident pas.

## Les valeurs calculées, face aux littéraux

| Site | Littéral d'origine | Valeur calculée |
|---|---|---|
| titre | **6,2 %** | **6,2 %** |
| phrase, borne actuelle | **6,2 %** | **6,2 %** |
| phrase, borne projetée | **~4,1 %** | **~4,1 %** |

> Les deux littéraux étaient **exacts** : la fonction redonne les
> mêmes valeurs. Le défaut était la **duplication de source**, pas
> l'erreur de calcul — et il est levé.

## Les dettes laissées en place — nommées, non corrigées

- littéraux `6,2` **encore présents** dans la cible : **2**

- **l. 123** — `ok_bound = abs(100 * bound(cum) - 6.2) < 0.2` : littéral **de contrôle** qui **garde une section** — le corriger changerait la logique, pas la typographie. Nommé au pré-enregistrement.
- **l. 132** — `L.append("## Ce que 6,2 % dit — et ne dit pas")` : **titre de section** portant le même littéral. **Mon énumération du pré-enregistrement ne l'avait pas vu** : je ne l'élargis pas après coup.

> La seconde est la plus instructive : **un cycle dédié à réparer des
> chiffres en dur a lui-même sous-énuméré les sites**. Je la laisse, et
> je l'écris — l'élargir maintenant serait la dérive que le #490 a
> refusée à son propre détriment.

## Le geste est-il resté borné ?

- autres fichiers de l'arbre touchés : **0**
- échec : **le diff du rapport déborde : 28 ligne(s) hors des sites autorisés**

> **Tout a été restauré** — script et rapport. Le barème du #489 et
> du #495 s'applique sans adoucissement.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| la cible est de classe A | 0 primitive | 0 | **vérifiée** |
| `100*bound(cum)` redonne le littéral | 6,2 | 6,2 | **vérifiée** |
| la borne projetée diffère de `~4,1` | ≠ | 4,1 | **réfutée** |

## Critères de succès

1. Classe de la cible établie par AST, 0 primitive d'exécution — **OUI**.
2. Diff du `.py` publié, limité aux sites énumérés (**13** lignes) — **OUI**.
3. Diff du rapport réduit aux sites autorisés (**28** lignes) — **NON**.
4. Valeurs calculées publiées face aux littéraux — **OUI**.
5. Littéraux de contrôle nommés comme dette (**2**), non modifiés — **OUI**.

**FAIL** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de réparation,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la
> date de son exécution.
