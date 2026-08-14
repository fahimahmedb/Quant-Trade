# Audit adversarial — idempotence des rapports (#463)

Le backtest compare **deux** passages. Cet audit pose les questions qu'un
tel résultat appelle et que deux passages ne peuvent pas trancher.

## A. Dérive perpétuelle, ou convergence en un pas ?

Si le passage 2 égale le passage 3, la non-idempotence n'est pas une
dérive sans fin : c'est une **convergence**, le rapport s'étant intégré
lui-même une bonne fois. **La lecture du résultat en dépend.**

| Script | P1 | P2 | P3 | Lecture |
|---|---|---|---|---|
| `verdict_rule_propagation` | `5d4e740d5f` | `9097520a9e` | `9097520a9e` | **convergence en un pas** |
| `six_reports_regeneration` | `967deebded` | `fc5270fdae` | `09ad5e79af` | **dérive perpétuelle** |


## B. Le mécanisme est-il bien l'auto-inclusion ?

Un rapport qui se compte lui-même doit **se nommer** dans son propre
texte au passage où il apparaît.

| Script | Se nomme dans son rapport | Verdict |
|---|---|---|
| `verdict_rule_propagation` | **oui** | auto-inclusion **confirmée** |
| `six_reports_regeneration` | **oui** | auto-inclusion **confirmée** |

**CONCORDANT** — le mécanisme annoncé par le
rapport est celui qu'on observe.

## C. Qui écrit les rapports hors périmètre ?

Le backtest constate **8** rapports réécrits sans dire par qui. On
attribue, en rejouant chaque suspect **seul**.

### `verdict_rule_propagation`

N'écrit **que** son propre rapport.

### `six_reports_regeneration`

Écrit **7** fichier(s) qui ne sont pas son rapport :

- `nonml_capitulation_gate_floor_sweep_result.md`
- `nonml_empty_pass_basket_extension_result.md`
- `nonml_empty_pass_requalification_result.md`
- `nonml_pnl_duplicate_sweep_result.md`
- `nonml_pnl_persistence_lot4_audit.md`
- `nonml_protocol_inventory_result.md`
- `nonml_sameday_timestamp_resolution_result.md`

**7** écriture(s) hors rapport propre attribuée(s) aux
deux suspects. Le reste vient d'autres scripts du lot, non attribué ici :
l'attribution complète demanderait 18 exécutions isolées, et **ce cycle
ne la promet pas**.

## D. Mon propre rapport est-il idempotent ?

- avant : `b82887f972ff5613`
- après : `b82887f972ff5613`

**CONCORDANT** — un cycle qui dénonce la
non-idempotence des autres doit commencer par la sienne.

## Ce que cet audit ne couvre pas

- Il n'attribue pas les **8** écritures hors périmètre à tous leurs
  auteurs — seulement à ceux qu'il a rejoués.
- Il ne teste que **3** passages : une dérive à période plus longue lui
  échapperait.
- Il ne dit rien des **296** scripts hors de l'univers.

## Verdict — **CONCORDANT**

Le mécanisme annoncé est confirmé, et ce cycle est idempotent.