# L'idempotence des rapports (pré-enregistré)

Le contrôle D du #461 a trouvé **un** rapport qui changeait d'une
exécution à l'autre — **par accident**, en vérifiant autre chose, comme
les quatre faux du backlog. Ce cycle pose la question directement :
**combien d'autres ?**

## La limite, rappelée avant les chiffres

Le dépôt compte **314** `nonml_*_backtest.py`. J'en éprouve **18**,
soit **5,7 %** — ceux des entrées #443-#460, même univers figé que les #461
et #462.

> **Rien ici ne se généralise aux 314.** Et deux exécutions consécutives
> ne sondent qu'une partie des sources de non-déterminisme : elles
> attrapent l'ordre d'itération et l'horloge, pas ce qui dépendrait de
> l'état du dépôt ou d'un autre interpréteur.

## Le résultat

- scripts de l'univers : **18**
- **éprouvés** : **18**
- écartés (budget, erreur, sans rapport) : **0**
- **non idempotents** : **3**

## Les deux empreintes, script par script

| Script | État | Passage 1 | Passage 2 |
|---|---|---|---|
| `npz_report_consistency_baskets` | idempotent | `acd2d1c3f1534fde` | `acd2d1c3f1534fde` |
| `third_npz_schema_handling` | idempotent | `87261f88f5989110` | `87261f88f5989110` |
| `net_pnl_correction` | idempotent | `ccb983e709e208ef` | `ccb983e709e208ef` |
| `sweep_pass_prose_fix` | idempotent | `5c9202475350b6ce` | `5c9202475350b6ce` |
| `verdict_detector_fix` | idempotent | `5b7537a8f3fe60c3` | `5b7537a8f3fe60c3` |
| `verdict_detector_complete` | idempotent | `c68f175b803e72c1` | `c68f175b803e72c1` |
| `verdict_rule_propagation` | **NON IDEMPOTENT** | `c603aec92e8991c7` | `4a1a99cd5b3ffae7` |
| `six_reports_regeneration` | **NON IDEMPOTENT** | `ee4012c7de11cbd3` | `fa9c5337ed3ad96f` |
| `marker_emitted_by_scripts` | **NON IDEMPOTENT** | `e64770ab06654398` | `a73d86149ff17ff4` |
| `tom_decomposition_npz` | idempotent | `587d25586bd61988` | `587d25586bd61988` |
| `orphan_npz_inspection` | idempotent | `0b261051a3e3c856` | `0b261051a3e3c856` |
| `verdict_variant_decision` | idempotent | `e81a208ad16c11a7` | `e81a208ad16c11a7` |
| `silent_skip_decision` | idempotent | `d20faaf2ec19e500` | `d20faaf2ec19e500` |
| `dsr_corrected_trials` | idempotent | `9f9d6ba01db87c9e` | `9f9d6ba01db87c9e` |
| `battery_coverage` | idempotent | `b3a872fee4664afb` | `b3a872fee4664afb` |
| `temporal_holdout` | idempotent | `ea7077a56401b543` | `ea7077a56401b543` |
| `relative_holdout` | idempotent | `cb38da520d6793b2` | `cb38da520d6793b2` |
| `verdict_rule_battery` | idempotent | `728414762c831251` | `728414762c831251` |

## Le défaut que je portais moi-même

> **Mon propre rapport n'était pas idempotent**, et c'est le contrôle D de
> l'audit qui l'a établi — pas moi.

La cause est **exactement celle que ce cycle mesure chez les autres** :
ce rapport fait partie du corpus que `verdict_rule_propagation` et
`six_reports_regeneration` recomptent quand je les exécute, donc son
contenu dépendait de sa propre version précédente.

Corrigé en supprimant ma sortie **avant** de mesurer — la correction que
le **#446** avait trouvée, que le **#447** avait énoncée, et que je ne
m'étais pas appliquée. **Un cycle qui dénonce un défaut en le portant
n'aurait pas dû être publié tel quel.**

## Les rapports non idempotents — avec le diff qui le prouve

### `verdict_rule_propagation`

Lignes de diff : **7**

```diff
--- passage 1
+++ passage 2
@@ -79 +79 @@
-Sur les **317** rapports du dépôt, **9** changent de
+Sur les **317** rapports du dépôt, **10** changent de
@@ -92,0 +93 @@
+| `verdict_rule_propagation` | PASS | **FAIL** |
```

