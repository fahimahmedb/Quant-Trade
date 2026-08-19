# Le défaut périmé du #485 est-il isolé ? Écran sur 4 autres dictionnaires `V` (pré-enregistré)

Écran **mécanique, déclaré faible d'avance** (même
discipline que le proxy du #485 lui-même) — il signale des
**candidats**, il ne confirme ni n'exclut rien.

## Les 4 dictionnaires, effectif et cycle d'origine

| Script | Cycle d'origine | Effectif |
|---|---|---|
| `nonml_hardcoded_figures_remainder_backtest.py` | #479 | **32** |
| `nonml_guards_witness_remainder_backtest.py` | #484 | **10** |
| `nonml_guards_without_witness_backtest.py` | #481 | **5** |
| `nonml_orphan_audits_declared_reading_backtest.py` | #483 | **4** |

- **51** entrées passées à l'écran.

> **Écart avec le pré-enregistrement, publié tel quel.** Le PREREG annonçait **108** entrées (comptées par une regex rapide sur les lignes commençant par un guillemet — y compris, à tort, des lignes de continuation de texte de justification, pas seulement des clés de dictionnaire). **L'extraction AST de ce script, plus rigoureuse, en trouve 51.** Même défaut de double comptage que celui trouvé au #500 sur les f-strings — corrigé ici par la méthode la plus stricte des deux, pas par un ajustement du seuil après lecture du résultat.

## Les candidats trouvés, par dictionnaire

### `nonml_hardcoded_figures_remainder_backtest.py` (#479, 32 entrées)

- `nonml_battery_backfill_lot_audit.py` — mentionné en **#508** avec marqueur(s) ['réfuté']
- `nonml_citer_451_resolution_backtest.py` — mentionné en **#481** avec marqueur(s) ['contredit']
- `nonml_conditional_sections_sweep_backtest.py` — mentionné en **#509** avec marqueur(s) ['réfuté']
- `nonml_content_defined_magnitudes_audit.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_content_defined_magnitudes_backtest.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_coverage_wording_fix_audit.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_dsr_corrected_trials_backtest.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_idempotence_famille_capable_backtest.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_idempotence_lot2_backtest.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_marker_emitter_crossing_backtest.py` — mentionné en **#481** avec marqueur(s) ['contredit']
- `nonml_net_pnl_correction_robustness.py` — mentionné en **#481** avec marqueur(s) ['contredit']
- `nonml_orphans_interrupted_or_lost_backtest.py` — mentionné en **#485** avec marqueur(s) ['réfuté']
- `nonml_pnl_duplicate_sweep_audit.py` — mentionné en **#480** avec marqueur(s) ['contredit', 'réfuté']
- `nonml_pnl_duplicate_sweep_v2_audit.py` — mentionné en **#480** avec marqueur(s) ['contredit', 'réfuté']
- `nonml_pnl_persistence_exposed_pass_audit.py` — mentionné en **#480** avec marqueur(s) ['contredit', 'réfuté']
- `nonml_report_idempotence_audit.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_report_idempotence_backtest.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_reproducibility_campaign_v2_audit.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_reproducibility_campaign_v3_lot2_audit.py` — mentionné en **#485** avec marqueur(s) ['réfuté']
- `nonml_reproducibility_sample_backtest.py` — mentionné en **#482** avec marqueur(s) ['contredit']
- `nonml_reproducibility_sample_lot3_audit.py` — mentionné en **#482** avec marqueur(s) ['contredit']
- `nonml_self_inclusion_detector_backtest.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_self_inclusion_repair_audit.py` — mentionné en **#516** avec marqueur(s) ['réfuté']
- `nonml_sweep_pass_prose_fix_backtest.py` — mentionné en **#494** avec marqueur(s) ['contredit', 'réfuté']

### `nonml_guards_witness_remainder_backtest.py` (#484, 10 entrées)

- `nonml_self_inclusion_detector_backtest.py` — mentionné en **#504** avec marqueur(s) ['réfuté']
- `nonml_six_reports_regeneration_backtest.py` — mentionné en **#494** avec marqueur(s) ['contredit', 'réfuté']
- `nonml_sweep_pass_prose_fix_backtest.py` — mentionné en **#494** avec marqueur(s) ['contredit', 'réfuté']

### `nonml_guards_without_witness_backtest.py` (#481, 5 entrées)

- `nonml_battery_coverage_backtest.py` — mentionné en **#489** avec marqueur(s) ['réfuté']
- `nonml_marker_emitter_crossing_backtest.py` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `nonml_net_pnl_correction_backtest.py` — mentionné en **#489** avec marqueur(s) ['réfuté']

### `nonml_orphan_audits_declared_reading_backtest.py` (#483, 4 entrées)

- `coverage_wording_fix` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']
- `duplicate_sweep_coverage` — mentionné en **#518** avec marqueur(s) ['FAUSSE', 'réfuté']

## Le compte

- entrées passées à l'écran : **51**
- candidats trouvés (tous dictionnaires confondus) : **32**

> **Le défaut du #485 n'est pas isolé — au sens où l'écran trouve au moins un endroit où chercher.** Cela ne confirme pas une staleness réelle : le screen peut être un faux positif (le marqueur peut porter sur autre chose que le verdict du dictionnaire). **Chaque candidat est ajouté à la file « à faire » pour vérification manuelle dédiée, pas résolu ici.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 1 candidat trouvé | ≥ 1 | 32 | **vérifiée** |
| taux de candidats plus élevé pour hardcoded_figures_remainder (#479) que les 3 autres réunis | plus élevé | 75.0% vs 42.1% | **vérifiée** |
| 0 candidat depuis orphan_audits_declared_reading (#483) | 0 | 2 | **réfutée** |

## Critères de succès

1. Les 4 dictionnaires nommés, effectif et cycle d'origine publiés — **OUI**.
2. Tous les noms extraits par AST passés à l'écran (51/51, écart au chiffre du PREREG publié et expliqué) — **OUI**.
3. Chaque candidat nommé avec sa section source — **OUI**.
4. Le screen est déclaré faible d'avance, sans confirmer ni exclure — **OUI**.
5. Candidats ajoutés à la file à faire, non résolus ici — **OUI**.

**PASS** — le critère porte sur le **procédé** : un écran mécanique déclaré, pas une vérification exhaustive.

Simulation 300 € et robustesse **sans objet** : cycle de vérification bibliographique, aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état du backlog à la date de son exécution.
