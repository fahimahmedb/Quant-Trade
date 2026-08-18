# Audit indépendant — committabilité des réparables (#507)

Le backtest classe sur la **structure** : quels appels le script fait.
Cet audit interroge l'**histoire** : combien de fois le rapport de chaque
réparable a **réellement été réécrit** dans le dépôt. Un rapport committé
une seule fois n'a jamais dérivé ; un rapport réécrit dix fois dérive à
chaque régénération.

## Le classement relu

- lignes de détail relues : **13**
- population annoncée : **13**
- accord : **OUI**
- NC1 + NC2 = non committables annoncés : **OUI**

## L'histoire, classe par classe

| Classe | Effectif | Réécritures — moyenne | min | max |
|---|---|---|---|---|
| **NC1** | **2** | **1,0** | **1** | **1** |
| **NC2** | **9** | **1,0** | **1** | **1** |
| **C** | **2** | **1,0** | **1** | **1** |

- moyenne des **candidats C** : **1,0**
- moyenne des **non committables** : **1,0**

- valeurs distinctes de réécritures sur la population : **1**

> **Cette route ne discrimine rien ici.** Les **13** rapports ont
> **tous** été écrits **1** fois. Une moyenne identique de
> part et d'autre n'est pas une confirmation : **c'est une absence de
> mesure.** Le contrôle correspondant est donc **non testable**, et
> je ne le compte pas comme réussi.
>
> *(La route fonctionne pourtant : un rapport régénéré du dépôt
> affiche bien plusieurs commits. C'est cette population-ci qui est
> uniforme — parce qu'aucun de ces rapports n'a jamais été refait.)*

## Le détail

| Script | Classe | Rapport | Réécritures |
|---|---|---|---|
| `nonml_battery_backfill_lot_audit.py` | **C** | `nonml_battery_backfill_lot_audit.md` | **1** |
| `nonml_coverage_wording_fix_audit.py` | **C** | `nonml_coverage_wording_fix_audit.md` | **1** |
| `nonml_content_defined_magnitudes_audit.py` | **NC1** | `nonml_content_defined_magnitudes_audit.md` | **1** |
| `nonml_report_idempotence_backtest.py` | **NC1** | `nonml_report_idempotence_result.md` | **1** |
| `nonml_content_defined_magnitudes_backtest.py` | **NC2** | `nonml_content_defined_magnitudes_result.md` | **1** |
| `nonml_dsr_corrected_trials_backtest.py` | **NC2** | `nonml_dsr_corrected_trials_result.md` | **1** |
| `nonml_duplicate_sweep_coverage_audit.py` | **NC2** | `nonml_duplicate_sweep_coverage_audit.md` | **1** |
| `nonml_idempotence_famille_capable_backtest.py` | **NC2** | `nonml_idempotence_famille_capable_result.md` | **1** |
| `nonml_idempotence_lot2_backtest.py` | **NC2** | `nonml_idempotence_lot2_result.md` | **1** |
| `nonml_marker_emitter_crossing_backtest.py` | **NC2** | `nonml_marker_emitter_crossing_result.md` | **1** |
| `nonml_orphans_interrupted_or_lost_backtest.py` | **NC2** | `nonml_orphans_interrupted_or_lost_result.md` | **1** |
| `nonml_reproducibility_campaign_v2_audit.py` | **NC2** | `nonml_reproducibility_campaign_v2_audit.md` | **1** |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | **NC2** | `nonml_reproducibility_campaign_v3_lot2_audit.md` | **1** |

## Ce que cet audit ne prouve pas

Le nombre de réécritures est un **indice**, pas une preuve : un rapport
peu réécrit peut l'être parce que personne ne s'y est intéressé, non
parce qu'il est stable. **La corrélation entre les deux routes ne
valide pas la règle du #507** — elle montre seulement qu'elles ne se
contredisent pas.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **21** ; dont **tapés en dur** : **0**

## Verdict

1. le détail relu couvre toute la population annoncée — **OUI**.
2. NC1 + NC2 égale le compte de non committables — **OUI**.
3. les classes ne dépassent pas la population — **OUI**.
4. l'histoire ne contredit pas la structure — **NON TESTABLE**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (4/4, **1** non testable(s))

Anti-lookahead **sans objet au sens temporel** pour les prix ; la
datation employée ici est **strictement rétrospective** — commits
passés, jamais l'état futur.