### `six_reports_regeneration`

Lignes de diff : **35** *(les 12 premières)*

```diff
--- passage 1
+++ passage 2
@@ -30,2 +30,2 @@
-- rapports réécrits : **13**
-- **hors des six déclarés** : **7**
+- rapports réécrits : **14**
+- **hors des six déclarés** : **8**
@@ -34,0 +35 @@
+- `nonml_six_reports_regeneration_result.md`
@@ -77,0 +79,25 @@
+
+## Un effet de bord découvert — les marqueurs du #439 sont effacés
```

### `marker_emitted_by_scripts`

Lignes de diff : **5**

```diff
--- passage 1
+++ passage 2
@@ -41 +41 @@
-| `nonml_reproducibility_campaign_v2_backtest.py` | porteur (#439) | ✔ | 1 | 1 | 143 |
+| `nonml_reproducibility_campaign_v2_backtest.py` | porteur (#439) | ✔ | 1 | 1 | 141 |
```

## L'effet de bord, annulé

Rejouer ces scripts **réécrit leurs rapports**. Le #450 a montré ce que
coûte une régénération non maîtrisée. L'arbre a donc été restauré.

- rapports touchés **pendant** la mesure : **18**
- résidus sous `results/` **après** restauration : **0**

**Ce cycle ne committe que son propre rapport.**

### Des scripts qui écrivent le rapport d'un **autre** cycle

> **Relevé ajouté après le premier passage**, et signalé comme tel. Le
> critère 4 ne regardait l'arbre qu'**après** restauration : la trace de
> ces écritures disparaissait avant d'avoir été relevée. Ni le protocole
> ni les critères ne changent.

**8** rapport(s) réécrit(s) alors qu'aucun des
**18** scripts éprouvés ne leur correspond :

- `nonml_capitulation_gate_floor_sweep_result.md`
- `nonml_empty_pass_basket_extension_result.md`
- `nonml_empty_pass_requalification_result.md`
- `nonml_pnl_duplicate_sweep_result.md`
- `nonml_pnl_persistence_lot4_audit.md`
- `nonml_protocol_inventory_result.md`
- `nonml_reproducibility_campaign_v2_result.md`
- `nonml_sameday_timestamp_resolution_result.md`

Autrement dit, **un script du lot écrit ailleurs que dans son propre
rapport**. C'est le couplage même que le #450 a payé cher — une
régénération qui touche ce qu'on ne surveillait pas. Publié, **pas
réparé** : l'engagement depuis le #450 est d'inscrire, pas de corriger
au passage.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 1 script non idempotent | ≥ 1 | 3 | **vérifiée** |
| ≥ 12 tiennent dans le budget | ≥ 12 | 18 | **vérifiée** |
| la dérive porte sur l'étiquetage, pas les compteurs | étiquettes | **les compteurs** | **réfutée** |

**La prédiction 3 est réfutée, et c'est la partie instructive.** Je
m'attendais à une dérive cosmétique, comme celle du #461. Ce sont les
**compteurs** qui bougent — `9 → 10`, `13 → 14`.

### Les deux cas sont **le même défaut**, et il a déjà un nom

> **Un rapport qui compte des rapports se compte lui-même** au second
> passage, s'il ne s'exclut pas du corpus.

C'est exactement ce que le **#447** avait énoncé et ce que le **#446**
avait corrigé en supprimant son propre fichier de sortie avant de
mesurer. **Deux scripts portent encore le défaut** que ces cycles-là
avaient identifié — la leçon avait été tirée sans être propagée.

Ce n'est pas une non-idempotence bénigne : `verdict_rule_propagation`
s'ajoute à **sa propre table de reclassement**, avec un verdict
`PASS → FAIL` qui n'existait pas au premier passage.

## Critères de succès

1. **18/18** scripts traités ou classés — **OUI**.
2. Les deux empreintes publiées pour chaque script éprouvé — **OUI**.
3. Tout non-idempotent publié avec son diff — **OUI**.
4. Arbre propre sous `results/` après restauration — **OUI**.

**PASS** — le critère porte sur le **procédé** : un cycle qui ne
trouve rien et le montre proprement réussit.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).