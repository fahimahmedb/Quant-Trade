# Audit indépendant — #520, réparation du dictionnaire V du #485

Route indépendante : reparse `V` par regex sur le texte brut (pas
l'AST du backtest, pas d'import du module), et compare au commit
précédent via `git show HEAD~1` plutôt qu'à une copie locale.

## Les 5 verdicts corrigés, vérifiés un par un

| Script | Avant (HEAD~1) | Après | Attendu | Accord |
|---|---|---|---|---|
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | IRRÉPARABLE | RÉPARABLE | RÉPARABLE | **OUI** |
| `nonml_battery_backfill_lot_audit.py` | RÉPARABLE | IRRÉPARABLE | IRRÉPARABLE | **OUI** |
| `nonml_coverage_wording_fix_audit.py` | RÉPARABLE | IRRÉPARABLE | IRRÉPARABLE | **OUI** |
| `nonml_report_idempotence_backtest.py` | RÉPARABLE | IRRÉPARABLE | IRRÉPARABLE | **OUI** |
| `nonml_reproducibility_campaign_v2_audit.py` | RÉPARABLE | IRRÉPARABLE | IRRÉPARABLE | **OUI** |

- les **12** autres entrées de `V` sont-elles identiques avant/après : **OUI**

## Le compte du rapport, recalculé indépendamment depuis `V`

- recalculé depuis `V` (regex indépendante) : **8** irréparables, **9** réparables (17 entrées au total)
- publié dans le rapport : **8 / 17** irréparables, **9** réparables
- accord : **OUI**

## Dette connue, non corrigée dans ce cycle

- le littéral en dur « chacun des 12 » (l.288, devrait valoir **9**) est-il toujours présent : **OUI — dette non résolue**

> Ce littéral décrivait une coïncidence numérique exacte avant
> ce cycle (12 réparables = « 12 » écrit en dur). La réparation
> du #520 change le compte sans le mettre à jour — **hors du
> périmètre déclaré au pré-enregistrement** (5 lignes de `V`
> uniquement). **Nouvelle dette, signalée, pas corrigée ici.**

**PASS** — les 5 corrections sont vérifiées sur pièce, les 12 autres entrées sont intactes, et le compte publié se recalcule identiquement par une route indépendante.
