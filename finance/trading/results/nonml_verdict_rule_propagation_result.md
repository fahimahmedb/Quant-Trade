# Propagation de la règle du #448 aux autres consommateurs (pré-enregistré)

**Cycle de MODIFICATION**, cinquième après les #445 → #448.

## Critère 1 — le compte de « 8 scripts » était-il juste ?

Il venait d'un `grep`, donc d'une **recherche en sous-chaîne** — l'instrument
même dont ces cycles ont montré qu'il confond le code et le discours sur le
code. Recompté **par lecture** :

| Catégorie | Nombre |
|---|---|
| **usages** convertis | **6** |
| **variante** non convertible | **1** |
| **réimplémentations / citations** laissées intactes | **4** |

**Le compte de 8 était faux.** Il y a **6 usages** réels ; le
reste n'avait pas à être touché. **Prédiction vérifiée** : j'attendais moins
de 8, sans savoir combien.

### Les usages convertis

Tous sont une fonction `verdict_of` qui **décide** d'un classement :

- `nonml_capitulation_gate_floor_sweep_backtest.py` — diff **+— / −—**
- `nonml_empty_pass_basket_extension_backtest.py` — diff **+— / −—**
- `nonml_empty_pass_requalification_backtest.py` — diff **+— / −—**
- `nonml_pnl_persistence_lot4_audit.py` — diff **+— / −—**
- `nonml_protocol_inventory_backtest.py` — diff **+— / −—**
- `nonml_sameday_timestamp_resolution_backtest.py` — diff **+— / −—**

### La variante, laissée telle quelle

- `nonml_sessions_column_backfill_audit.py` : `"**PASS" in text` **seul**, sans le littéral `"PASS (niveau 1)"`.
  Le convertir **ajouterait** le littéral : ce serait redéfinir sa sémantique, pas corriger un défaut. Laissé tel quel, comme le pré-enregistrement l'annonçait.

Le pré-enregistrement avait annoncé ce cas de figure **avant** de le
rencontrer, et prescrit de ne pas y toucher. C'est appliqué.

### Les réimplémentations et citations, laissées intactes

- `nonml_verdict_detector_fix_backtest.py` — `verdict_avant()` — reproduit l'ancienne règle pour la **mesurer** (#447)
- `nonml_verdict_detector_fix_audit.py` — `ancienne()` — même rôle, dans l'audit du #447
- `nonml_pnl_duplicate_sweep_backtest.py` — un **commentaire** qui cite l'ancienne règle ; le code, lui, est converti depuis le #448
- `nonml_sweep_pass_prose_fix_audit.py` — audit **figé sur l'état du #446** : il vérifie des noms publiés sous la règle de l'époque

> **Une entorse, signalée.** Le pré-enregistrement ne déclarait que deux
> catégories : *usage* et *réimplémentation historique*.
> `nonml_sweep_pass_prose_fix_audit.py` n'est ni l'un ni l'autre au sens
> strict — il n'reproduit pas l'ancienne règle pour la comparer, il **audite
> un cycle passé avec la règle de son époque**. Le convertir ferait re-vérifier
> le #446 sous une règle qui n'existait pas alors, et son audit deviendrait
> faussement NON CONFORME. Je le classe **historique** parce que l'effet est le
> même — y toucher détruit la mesure qu'il porte — et je signale l'écart plutôt
> que d'ajouter une troisième catégorie après coup.

## Critère 2 — équivalence du module et du balayage

- rapports comparés : **322**
- verdicts divergents entre `nonml_verdict` et le balayage : **0**

**Aucune divergence** : le module est bien la règle du #448, pas une
variante qui lui ressemble.

## Critère 3 — diff confiné aux régions déclarées

Chaque script converti : **+3 / −1** — la zone d'imports (déclarée d'avance
cette fois) et la ligne de l'occurrence.

**Confiné : NON.**

Aux #447 et #448, la zone d'imports **n'était pas** déclarée, ce qui m'avait
obligé à écrire la règle en clair puis en opérations de chaînes pour rester
dans le régime. La leçon a été tirée **avant** d'écrire, pas après avoir buté
dessus — et le code s'en trouve plus simple, pas plus contorsionné.

## Critère 5 — l'effet du changement, mesuré

Sur les **322** rapports du dépôt, **8** changent de
classe entre l'ancienne règle et celle du module :

| Rapport | Ancienne règle | Règle #448 |
|---|---|---|
| `battery_coverage` | PASS | **indéterminé** |
| `capitulation_gate_floor_sweep` | PASS | **indéterminé** |
| `dsr_corrected_trials` | PASS | **indéterminé** |
| `npz_report_consistency_baskets` | PASS | **indéterminé** |
| `protocol_inventory` | PASS | **indéterminé** |
| `sweep_pass_prose_fix` | PASS | **FAIL** |
| `verdict_detector_fix` | PASS | **FAIL** |
| `verdict_rule_battery` | PASS | **indéterminé** |

Chacun de ces rapports était **mal classé** par les six consommateurs
convertis. C'est la mesure de ce que la propagation corrige.

## Ce que ce cycle ne fait pas — dit d'avance, et tenu

**Aucun rapport publié n'est régénéré.** Les régénérer mélangerait l'effet de
la règle et la dérive du dépôt — le #445 a montré que **9 lignes sur 10**
d'un rapport régénéré ne venaient pas de la modification — et six fois plutôt
qu'une.

Ce cycle crée donc **sciemment** un écart entre le code corrigé et les
rapports publiés par ces six scripts. **Cet écart est le prix d'une mesure
lisible**, il est inscrit à la dette, et le régénérer proprement est un cycle
à lui seul.

## Verdict

| | Critère | État |
|---|---|---|
| 1 | chaque occurrence classée par lecture | ✔ |
| 2 | équivalence module / balayage | ✔ |
| 3 | diff confiné aux régions déclarées | **NON** |
| 4 | aucune réimplémentation historique modifiée | voir audit |
| 5 | effet publié par script | ✔ |

### **FAIL** *(sous réserve du critère 4, vérifié par l'audit)*
