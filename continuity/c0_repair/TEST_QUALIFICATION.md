# Exact candidate qualification

PREQUALIFICATION_SHA=df513ec327b09277c83d6a153181a8fb989d79c6
LOCAL_RESULT=FAIL
HOSTED_RUN_ID=40436205163
HOSTED_HEAD_SHA=df513ec327b09277c83d6a153181a8fb989d79c6
HOSTED_CONCLUSION=failure

- targeted_c0: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', '-m', 'unittest', '-v', 'tests.test_wave2_c2_scientific_adjudication', 'tests.test_c0_confirmation_count_repair']; log candidate_exact_runs/targeted_c0.log
- preserved_current_c0_attack: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'continuity/one_shot/oneshot_c0_current_attack.py']; log candidate_exact_runs/preserved_current_c0_attack.log
- residual_outcome_ref_invariant: FAIL; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'continuity/c0_repair/probes/outcome_ref_current_probe.py']; log candidate_exact_runs/residual_outcome_ref_invariant.log
- retained_integrity: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', '-m', 'unittest', '-v', 'tests.test_research_os_trial_proposal_export_binding', 'tests.test_research_os_epoch_model_admission', 'tests.test_research_os_trial_epoch_window', 'tests.test_research_os_serializable_outcome_membrane', 'tests.test_research_os_native_trial_lineage', 'tests.test_research_os_epoch_blinding_admission', 'tests.test_research_os_evaluation_membrane_admission', 'tests.test_research_os_source_pit_clocks']; log candidate_exact_runs/retained_integrity.log
- ordinary_regression: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py']; log candidate_exact_runs/ordinary_regression.log
- research_os_regression: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', '-m', 'unittest', 'discover', '-s', 'research/research_os/tests', '-p', 'test_*.py']; log candidate_exact_runs/research_os_regression.log
- historical_replay: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'continuity/one_shot/replay_historical_tests.py']; log candidate_exact_runs/historical_replay.log
- source_shadow: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'continuity/one_shot/oneshot_e1_probe.py']; log candidate_exact_runs/source_shadow.log
- schema_check: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'scripts/generate_schemas.py', '--check']; log candidate_exact_runs/schema_check.log
- status_check: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', 'scripts/status_artifacts.py', '--check']; log candidate_exact_runs/status_check.log
- selected_q_attacks: PASS; command ['/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3', '-m', 'pytest', '-q', 'continuity/one_shot/evidence/regression_classification/q-source/test_giga_q_core_identity.py', '-k', 'export_guard_covers_nested_json_serializable_sequences or pipeline_cannot_accept_tuple_hidden_outcome or authority_never_coerces_false_like_values']; log candidate_exact_runs/selected_q_attacks.log

FACT: All guard outcomes, environment, SHA, start/end, failures and logs in evidence/PREQUALIFICATION.json and candidate_exact_runs. Residual failure is mandatory, not waived. Evidence-only final attestation follows, then same local/hosted commands on its exact SHA. No code/test/CI/helper change after freeze, no commit after final run. Final run metadata externally anchored.
