# Réparer les deux scripts auto-inclusifs (pré-enregistré)

**Premier cycle de RÉPARATION de la série.** Le #463 avait trouvé les
défauts sans les corriger et le #466 avait refusé de le faire :
l'engagement depuis le #450 est de **ne pas mêler la découverte d'un
défaut à sa correction**. Ici le cycle **ne fait que réparer**.

## 1. Idempotence après correction — **trois** passages

Trois, pas deux : le #467 a montré qu'une dérive de **période 2** échappe
à deux passages.

| Script | P1 | P2 | P3 | Verdict |
|---|---|---|---|---|
| `verdict_rule_propagation` | `5dbb1e74be` | `5dbb1e74be` | `5dbb1e74be` | **stable** |
| `six_reports_regeneration` | `3e954b0633` | `3e954b0633` | `3e954b0633` | **stable** |

**Les deux sont idempotents.** La correction tient, et le diagnostic
du #463 — l'auto-inclusion — était bien la cause **unique**.

## 2. L'effet de la correction sur les rapports

Comparaison au rapport **tel qu'il était au commit épinglé** (`814e373`) — jamais au fichier du disque, leçon des #445 et #451.

### `verdict_rule_propagation`

Lignes de diff : **36** *(les 20 premières)*

```diff
--- avant (épinglé)
+++ après correction
@@ -25,6 +25,6 @@
-- `nonml_capitulation_gate_floor_sweep_backtest.py` — diff **+3 / −1**
-- `nonml_empty_pass_basket_extension_backtest.py` — diff **+3 / −1**
-- `nonml_empty_pass_requalification_backtest.py` — diff **+3 / −1**
-- `nonml_pnl_persistence_lot4_audit.py` — diff **+3 / −1**
-- `nonml_protocol_inventory_backtest.py` — diff **+3 / −1**
-- `nonml_sameday_timestamp_resolution_backtest.py` — diff **+3 / −1**
+- `nonml_capitulation_gate_floor_sweep_backtest.py` — diff **+— / −—**
+- `nonml_empty_pass_basket_extension_backtest.py` — diff **+— / −—**
+- `nonml_empty_pass_requalification_backtest.py` — diff **+— / −—**
+- `nonml_pnl_persistence_lot4_audit.py` — diff **+— / −—**
+- `nonml_protocol_inventory_backtest.py` — diff **+— / −—**
+- `nonml_sameday_timestamp_resolution_backtest.py` — diff **+— / −—**
@@ -59 +59 @@
-- rapports comparés : **303**
+- rapports comparés : **322**
@@ -70 +70 @@
-**Confiné : OUI.**
```

### `six_reports_regeneration`

Lignes de diff : **117** *(les 20 premières)*

```diff
--- avant (épinglé)
+++ après correction
@@ -17,6 +17,6 @@
-| `nonml_capitulation_gate_floor_sweep_backtest.py` | `3acd787` | 0 | 2 | régénéré |
-| `nonml_empty_pass_basket_extension_backtest.py` | `3acd787` | 1 | 6 | régénéré |
-| `nonml_empty_pass_requalification_backtest.py` | `3acd787` | 1 | 3 | régénéré |
-| `nonml_pnl_persistence_lot4_audit.py` | `d0f42ed` | 0 | 1 | régénéré |
-| `nonml_protocol_inventory_backtest.py` | `3acd787` | 3 | 6 | régénéré |
-| `nonml_sameday_timestamp_resolution_backtest.py` | `aa498f1` | 0 | 0 | régénéré |
+| `nonml_capitulation_gate_floor_sweep_backtest.py` | `afe8ea1` | 0 | 1 | régénéré |
+| `nonml_empty_pass_basket_extension_backtest.py` | `afe8ea1` | 0 | 2 | régénéré |
+| `nonml_empty_pass_requalification_backtest.py` | `afe8ea1` | 1 | 2 | régénéré |
+| `nonml_pnl_persistence_lot4_audit.py` | `bbe5165` | 0 | 1 | régénéré |
+| `nonml_protocol_inventory_backtest.py` | `d1cfb75` | 3 | 6 | régénéré |
+| `nonml_sameday_timestamp_resolution_backtest.py` | `aa498f1` | 0 | 3 | régénéré |
@@ -25,2 +25,2 @@
-- groupes de diff imputables à **la règle** : **5**
-- groupes imputables à la **dérive du dépôt** : **18**
+- groupes de diff imputables à **la règle** : **4**
+- groupes imputables à la **dérive du dépôt** : **15**
```

