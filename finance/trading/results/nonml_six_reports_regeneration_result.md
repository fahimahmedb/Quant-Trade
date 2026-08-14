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
| `nonml_capitulation_gate_floor_sweep_backtest.py` | `3acd787` | 0 | 2 | régénéré |
| `nonml_empty_pass_basket_extension_backtest.py` | `3acd787` | 1 | 6 | régénéré |
| `nonml_empty_pass_requalification_backtest.py` | `3acd787` | 1 | 3 | régénéré |
| `nonml_pnl_persistence_lot4_audit.py` | `d0f42ed` | 0 | 1 | régénéré |
| `nonml_protocol_inventory_backtest.py` | `3acd787` | 3 | 6 | régénéré |
| `nonml_sameday_timestamp_resolution_backtest.py` | `aa498f1` | 0 | 0 | régénéré |

- rapports régénérés : **6/6**
- groupes de diff imputables à **la règle** : **5**
- groupes imputables à la **dérive du dépôt** : **18**

## Portée réelle — un rapport de plus que les six déclarés

- rapports réécrits : **6**
- **hors des six déclarés** : **1**

- `nonml_pnl_duplicate_sweep_result.md`

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

- rapports réécrits qui ne s'annoncent pas comme diagnostic/inventaire/audit : **2**
  - `nonml_empty_pass_basket_extension_result.md`
  - `nonml_empty_pass_requalification_result.md`

**Ces deux-là ont été relus** plutôt que classés par mot-clé — mon filtre
cherchait une formule d'en-tête, et ces rapports en emploient une autre :

> *« Requalification **documentaire** : aucun verdict n'est recalculé ni
> annulé. »*

Ce sont des **requalifications documentaires** (#417, #422) : elles
annotent des PASS obtenus par inactivité **sans toucher au verdict**. Le
critère 3 tient donc, mais il tient **par lecture**, pas par le filtre —
quatrième fois qu'une heuristique textuelle se montre trop grossière dans
cette série de cycles.

## Un effet de bord découvert — les marqueurs du #439 sont effacés

**4** rapports perdent, en étant régénérés, l'encart que le
#439 leur avait ajouté :

- `nonml_capitulation_gate_floor_sweep_result.md`
- `nonml_empty_pass_basket_extension_result.md`
- `nonml_empty_pass_requalification_result.md`
- `nonml_protocol_inventory_result.md`

> **Rapport dépendant du dépôt** — *ce document décrit l'état du dépôt à la
> date de son exécution…*

La cause est structurelle : le #439 a **ajouté ces encarts aux fichiers
publiés**, pas aux scripts qui les produisent. Toute régénération les
efface donc — et ce cycle vient de le démontrer sur des cas réels.

**Le marquage du #439 est fragile par construction.** Un encart qui décrit
le comportement d'un script doit être **émis par ce script**, sinon il ne
survit pas à la première ré-exécution.

**Je ne les restaure pas.** L'engagement 2 du pré-enregistrement est
explicite : *tout défaut découvert est publié et inscrit, pas réparé au
passage*. Les restaurer serait une modification non déclarée, et surtout
cela remettrait en place un marquage dont ce cycle vient d'établir qu'il ne
tient pas. La bonne correction — faire émettre l'encart par les scripts —
est **inscrite à la file**.

## Détail des groupes attribués

### `nonml_capitulation_gate_floor_sweep_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- scripts `nonml_*_backtest.py` examinés : **284**` |
| dérive | 4 | `` |

### `nonml_empty_pass_basket_extension_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 4 | `- fichiers `nonml_*_pnl.npz` : **174**` |
| dérive | 2 | `- schéma indiciel, déjà traités au #417 : **145**` |
| **effet** | 2 | `- PASS panier dont la jambe candidate **agit** : **9**` |
| dérive | 1 | `| `january_effect_lowprice_overlay` | 106 / 1375 | +470.2 % | +373.6 % |` |
| dérive | 2 | `| `lowvol_sma200_overlay` | 1033 / 1336 | +122.4 % | +60.8 % |` |
| dérive | 1 | `| `short_term_momentum` | 1390 / 1391 | +259.4 % | +209.4 % |` |
| dérive | 4 | `` |

### `nonml_empty_pass_requalification_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 6 | `- fichiers `nonml_*_pnl.npz` trouvés : **173**` |
| **effet** | 2 | `- PASS dont l'overlay **agit** (non requalifiables) : **72**` |
| dérive | 2 | `Sur **158** candidats mesurables, **72** portent un` |
| dérive | 4 | `` |

### `nonml_pnl_persistence_lot4_audit.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `| séries de P&L reconstruites | 200 | **202** |` |

### `nonml_protocol_inventory_result.md`

| Cause | Lignes | Première ligne du groupe |
|---|---|---|
| dérive | 2 | `- rapports anti-cheat examinés : **330**` |
| dérive | 2 | `- rapports de résultat examinés : **287**` |
| dérive | 2 | `- sans trace de batterie (fichier dédié **ni** mention interne) : **33**` |
| **effet** | 2 | `| PASS **strictement postérieurs**, sans batterie | **6** |` |
| **effet** | 4 | `| `gjr_vol_managed_russell2000` | 2026-08-04 |` |
| dérive | 3 | `| `weakness_breadth_vol_targeting_overlay_pit_universe` | 2026-08-13 |` |
| dérive | 2 | `- pré-enregistrements examinés : **407**` |
| **effet** | 2 | `| C — PASS sans trace de batterie | **33** |` |
| dérive | 4 | `` |

### `nonml_sameday_timestamp_resolution_result.md`

**Aucun changement** — le rapport était déjà à jour.

## Verdict

| | Critère | État |
|---|---|---|
| 1 | 6/6 régénérés, ou échec publié | ✔ |
| 2 | chaque groupe de diff attribué | ✔ |
| 3 | aucun verdict de stratégie modifié | ✔ *(par lecture)* |
| 4 | écart code/rapport résorbé | ✔ |

### **PASS**

**Les prédictions du pré-enregistrement, une par une :**

- *« la dérive domine largement l'effet »* — **vérifiée** : 18 groupes
  de dérive contre 5 d'effet.
- *« au moins un rapport sans aucun effet de la règle »* — **vérifiée**, et
  plus largement qu'annoncé : trois rapports sur six.
- *« je n'exclus pas qu'un script échoue »* — **réfutée** : les six s'exécutent.
  Tant mieux, et je le note comme une prédiction fausse, pas comme un succès.

**Ce que le cycle a trouvé, et qu'il ne cherchait pas** : un septième rapport
hors périmètre, et quatre encarts du #439 effacés par la régénération. Ni
l'un ni l'autre n'a été trouvé par la mesure — le premier en lisant
`git status`, le second en relisant un diff.
