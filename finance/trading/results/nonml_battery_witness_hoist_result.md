# **Déplacer** le témoin de `battery_coverage` (pré-enregistré)

## L'aveu préalable

Le #489 a ajouté ce témoin **dans un bloc englobant**, a conclu **FAIL**,
et a **refusé de déplacer la ligne après coup** en inscrivant le
déplacement comme piste à déclarer d'avance. **C'est ce cycle.**

> **Je sais qu'une ligne placée au niveau libre satisferait la règle.**
> Ce point est donc **non informatif**, et **aucune prédiction ne porte
> dessus.** Ce qui était ouvert est ailleurs : `indet` est-elle seulement
> **disponible** au niveau libre ?

## Volet A — le déplacement tient-il en une ligne ?

| Nom | Ligne d'affectation | Profondeur de garde |
|---|---|---|
| `indet` | 157 | **1** |
| `executes` | 97 | **0** |

- `indet` est affectée à **profondeur 1** ;
- `executes`, dont elle dépend, est liée à **profondeur 0**.

> **Le témoin ne peut pas être écrit au niveau libre en déplaçant une
> seule ligne** : `indet` n'y est pas dans la portée. Il faudrait
> **hisser son affectation** — ou **dupliquer** le `sum(...)` dans
> le témoin, ce qui créerait **deux sources pour un même chiffre**,
> précisément le défaut que les #479 à #488 ont passé neuf cycles à
> dénombrer.

**Le pré-enregistrement l'interdisait** : *« Si le déplacement exige de
hisser `indet` ou `executes`, il n'est pas fait. »*

### Ce que je dois dire contre moi

`executes` est liée au **niveau libre** (ligne 97), et le script y publie déjà `len(executes)` **sans garde**.
**Hisser `indet` serait donc parfaitement anodin ici** : toutes ses
dépendances sont disponibles, et le calcul est pur.

> **Mon pré-enregistrement était plus strict que nécessaire, et je
> l'applique quand même.** Il a été écrit avant de savoir que le
> déplacement serait inoffensif ; l'assouplir maintenant parce que la
> mesure me montre qu'il l'est **serait exactement l'ajustement
> a posteriori que ces cycles refusent.**

**Un cycle ultérieur pourra déclarer le hissage d'avance.** Ce sera
un geste légitime — mais il devra être annoncé, pas improvisé.

## Volet B — ce qui a été modifié

- lignes ajoutées : **0** — supprimées : **0**

> **Rien.** Le volet A a décidé, et sa décision était prise **avant**
> de consulter la règle du #481. **Un cycle de modification qui ne
> modifie rien n'a pas échoué** — c'était déjà la conclusion du #482.

## Volet C — la règle du #481, avant et après

| | Avec témoin | Sans témoin | Garde non nommée |
|---|---|---|---|
| **avant** | 1 | **1** | 0 |
| **après** | 1 | **1** | 0 |

**Inchangé, puisque rien n'a été modifié.** Il n'y a donc **aucun
résultat favorable à présenter comme non informatif** — la question ne
se pose pas, et c'est le volet A qui a tout décidé.

## Aucune exécution

`battery_coverage` **exécute la batterie de validation** ; il n'est pas
lancé. Vérifié par l'état git de son rapport :

- `nonml_battery_coverage_result.md` : **inchangé**

**Son témoin — celui ajouté au #489 — reste dans le code, pas dans son
rapport.** Il y paraîtra à la prochaine exécution légitime de la
batterie.

## Mes trois prédictions, confrontées

*(Aucune ne porte sur la règle du #481 — c'était l'engagement 3.)*

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| `indet` affectée à profondeur > 0 | > 0 | 1 | **vérifiée** |
| le déplacement exige de hisser un calcul | oui | oui | **vérifiée** |
| aucune autre section ne change de classe | 0 | 0 | **vérifiée** |

**Les trois sont vérifiées, et le cycle ne modifie rien.** C'est le
résultat le plus mince de la série — mais il est **décidé par une mesure**
prise avant toute modification, et non par le confort de conclure.

## Critères de succès

1. Profondeur de `indet` et portée de ses dépendances publiées — **OUI**.
2. Décision prise par le volet A, avant la règle — **OUI**.
3. Diff conforme à la décision — **OUI** (**0** ajout(s), **0** suppression(s)).
4. Règle ré-appliquée, résultat favorable dit non informatif — **OUI** *(sans objet : aucun changement)*.
5. `battery_coverage` non exécuté — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).