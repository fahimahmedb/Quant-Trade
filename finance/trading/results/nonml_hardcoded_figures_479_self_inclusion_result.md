# La citation « 16 et 2 » du #479 est-elle traçable au #463 ? (pré-enregistré)

Le #479 classe `nonml_self_inclusion_detector_backtest.py` **legitime**, disant que ses listes sont des citations du #463. Le #504 le classe parmi les **5 résidus** jamais rattachés à une source publiée. Ce cycle tranche mécaniquement.

## Les 18 noms, extraits par script (AST, pas regex)

- `FAUTIFS_463` : **2** — ['nonml_verdict_rule_propagation_backtest.py', 'nonml_six_reports_regeneration_backtest.py']
- `SAINS_463` : **16** — ['nonml_npz_report_consistency_baskets_backtest.py', 'nonml_third_npz_schema_handling_backtest.py', 'nonml_net_pnl_correction_backtest.py', 'nonml_sweep_pass_prose_fix_backtest.py', 'nonml_verdict_detector_fix_backtest.py', 'nonml_verdict_detector_complete_backtest.py', 'nonml_marker_emitted_by_scripts_backtest.py', 'nonml_tom_decomposition_npz_backtest.py', 'nonml_orphan_npz_inspection_backtest.py', 'nonml_verdict_variant_decision_backtest.py', 'nonml_silent_skip_decision_backtest.py', 'nonml_dsr_corrected_trials_backtest.py', 'nonml_battery_coverage_backtest.py', 'nonml_temporal_holdout_backtest.py', 'nonml_relative_holdout_backtest.py', 'nonml_verdict_rule_battery_backtest.py']
- total : **18**

## Recherche littérale dans la section `## Backlog #463`

| Script | Radical cherché | Trouvé littéralement dans #463 |
|---|---|---|
| `nonml_verdict_rule_propagation_backtest.py` | `verdict_rule_propagation` | **OUI** |
| `nonml_six_reports_regeneration_backtest.py` | `six_reports_regeneration` | **OUI** |
| `nonml_npz_report_consistency_baskets_backtest.py` | `npz_report_consistency_baskets` | **NON** |
| `nonml_third_npz_schema_handling_backtest.py` | `third_npz_schema_handling` | **NON** |
| `nonml_net_pnl_correction_backtest.py` | `net_pnl_correction` | **NON** |
| `nonml_sweep_pass_prose_fix_backtest.py` | `sweep_pass_prose_fix` | **NON** |
| `nonml_verdict_detector_fix_backtest.py` | `verdict_detector_fix` | **NON** |
| `nonml_verdict_detector_complete_backtest.py` | `verdict_detector_complete` | **NON** |
| `nonml_marker_emitted_by_scripts_backtest.py` | `marker_emitted_by_scripts` | **NON** |
| `nonml_tom_decomposition_npz_backtest.py` | `tom_decomposition_npz` | **NON** |
| `nonml_orphan_npz_inspection_backtest.py` | `orphan_npz_inspection` | **NON** |
| `nonml_verdict_variant_decision_backtest.py` | `verdict_variant_decision` | **NON** |
| `nonml_silent_skip_decision_backtest.py` | `silent_skip_decision` | **NON** |
| `nonml_dsr_corrected_trials_backtest.py` | `dsr_corrected_trials` | **NON** |
| `nonml_battery_coverage_backtest.py` | `battery_coverage` | **NON** |
| `nonml_temporal_holdout_backtest.py` | `temporal_holdout` | **NON** |
| `nonml_relative_holdout_backtest.py` | `relative_holdout` | **NON** |
| `nonml_verdict_rule_battery_backtest.py` | `verdict_rule_battery` | **NON** |

- retrouvés : **2 / 18**
- absents : **16 / 18**

> **La classification « legitime » du #479 est contredite.** Seuls **2** des **18** noms cités par le script apparaissent littéralement dans la section `## Backlog #463`. Les **16** autres ne sont **pas une citation** — ce sont des noms que le script `self_inclusion_detector_backtest.py` a dû reconstruire ou obtenir ailleurs, jamais publiés par le #463 lui-même. **Le #504 avait raison** : ce sont des emprunts non rattachables à une source publiée.

## Le geste appliqué, et une régénération refusée par précaution

Le verdict `V` du #479 pour cette cible corrigé (`legitime` → `partiel`), diff vérifié borné à cette seule entrée, citant le #504.

**Le rapport du #479 n'a délibérément pas été régénéré ni committé**, même garde-fou qu'aux #524/#525 : ce script recalcule sa population par un balayage du dépôt à l'exécution, susceptible de la même dérive déjà mesurée pour les dictionnaires `V` similaires (58→67 au #524). Regénérer sans vérifier d'abord l'ampleur de cette dérive risquerait de committer un diff qui déborde de la seule correction déclarée ici.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| Au plus 2 des 18 retrouvés (seuls les FAUTIFS) | ≤ 2 | 2 | **vérifiée** |
| Verdict « legitime » du #479 contredit | oui | oui | **vérifiée** |
| Correction bornée à 1 entrée de `V` | oui | oui | **vérifiée** |

## Critères de succès

1. Les 18 noms extraits par script et publiés — **OUI**.
2. Compte de noms retrouvés dans #463 publié (2/18) — **OUI**.
3. Verdict du #479 confronté au compte, sans jugement à l'œil — **OUI**.
4. Si contradiction : ligne V corrigée, diff borné, #504 cité — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : trancher une contradiction entre deux verdicts antérieurs par une vérification mécanique, pas par préférence pour l'un ou l'autre.

Simulation 300 € et robustesse **sans objet** : cycle de vérification/réparation de dépôt, aucune position.
