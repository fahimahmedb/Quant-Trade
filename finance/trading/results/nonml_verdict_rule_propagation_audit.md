# Audit indépendant — propagation de la règle (#449)

**Critère 4** : aucune réimplémentation historique modifiée. Un cycle qui
corrige une règle partout risque d'écraser les scripts qui reproduisent
**volontairement** l'ancienne — et de détruire la mesure qu'ils portent.

## Contrôle 1 — les historiques ont-ils gardé l'ancienne règle ?

Recherche de la forme **exécutable** (`if`/`return` … `"**PASS" in `), pas
de la sous-chaîne : au #447 ce même contrôle s'était trompé en retrouvant la
règle dans un *commentaire* qui la citait.

| Script | Ancienne règle encore exécutable |
|---|---|
| `nonml_verdict_detector_fix_backtest.py` | **oui** |
| `nonml_verdict_detector_fix_audit.py` | **oui** |
| `nonml_sweep_pass_prose_fix_audit.py` | **oui** |

## Contrôle 2 — les convertis en sont-ils débarrassés ?

| Script | Ancienne règle absente | Importe le module |
|---|---|---|
| `nonml_capitulation_gate_floor_sweep_backtest.py` | ✔ | ✔ |
| `nonml_empty_pass_basket_extension_backtest.py` | ✔ | ✔ |
| `nonml_empty_pass_requalification_backtest.py` | ✔ | ✔ |
| `nonml_pnl_persistence_lot4_audit.py` | ✔ | ✔ |
| `nonml_protocol_inventory_backtest.py` | ✔ | ✔ |
| `nonml_sameday_timestamp_resolution_backtest.py` | ✔ | ✔ |

## Contrôle 3 — les convertis restent-ils valides ?

**6/6** analysables
sans erreur de syntaxe. Une conversion qui casserait un script serait pire
que le défaut qu'elle corrige.

## Contrôle 4 — le module est-il bien la règle du #448 ?

- rapports comparés : **304** (× 2 marqueurs)
- verdicts divergents : **0**

Le module a été **copié** du balayage ; ce contrôle vérifie que la copie n'a
pas dérivé en cours de route. C'est précisément la divergence entre copies
que ce cycle existe pour empêcher à l'avenir.

## Verdict de l'audit

**CONFORME**

- historiques préservés : **oui**
- convertis assainis : **oui**
- convertis valides : **oui**
- module fidèle au #448 : **oui**

### Ce que cet audit ne prouve pas

Il vérifie que les scripts **contiennent** ce qu'ils doivent contenir, pas
que leurs **rapports publiés** aient été mis à jour — ils ne l'ont pas été,
délibérément et de façon déclarée. L'écart entre le code et les rapports de
ces six scripts est **réel et assumé**, pas couvert par ce CONFORME.
