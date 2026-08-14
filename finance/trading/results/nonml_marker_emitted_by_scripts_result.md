# L'encart « dépendant du dépôt », émis par les scripts (pré-enregistré)

**Cycle de MODIFICATION**, septième après les #445 → #450.

## Critère 4 — le périmètre réel, et l'écart au backlog

Le backlog annonçait « **6 autres** rapports condamnés ». Rétabli **par
lecture**, le périmètre est tout autre :

| Catégorie | Nombre |
|---|---|
| rapport **portant** l'encart, script ne l'émettant pas | **1** |
| rapport dont le script **l'émet déjà** (rien à faire) | **1** |
| rapport qui **cite** l'encart sans le porter | **1** |
| rapports **effacés au #450**, à rétablir | **4** |

**Le chiffre de 6 était faux.** Il comptait comme « marqués » des rapports
qui **parlent** de l'encart — dont celui du #450, qui le reproduit pour
l'expliquer. C'est le même défaut « code contre discours sur le code » que
les #446 à #449 ont corrigé ailleurs, ici dans un **compte de backlog**.

**Prédiction vérifiée** : j'annonçais un périmètre plus petit que 6, sans
savoir combien. Il y en a **1** au sens strict.

> **Une ambiguïté de mon propre pré-enregistrement, signalée.** Sa définition
> du périmètre — *« le fichier le contient hors citation »* — **exclut**, lue
> au mot, les 4 rapports effacés au #450, puisqu'ils ne contiennent plus rien.
> Or c'est précisément pour eux que le cycle existe. J'ai tranché en faveur de
> l'objet du cycle et **je le dis** : les 4 sont inclus. Les exclure aurait été
> respecter la lettre d'une phrase que j'avais mal écrite, tout en laissant
> intact le défaut que le cycle prétend corriger.

## Critère 2 — la survie à la régénération

C'est le cœur du cycle : chaque script est exécuté **deux fois de suite**, et
l'encart doit être présent **après les deux**. Le marquage du #439 échouait
exactement ici.

| Script | Origine | Exécute | Encart après 1ʳᵉ | après 2ᵉ | Autres lignes modifiées |
|---|---|---|---|---|---|
| `nonml_reproducibility_campaign_v2_backtest.py` | porteur (#439) | ✔ | 1 | 1 | 109 |
| `nonml_capitulation_gate_floor_sweep_backtest.py` | effacé au #450 | ✔ | 1 | 1 | 3 |
| `nonml_empty_pass_basket_extension_backtest.py` | effacé au #450 | ✔ | 1 | 1 | 3 |
| `nonml_empty_pass_requalification_backtest.py` | effacé au #450 | ✔ | 1 | 1 | 3 |
| `nonml_protocol_inventory_backtest.py` | effacé au #450 | ✔ | 1 | 1 | 10 |

- l'encart **survit** aux deux exécutions partout : **OUI**
- **aucun doublon** : **OUI**

## Critère 1 — diff confiné

Une insertion par script, **+7 / −0**, immédiatement avant l'écriture du
fichier. Le texte est repris **mot pour mot** du #439 : le reformuler aurait
fait de ce cycle une réécriture déguisée.

- `nonml_reproducibility_campaign_v2_backtest.py` : **+7 / −0**
- `nonml_capitulation_gate_floor_sweep_backtest.py` : **+7 / −0**
- `nonml_empty_pass_basket_extension_backtest.py` : **+7 / −0**
- `nonml_empty_pass_requalification_backtest.py` : **+7 / −0**
- `nonml_protocol_inventory_backtest.py` : **+7 / −0**

**Confiné : OUI.**

## Critère 5 — l'ajout ne déplace rien d'autre

La colonne « autres lignes modifiées » compare le rapport **encart retiré**
à sa baseline. Ce qui y figure est de la **dérive du dépôt**, pas un effet de
l'encart — les scripts régénérés au #450 recomptent un dépôt qui a grossi
depuis.

## Verdict

| | Critère | État |
|---|---|---|
| 1 | diff confiné (+7/−0 par script) | ✔ |
| 2 | l'encart survit à la régénération | ✔ |
| 3 | aucun doublon | ✔ |
| 4 | périmètre réel publié, écart au backlog dit | ✔ |
| 5 | rien d'autre déplacé par l'ajout | ✔ |

### **PASS**

Le défaut structurel que le #450 avait mis au jour est corrigé : l'encart
**appartient désormais au script**, et une régénération le reproduit au lieu
de l'effacer.

**Ce n'est pas un résultat de stratégie**, et l'encart lui-même ne prouve
rien : il **avertit** un lecteur qu'un rapport dépend de l'état du dépôt.
Sa seule vertu est de ne plus disparaître au premier lavage.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).