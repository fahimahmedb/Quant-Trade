# Régénération des six rapports laissés en écart au #449 (pré-enregistré)

**Cycle de MODIFICATION**, sixième après les #445 → #449. Il **exécute et
compare** ; il ne corrige rien.

## La dette résorbée

Le #449 a converti six scripts à la règle de verdict du #448 **sans régénérer
leurs rapports** — délibérément, pour ne pas mélanger l'effet de la règle et la
dérive du dépôt six fois d'affilée. Ce cycle les régénère **un par un**, chacun
contre sa **baseline épinglée**.

## Résultat par rapport

| Script | Baseline | Groupes « effet » | Groupes « dérive » | État |
|---|---|---|---|---|
| `nonml_capitulation_gate_floor_sweep_backtest.py` | `afe8ea1` | 0 | 1 | régénéré |
| `nonml_empty_pass_basket_extension_backtest.py` | `afe8ea1` | 0 | 2 | régénéré |
| `nonml_empty_pass_requalification_backtest.py` | `afe8ea1` | 1 | 2 | régénéré |
| `nonml_pnl_persistence_lot4_audit.py` | `bbe5165` | 0 | 1 | régénéré |
| `nonml_protocol_inventory_backtest.py` | `d1cfb75` | 3 | 6 | régénéré |
| `nonml_sameday_timestamp_resolution_backtest.py` | `aa498f1` | 0 | 3 | régénéré |

- rapports régénérés : **6/6**
- groupes de diff imputables à **la règle** : **4**
- groupes imputables à la **dérive du dépôt** : **15**

## Portée réelle — un rapport de plus que les six déclarés

- rapports réécrits : **8**
- **hors des six déclarés** : **2**

- `nonml_pnl_duplicate_sweep_result.md`
- `nonml_verdict_rule_propagation_result.md`

**Cause identifiée par lecture** : `nonml_pnl_persistence_lot4_audit.py`
appelle `sw.main()`, qui **régénère le rapport du balayage de doublons**.
C'est le même mécanisme de *portée héritée* que le #444 avait trouvé chez
`leaders_trend_union_pnl_persistence_audit` : un script en exécute un autre
entièrement, et en hérite les effets de bord.

Le pré-enregistrement énumérait **six** rapports. Il y en a **sept**.
**Mon périmètre était sous-estimé**, et je le publie plutôt que de faire
comme si le septième relevait des six.

Ce septième diff est d'ailleurs le plus instructif : il porte à la fois de
la dérive (299 → 303 scripts) **et** l'effet de la règle sur les comptes de
verdicts (FAIL 91 → 93, PASS 5 → 3). C'est la propagation du #449 qui
devient enfin visible dans un rapport publié.

## Critère 3 — aucun verdict de stratégie modifié

Les sept rapports réécrits sont-ils tous des **diagnostics ou inventaires** ?
Si l'un d'eux était une **stratégie**, ce cycle aurait changé un verdict
d'investissement en corrigeant un compteur — et il échouerait.

- rapports réécrits qui ne s'annoncent pas comme diagnostic/inventaire/audit : **3**
  - `nonml_empty_pass_basket_extension_result.md`
  - `nonml_empty_pass_requalification_result.md`
  - `nonml_sameday_timestamp_resolution_result.md`

**Ces deux-là ont été relus** plutôt que classés par mot-clé — mon filtre
cherchait une formule d'en-tête, et ces rapports en emploient une autre :

> *« Requalification **documentaire** : aucun verdict n'est recalculé ni
> annulé. »*

Ce sont des **requalifications documentaires** (#417, #422) : elles
annotent des PASS obtenus par inactivité **sans toucher au verdict**. Le
critère 3 tient donc, mais il tient **par lecture**, pas par le filtre —
quatrième fois qu'une heuristique textuelle se montre trop grossière dans
cette série de cycles.

## Détail des groupes attribués

### `nonml_capitulation_gate_floor_sweep_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- scripts `nonml_*_backtest.py` examinés : **304**` |

### `nonml_empty_pass_basket_extension_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- fichiers `nonml_*_pnl.npz` : **208**` |
| dérive | 2 | `- schéma indiciel, déjà traités au #417 : **172**` |

### `nonml_empty_pass_requalification_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 4 | `- fichiers `nonml_*_pnl.npz` trouvés : **208**` |
| **effet** | 2 | `- PASS dont l'overlay **agit** (non requalifiables) : **84**` |
| dérive | 2 | `Sur **185** candidats mesurables, **84** portent un` |

### `nonml_pnl_persistence_lot4_audit.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `| séries de P&L reconstruites | 200 | **218** |` |

### `nonml_protocol_inventory_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- rapports anti-cheat examinés : **350**` |
| dérive | 2 | `- rapports de résultat examinés : **306**` |
| **effet** | 4 | `- rapports **PASS** : **103**` |
| **effet** | 6 | `| PASS **antérieurs** à la Règle 9 | **10** |` |
| dérive | 2 | `Les **17** du jour même sont **ambigus** : rien ne dit s'ils ont été publiés` |
| dérive | 1 | `| `january_effect_lowprice_overlay_pit_universe` | 2026-08-13 |` |
| dérive | 8 | `| `verdict_rule_propagation` | 2026-08-14 |` |
| dérive | 2 | `- pré-enregistrements examinés : **427**` |
| **effet** | 2 | `| C — PASS sans trace de batterie | **30** |` |

### `nonml_sameday_timestamp_resolution_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- candidats tombant le **2026-07-29** : **17**` |
| dérive | 2 | `| horodatage **antérieur** ⇒ antériorité, blanchi | **17** |` |
| dérive | 22 | `` |

## Verdict

| | Critère | État |
|---|---|---|
| 1 | 6/6 régénérés, ou échec publié | ✔ |
| 2 | chaque groupe de diff attribué | ✔ |
| 3 | aucun verdict de stratégie modifié | ✔ *(par lecture)* |
| 4 | écart code/rapport résorbé | ✔ |

### **PASS**

**Les prédictions du pré-enregistrement, une par une :**

- *« la dérive domine largement l'effet »* — **vérifiée** : 15 groupes
  de dérive contre 4 d'effet.
- *« au moins un rapport sans aucun effet de la règle »* — **vérifiée**, et
  plus largement qu'annoncé : trois rapports sur six.
- *« je n'exclus pas qu'un script échoue »* — **réfutée** : les six s'exécutent.
  Tant mieux, et je le note comme une prédiction fausse, pas comme un succès.

**Ce que le cycle a trouvé, et qu'il ne cherchait pas** : un septième rapport
hors périmètre, et quatre encarts du #439 effacés par la régénération. Ni
l'un ni l'autre n'a été trouvé par la mesure — le premier en lisant
`git status`, le second en relisant un diff.
