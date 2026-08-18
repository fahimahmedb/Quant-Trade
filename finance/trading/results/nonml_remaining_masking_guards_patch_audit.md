# Audit adversarial — les 2 masquants restants (#489)

**Le cycle se déclare FAIL.** Un cycle qui échoue son propre critère est
peu suspect de complaisance ; l'audit vérifie donc **l'inverse du réflexe
habituel** : le FAIL est-il **réel**, ou le cycle s'accable-t-il pour
paraître rigoureux tout en ayant fait le travail ?

## 1. Le témoin existe-t-il vraiment dans le code ?

| Script | Variable | Écritures f-string mentionnant la variable | Profondeurs de garde |
|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | `indet` | **2** | [1, 2] |
| `nonml_net_pnl_correction_backtest.py` | `incoh` | **1** | [0] |

> **Les deux témoins existent.** Le FAIL ne vient pas d'un patch
> manquant.

## 2. Le FAIL est-il dû à la raison annoncée ?

Le rapport dit que le témoin de `battery_coverage` est **dans un bloc
englobant**, donc invisible à une règle qui ne cherche qu'au niveau non
gardé. **Vérifié par la profondeur mesurée ci-dessus :**

- `battery_coverage` — profondeur du témoin : **[1, 2]** *(> 0 ⇒ sous garde)*
- `net_pnl_correction` — profondeur du témoin : **[0]** *(0 ⇒ niveau libre)*

> **La raison annoncée est exacte.** L'un est sous garde, l'autre non,
> et c'est précisément ce qui sépare le succès de l'échec. **Le FAIL
> est réel et bien diagnostiqué** — ce n'est pas une modestie de
> façade.

**Et c'est l'angle mort exact que le #484 avait mesuré** : « témoin
situé dans un bloc parent ». Le #489 le rencontre en le provoquant
lui-même.

## 3. Le patch a-t-il été retouché après coup ?

Un cycle qui verrait sa règle échouer serait tenté de **déplacer la
ligne** jusqu'à passer. Contrôle : le diff ne contient-il qu'**une**
écriture de témoin par cible, et **aucune ligne déplacée** ?

- instructions ajoutées : **4** — dont **écritures de
  témoin** : **2**
- lignes **supprimées** : **0**

> **Deux témoins, zéro suppression.** Le patch est **purement
> additif** : aucune ligne n'a été déplacée pour satisfaire la règle.
> **L'engagement de ne pas retoucher est tenu, et vérifiable.**

## 4. `battery_coverage` a-t-il été exécuté ? L'arbre est-il propre ?

| Contrôle | Résultat |
|---|---|
| rapport de `battery_coverage` | **inchangé** |
| rapport de `net_pnl_correction` *(exécuté, non committé)* | **restauré** |
| résidus sous `results/` | **0** |

> **L'exécution asymétrique est respectée et l'arbre est propre.**
> Le rapport régénéré, dont le diff **ne se réduisait pas au témoin**,
> n'est **pas committé** — et il a été **restauré**, pas laissé sale.

## 5. Le cycle publie-t-il ce qui l'accuse ?

| Contrôle | Résultat |
|---|---|
| il rétracte une phrase qu'il avait lui-même écrite au #487 | **OUI** |
| il refuse de déplacer la ligne après coup | **OUI** |
| il relie l'échec à l'angle mort du #484 | **OUI** |
| il conclut FAIL | **OUI** |
| il dit que le témoin non exécuté n'est pas encore visible | **OUI** |

> **Le cycle s'accuse sur pièce** : il rétracte sa propre phrase du
> #487, refuse de retoucher, et conclut FAIL alors qu'un déplacement
> de ligne l'aurait fait passer.

## Verdict

**CONCORDANT** — le **FAIL est réel**, sa
cause est **l'angle mort du #484** rencontré en direct, le patch est
**purement additif et non retouché**, l'arbre est **propre**, et
**5/5** contrôles de
transparence sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).