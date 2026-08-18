# La convention est-elle **en train de mourir** ? (pré-enregistré)

Le **#486** avait observé **33** déclarés apparus le 13/08, puis **0**
sur les 5 derniers, et inscrit la question sans la trancher.

## Les deux règles, citées verbatim

```python
LITTERALE = r"Cycle d[e\'’]\s*\*\*([^*]+)\*\*"        # celle du #483
TOLERANTE = r"\*\*Cycle d[e\'’]\s*([^*]+)\*\*|Cycle d[e\'’]\s*\*\*([^*]+)\*\*"
```

La tolérante accepte **les deux mises en forme** — le mot seul en gras,
ou la phrase entière — **et rien d'autre**. Elle n'élargit pas la notion
de déclaration, seulement sa typographie.

## Les deux comptes, côte à côte

| Règle | Déclarés sur l'ensemble | Part parmi les 20 plus récents |
|---|---|---|
| **littérale** *(#483)* | **34 / 467** | **5,0 %** |
| **tolérante** | **72 / 467** | **95,0 %** |
| *écart* | *+38* | *90,0 points* |

## La chronologie, sous les deux règles

| Tranche | Période | Littérale | Tolérante |
|---|---|---|---|
| 1–77 | 28/07/2026 → 29/07/2026 | **0 / 77** | **0 / 77** |
| 78–154 | 29/07/2026 → 30/07/2026 | **0 / 77** | **0 / 77** |
| 155–231 | 30/07/2026 → 05/08/2026 | **0 / 77** | **0 / 77** |
| 232–308 | 05/08/2026 → 06/08/2026 | **0 / 77** | **0 / 77** |
| 309–385 | 06/08/2026 → 13/08/2026 | **2 / 77** | **2 / 77** |
| 386–462 | 13/08/2026 → 18/08/2026 | **32 / 77** | **65 / 77** |
| 463–467 | 18/08/2026 → 18/08/2026 | **0 / 5** | **5 / 5** |

## Les cinq derniers cycles, nommés

*Critère 5 : ce sont les miens, et ce sont eux qui font le constat du
#486. Ils doivent être nommés un par un.*

| Cycle | Littérale | Tolérante | Déclaration lue |
|---|---|---|---|
| `masking_guards_witness_patch` | **non** | **oui** | « MODIFICATION » |
| `duplicate_sweep_irreparability` | **non** | **oui** | « VÉRIFICATION » |
| `remaining_masking_guards_patch` | **non** | **oui** | « MODIFICATION » |
| `battery_witness_hoist` | **non** | **oui** | « MODIFICATION » |
| `battery_indet_hoist_declared` | **non** | **oui** | « MODIFICATION » |

- détectés par la **tolérante seule** : **5 / 5**

## La lecture retenue

Le critère, **fixé avant mesure** : **B** si `T − L ≥ 30 points` ;
**A** si `T < 30 %` et `T − L < 30 points` ; **C** sinon.

> ### **B** — **Artefact de format** — c'est le détecteur qui décroche

**La convention n'est pas morte : elle a changé de typographie.** Les
cycles récents écrivent `**Cycle de MODIFICATION**` — la phrase
entière en gras — au lieu de `Cycle de **MODIFICATION**`. **Ils
déclarent exactement la même chose**, et la règle du #483 ne les voit
pas.

> **Le constat du #486 est nuancé, pas réécrit.** Son « 0 sur les 5
> derniers » était **exact sous sa règle** ; il mesurait la couverture
> d'un détecteur, pas l'état d'une pratique.

**C'est l'hypothèse qui m'arrangeait, et elle se vérifie.** Je la
publie donc avec la réserve qui s'impose : je l'avais formulée avant
de mesurer, mais **c'est moi qui écris les cycles dont il s'agit**, et
j'avais toute latitude pour deviner juste. **Le fait mesurable — deux
mises en forme pour une même déclaration — est vérifiable par un
tiers ; mon mérite à l'avoir prédit ne l'est pas.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| lecture B retenue | B | B | **vérifiée** |
| les 5 derniers : tolérante seule | 5 | 5 | **vérifiée** |
| +5 déclarés au moins | ≥ 5 | +38 | **vérifiée** |

## Ce que cela change au compte du #486

- déclarés selon le #483/#486 : **34**
- déclarés en acceptant les deux typographies : **72**

**Aucun chiffre du #486 n'est faux** : il comptait ce que sa règle
voyait, et il l'a dit. **Ce cycle ajoute que la règle voyait moins que la
pratique.**

> La règle du #483 **n'est pas modifiée** dans les autres cycles : la
> tolérante n'existe que dans ce rapport. La changer partout serait une
> modification non déclarée, et elle mériterait son propre cycle.

## Critères de succès

1. Deux règles citées verbatim, comptes côte à côte — **OUI**.
2. Chronologie publiée sous les deux règles — **OUI**.
3. Une lecture nommée par le critère chiffré — **OUI** (**B**).
4. Constat du #486 nuancé sans réécriture — **OUI**.
5. Les 5 derniers cycles nommés individuellement — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date
> de son exécution (cycles #436-#438).