## 2 bis. L'effet du correctif, **isolé** de la dérive

Épingler le texte du rapport « avant » **n'isole pas** l'effet du
correctif : la sortie dépend de l'état **courant** du dépôt. Le passage
de « 303 rapports comparés » à « 321 » ci-dessus est de la **dérive**,
pas ma correction — le défaut que les #449/#450/#451 avaient déjà
rencontré, et que mon pré-enregistrement n'avait pas anticipé.

Les **deux versions** sont donc exécutées au **même état de dépôt**, et
leurs sorties comparées entre elles.

### `verdict_rule_propagation`

Lignes de diff : **10**

```diff
--- ancienne version
+++ version corrigée
@@ -59 +59 @@
-- rapports comparés : **323**
+- rapports comparés : **322**
@@ -79 +79 @@
-Sur les **323** rapports du dépôt, **9** changent de
+Sur les **322** rapports du dépôt, **8** changent de
@@ -92 +91,0 @@
-| `verdict_rule_propagation` | PASS | **FAIL** |
```

### `six_reports_regeneration`

Lignes de diff : **35** *(les 16 premières)*

```diff
--- ancienne version
+++ version corrigée
@@ -30,2 +30,2 @@
-- rapports réécrits : **9**
-- **hors des six déclarés** : **3**
+- rapports réécrits : **8**
+- **hors des six déclarés** : **2**
@@ -34 +33,0 @@
-- `nonml_six_reports_regeneration_result.md`
@@ -74,25 +72,0 @@
-
-## Un effet de bord découvert — les marqueurs du #439 sont effacés
-
-**1** rapports perdent, en étant régénérés, l'encart que le
-#439 leur avait ajouté :
-
```

> **C'est ce diff-là qui mesure la correction**, et lui seul.

## 3. Le diff du code — confiné au régime déclaré ?

Le régime annonçait : **une expression par script**, des commentaires,
**aucun import**, **aucune autre ligne**.

| Fichier | + | − |
|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` | 6 | 1 |
| `nonml_verdict_rule_propagation_backtest.py` | 6 | 1 |

- fichiers hors régime : **0**

**Confiné : OUI.**

## 4. La régénération, bornée

`six_reports_regeneration` **écrit 7 rapports qui ne sont pas le sien**
(#463). Ils ont donc été réécrits pendant la mesure, puis **restaurés** :
committer leur régénération mêlerait l'effet de la correction à la dérive
du dépôt, ce que le #450 a payé cher.

> **La restauration a lieu après TOUTE exécution**, section 2 bis
> comprise. Dans une première version elle la précédait, et le critère 4
> annonçait « 0 résidu » **sur un arbre sale** — le défaut d'ordre
> d'exécution qui avait déjà vidé un contrôle au #446 et faussé le #451.

- rapports tiers restaurés : **7**
  - `nonml_capitulation_gate_floor_sweep_result.md`
  - `nonml_empty_pass_basket_extension_result.md`
  - `nonml_empty_pass_requalification_result.md`
  - `nonml_pnl_duplicate_sweep_result.md`
  - `nonml_pnl_persistence_lot4_audit.md`
  - `nonml_protocol_inventory_result.md`
  - `nonml_sameday_timestamp_resolution_result.md`
- **résidus hors des fichiers autorisés** : **0**

## Mes trois prédictions, confrontées

| Prédiction | Mesuré | Verdict |
|---|---|---|
| les deux deviennent idempotents sur 3 passages | oui | **vérifiée** |
| leurs compteurs baissent d'exactement 1 | *voir les diffs* | *à lire* |
| aucun autre fichier suivi ne reste modifié | 0 | **vérifiée** |

## Critères de succès

1. Les 2 scripts idempotents sur 3 passages — **OUI**.
2. Diff de code confiné au régime — **OUI**.
3. Effet sur les 2 rapports publié avec son diff — **OUI**.
4. Arbre propre hors des fichiers du cycle — **OUI**.

**PASS**

## Ce que ce cycle ne fait pas

- Il ne **touche** à aucun autre script, même signalé par le #466 : ces
  signalements sont **sans valeur démontrée** (#467, **0/6**).
- Il ne **committe** aucun rapport tiers régénéré.
- Il ne **réécrit** aucun verdict de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).