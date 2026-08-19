# Audit indépendant — #528, clôture du lot hardcoded_figures_remainder

Route distincte du backtest : `grep -c` externe sur un extrait de
section isolé par indices de ligne (pas de découpage regex en
mémoire unique), recherche des marqueurs de rétractation avec un
filtre explicite sur la phrase générique de la « Dette restante ».

## Recompte des marqueurs de rétractation, par grep externe

| Script | Radical | Marqueur trouvé (hors dette générique) |
|---|---|---|
| `nonml_battery_backfill_lot_audit.py` | `battery_backfill_lot` | non |
| `nonml_citer_451_resolution_backtest.py` | `citer_451_resolution` | non |
| `nonml_conditional_sections_sweep_backtest.py` | `conditional_sections_sweep` | non |
| `nonml_dsr_corrected_trials_backtest.py` | `dsr_corrected_trials` | non |
| `nonml_idempotence_famille_capable_backtest.py` | `idempotence_famille_capable` | non |
| `nonml_idempotence_lot2_backtest.py` | `idempotence_lot2` | non |
| `nonml_marker_emitter_crossing_backtest.py` | `marker_emitter_crossing` | non |
| `nonml_net_pnl_correction_robustness.py` | `net_pnl_correction_robustness` | non |
| `nonml_orphans_interrupted_or_lost_backtest.py` | `orphans_interrupted_or_lost` | non |
| `nonml_pnl_duplicate_sweep_audit.py` | `pnl_duplicate_sweep` | non |
| `nonml_pnl_duplicate_sweep_v2_audit.py` | `pnl_duplicate_sweep_v2` | non |
| `nonml_pnl_persistence_exposed_pass_audit.py` | `pnl_persistence_exposed_pass` | non |
| `nonml_report_idempotence_audit.py` | `report_idempotence` | non |
| `nonml_reproducibility_campaign_v2_audit.py` | `reproducibility_campaign_v2` | non |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | `reproducibility_campaign_v3_lot2` | non |
| `nonml_reproducibility_sample_backtest.py` | `reproducibility_sample` | non |
| `nonml_self_inclusion_repair_audit.py` | `self_inclusion_repair` | non |
| `nonml_sweep_pass_prose_fix_backtest.py` | `sweep_pass_prose_fix` | non |
| `nonml_content_defined_magnitudes_audit.py` | `content_defined_magnitudes` | non |
| `nonml_content_defined_magnitudes_backtest.py` | `content_defined_magnitudes` | non |
| `nonml_coverage_wording_fix_audit.py` | `coverage_wording_fix` | non |
| `nonml_report_idempotence_backtest.py` | `report_idempotence` | non |

- marqueurs de rétractation réels retrouvés (hors dette générique) : **0**
- accord avec le backtest (0 nouvelle rétractation) : **OUI**

## Le dictionnaire `V` du #479, confirmé inchangé par ce commit

- `nonml_hardcoded_figures_remainder_backtest.py` touché par le commit du #528 : **NON**

> Confirme qu'aucune correction n'a été appliquée — cohérent avec 0 nouvelle rétractation trouvée par les deux routes.

**PASS** — la route indépendante (grep externe par section isolée) reproduit le compte 0/22 et confirme qu'aucune correction n'a été committée.
