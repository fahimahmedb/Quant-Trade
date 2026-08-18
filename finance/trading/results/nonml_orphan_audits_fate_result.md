# Le sort des **3 audits orphelins** (pré-enregistré)

Le **#477** les a nommés « audits orphelins » et a posé la question sans
y répondre : **cycle interrompu après l'audit, ou résultat publié sous un
autre nom ?** Il avait déjà reconnu qu'une étiquette précédente — « cycle
complet » — était trop généreuse. **Rien ne garantissait que celle-ci le
soit davantage.**

## Les quatre faits, cycle par cycle

La commande qui balaie l'historique, pour qu'un lecteur la refasse :

```
git log --all --diff-filter=A \
    -- 'finance/trading/results/nonml_<nom>_result.md'
```

| `<nom>` | script `_backtest.py` | `_result.md` dans l'historique | l'audit cite un rapport présent | le PREREG promet un résultat |
|---|---|---|---|---|
| `n_trials_dependence_correction` | **ABSENT** | **0** | **0** | **non** |
| `pnl_duplicate_sweep_v2` | **ABSENT** | **0** | **0** | **non** |
| `pnl_persistence_exposed_pass` | **ABSENT** | **0** | **0** | **oui** |

## Cycle par cycle — nominativement

### `n_trials_dependence_correction` → **C — aucun résultat attendu par conception**

- script producteur `nonml_n_trials_dependence_correction_backtest.py` : **absent**
- `_result.md` ajouté à un commit quelconque : **0**
- pré-enregistrement présent : **oui** ; il **promet** un `_result.md` : **non** ; il se déclare cycle d'audit/correction : **oui**
- son audit ne cite **aucun** rapport tiers

### `pnl_duplicate_sweep_v2` → **aucune des trois**

- script producteur `nonml_pnl_duplicate_sweep_v2_backtest.py` : **absent**
- `_result.md` ajouté à un commit quelconque : **0**
- pré-enregistrement présent : **oui** ; il **promet** un `_result.md` : **non** ; il se déclare cycle d'audit/correction : **non**
- son audit ne cite **aucun** rapport tiers

### `pnl_persistence_exposed_pass` → **A — cycle interrompu après l'audit**

- script producteur `nonml_pnl_persistence_exposed_pass_backtest.py` : **absent**
- `_result.md` ajouté à un commit quelconque : **0**
- pré-enregistrement présent : **oui** ; il **promet** un `_result.md` : **oui** ; il se déclare cycle d'audit/correction : **non**
- son audit ne cite **aucun** rapport tiers

## Le verdict d'ensemble

| Lecture | Nombre | Cycles |
|---|---|---|
| **A** — cycle interrompu | **1** | `pnl_persistence_exposed_pass` |
| **B** — publié sous un autre nom | **0** | — |
| **C** — aucun résultat attendu | **1** | `n_trials_dependence_correction` |
| **?** — aucune des trois | **1** | `pnl_duplicate_sweep_v2` |

> **La dette du #477 est réelle** pour les cycles classés **A** : le
> pré-enregistrement annonçait un résultat, aucun n'existe ni n'a
> jamais existé. Elle reste inscrite telle quelle.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 2 sur 3 relèvent de C | ≥ 2 | 1 | **réfutée** |
| aucun `_result.md` dans l'historique | 0 | 0 | **vérifiée** |
| ≥ 1 audit nomme un rapport présent | ≥ 1 | 0 | **réfutée** |

## Ce que ma règle a mal lu — constat post-mesure

*Ajouté après mesure, et signalé comme tel.* **Le classement ci-dessus
n'est pas modifié** : la règle était fixée d'avance, cet examen ne
l'était pas.

En relisant les trois pré-enregistrements, chacun **se déclare**
explicitement dès ses premières lignes :

| `<nom>` | Ce que son pré-enregistrement dit de lui-même |
|---|---|
| `n_trials_dependence_correction` | « Cycle de **correction statistique** » |
| `pnl_duplicate_sweep_v2` | « Cycle de **diagnostic** » |
| `pnl_persistence_exposed_pass` | « Cycle de **infrastructure et de mesure** » |

**Deux défauts de ma règle, mesurés :**

1. `pnl_duplicate_sweep_v2` se déclare **« Cycle de diagnostic :
   aucune stratégie évaluée »**. Mon expression régulière cherchait
   « audit », « correction », « vérification » — **pas « diagnostic »**.
   D'où le classement « aucune des trois ».
2. `pnl_persistence_exposed_pass` se déclare **« Cycle
   d'infrastructure et de mesure »**. Ma règle l'a cru **promettant un
   résultat** parce que son texte contient `results/nonml_<nom>_result.md`
   — mais cette mention désigne **les rapports des dix autres cycles**
   qu'il compare, pas le sien. **Faux positif.**

> **Lu à la main, les trois relèvent de la lecture C** — aucun n'attendait
> de `_result.md`. **Je ne retiens pas cette version.**

Le pré-enregistrement fixait une règle mécanique et **n'avait pas prévu**
d'examen à la main, contrairement aux #476 et #479 qui l'avaient déclaré.
Reclasser maintenant serait **choisir le résultat qui m'arrange après
l'avoir vu** — la faute exacte que le #469 avait refusé de commettre
quand son propre examen le désavantageait.

**La prédiction 1 reste donc réfutée**, et les faits qui la
vérifieraient sont publiés juste au-dessus. Un lecteur tranchera mieux
que moi.

## Une limite de ma règle, dite sans être découverte après coup

La lecture **C** repose sur une expression régulière appliquée au
pré-enregistrement — elle cherche s'il se **déclare** cycle d'audit ou
de correction. **Une déclaration formulée autrement lui échappe**, comme
l'écriture par variable avait échappé au #469 et l'apostrophe à l'audit
du #478.

C'est pourquoi les **quatre faits bruts sont publiés** au-dessus du
classement : un lecteur qui juge ma règle trop lâche ou trop stricte
peut reclasser lui-même, **sans me croire**.

## Critères de succès

1. Les **3** nommés, quatre faits publiés chacun — **OUI**.
2. Historique balayé, commande publiée — **OUI**.
3. Une lecture nommée pour chacun — **OUI**.
4. Étiquette « audit orphelin » rétractée si C domine — **sans objet**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).