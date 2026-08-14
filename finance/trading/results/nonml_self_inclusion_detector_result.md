# Détecter l'auto-inclusion **sans exécuter** (pré-enregistré)

Le #463 a trouvé **2** scripts non idempotents en en rejouant **18**. Le
dépôt en compte **319** : les rejouer deux fois chacun est hors de
portée d'un cycle. Ce script **lit le code**, il n'exécute rien.

## La calibration — avant les résultats, parce qu'elle les conditionne

Le #463 fournit une **vérité terrain** : **2** fautifs, **16** sains.

| | Attendu | Mesuré |
|---|---|---|
| **rappel** (fautifs signalés) | 2 / 2 | **1 / 2** |
| **faux positifs** (sains signalés) | ≤ 4 | **10 / 16** |

**Cas connus MANQUÉS :**

- `nonml_six_reports_regeneration_backtest.py`

> **Le détecteur rate un défaut qu'il devait trouver. Il est
> inutilisable en l'état**, et tout ce qui suit doit se lire avec cette
> réserve — un détecteur qui manque les cas connus n'autorise aucune
> conclusion sur les cas inconnus.

### Pourquoi il l'a manqué — diagnostic, sans toucher à la règle

*Ajouté après avoir vu le résultat, et signalé comme tel.*

`six_reports_regeneration` n'énumère **pas** `results/` par un glob :
il exécute d'autres scripts, puis demande à **`git status --short`**
ce qui a bougé. Son corpus est donc **l'état du dépôt**, pas une
liste de fichiers — et ma condition 2 ne prévoit que la seconde forme.

> **L'auto-inclusion n'exige pas de parcourir un dossier.** Il suffit
> de demander au dépôt ce qui a changé, après avoir soi-même changé
> quelque chose. Ma règle, écrite en pensant aux globs, était trop
> étroite d'une forme entière.

**La règle n'est pas corrigée ici** : elle a été déclarée avant mesure,
et l'ajuster maintenant reviendrait à la tailler sur le cas qu'elle
vient de rater. Une règle élargie devra être **déclarée dans un cycle
à part**, et **recalibrée sur la même vérité terrain**.

**Faux positifs** — scripts sains pourtant signalés :

- `nonml_battery_coverage_backtest.py`
- `nonml_dsr_corrected_trials_backtest.py`
- `nonml_net_pnl_correction_backtest.py`
- `nonml_npz_report_consistency_baskets_backtest.py`
- `nonml_orphan_npz_inspection_backtest.py`
- `nonml_relative_holdout_backtest.py`
- `nonml_silent_skip_decision_backtest.py`
- `nonml_temporal_holdout_backtest.py`
- `nonml_third_npz_schema_handling_backtest.py`
- `nonml_verdict_rule_battery_backtest.py`

Ils rappellent ce que le détecteur **ne voit pas** : si le glob d'un
script rencontre réellement son propre fichier, et si une protection
écrite autrement fonctionne.

> **Nuance que le contrôle C de l'audit impose — et elle joue en ma
> faveur, ce qui ne la rend pas moins due.** Ces scripts écrivent leur
> rapport dans le dossier qu'ils énumèrent : ils sont
> **structurellement exposés**. Que le #463 ne les ait pas vus dériver
> est une **observation**, pas une garantie — leur corpus n'a
> peut-être pas rencontré leur propre fichier ces jours-là.
>
> Le chiffre de faux positifs ci-dessus est donc **pessimiste**. Je le
> laisse tel quel : il a été défini avant mesure, et le corriger à la
> baisse après coup serait exactement ce que je reproche aux trois
> cycles précédents, à l'envers.

## Le résultat sur tout le dépôt

- scripts examinés : **319**
- **hors périmètre** (n'écrivent pas ou n'énumèrent pas) : **296**
- **protégés** : **3**
- **signalés** : **20**
- dont **inconnus du #463** : **9**

## Les scripts signalés

> **« Signalé » ne veut pas dire « défectueux ».** Seule l'exécution le
> prouverait, et ce cycle n'exécute rien. C'est une **liste de suspects**,
> à valeur de priorité pour un cycle qui, lui, les rejouerait.

- `nonml_battery_coverage_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_content_defined_magnitudes_backtest.py`
- `nonml_dsr_corrected_trials_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_empty_pass_basket_extension_backtest.py`
- `nonml_empty_pass_requalification_backtest.py`
- `nonml_net_pnl_correction_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_npz_report_consistency_backtest.py`
- `nonml_npz_report_consistency_baskets_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_orphan_npz_inspection_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_pnl_duplicate_sweep_backtest.py`
- `nonml_prereg_convention_coverage_backtest.py`
- `nonml_protocol_inventory_backtest.py`
- `nonml_relative_holdout_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_repo_magnitudes_recount_backtest.py`
- `nonml_sameday_timestamp_resolution_backtest.py`
- `nonml_silent_skip_decision_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_temporal_holdout_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_third_npz_schema_handling_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_verdict_rule_battery_backtest.py` — *sain au #463, donc **faux positif***
- `nonml_verdict_rule_propagation_backtest.py` — *fautif confirmé au #463*

## Les protections trouvées

**3** scripts portent un signe de protection. Répartition :

| Signe | Nombre |
|---|---|
| `unlink(` sur la sortie | **3** |

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| rappel 2/2 sur les cas connus | 2 | 1 | **réfutée** |
| ≥ 5 scripts nouveaux signalés | ≥ 5 | 9 | **vérifiée** |
| faux positifs ≤ 4 sur 16 | ≤ 4 | 10 | **réfutée** |

## Ce que ce cycle ne fait pas

- Il ne **répare** rien. La file demandait de propager l'exclusion de soi
  aux deux fautifs ; **c'est reporté à un cycle déclaré**, parce que
  réparer **régénère leurs rapports** et que le #450 a payé cher le
  mélange d'une réparation et d'une mesure.
- Il n'**exécute** aucun script : aucun effet de bord, contrairement au
  #463.
- Il ne **prouve** aucun défaut : il **priorise** des suspects.

## Critères de succès

1. **319/319** scripts classés — **OUI**.
2. Calibration publiée (rappel et faux positifs) — **OUI**.
3. Scripts signalés listés nominativement — **OUI**.
4. Aucun script modifié — **OUI** (lecture seule).

**PASS** — le critère porte sur le **procédé** : un
détecteur qui se révèle mauvais **et le montre proprement** réussit.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).