# GIGA F test matrix

New suite: `tests/test_giga_f_idea_feed.py` (18 unittest cases, including bounded
adversarial subcases). Its CanonicalWorkerFeedTests reuse the disposable real Git
remote harness, not mocked persistence or a second runtime.

| Challenge | Exact test / existing reused qualification |
|---|---|
| Duplicate / reordered JSON / duplicate delivery / replay counts | RegistryTests.test_duplicate_reordered_json_and_replay_do_not_inflate_roots |
| Parameters / same mechanism with changed text / similar text distinct actors / structural transfer | RegistryTests.test_parameter_variant_different_text_and_economic_distinctness |
| Variant claiming root or a false parent | RegistryTests.test_variant_cannot_claim_a_new_root_or_rewrite_parent |
| Unknown mechanism / pending cohort after restart / contaminated exposure | RegistryTests.test_unknown_mechanism_and_contamination_stay_visible_after_restart |
| Later known future result invalidates earlier eligible proposal | RegistryTests.test_later_contamination_blocks_previously_eligible_proposals |
| Outcome, authority, Candidate or scheduler payload injection | RegistryTests.test_outcome_authority_and_candidate_injection_are_rejected_recursively |
| Source publication after claimed availability / malformed schema / partial journal | RegistryTests.test_bad_availability_malformed_seed_and_partial_write |
| Blocked != negative; parked reopen reason; unauthorized verdict | RegistryTests.test_blocked_unexecuted_parked_reopening_are_not_negative |
| All seven origins / finite empirical space / all variants / missing model | RegistryTests.test_federation_all_alternatives_and_bounded_empirical_denominator |
| A/B/C shared context / passive ledger / eligibility insufficient / existing Discovery succeeds under qualified RI fixture | RegistryTests.test_policies_reused_passive_ledger_and_discovery_gate |
| Real captured-source adapter / stale captured packet / UNKNOWN mechanism | RegistryTests.test_existing_documentary_connector_is_hash_qualified_and_unknown_stays_unknown |
| LLM method distinct from rule origin and economic mechanism | RegistryTests.test_llm_extraction_does_not_replace_origin_or_mechanism |
| Existing Oracle requests source work / commits before policy intake / all origins / restart / saturated backlog / zero sources | CanonicalWorkerFeedTests.test_autonomous_replenishment_all_origins_restart_and_backpressure |
| Concurrent admissions / source ingestion / actual global Git CAS | CanonicalWorkerFeedTests.test_concurrent_replenishment_and_seed_ingestion_use_canonical_CAS |
| Crash during append / lease recovery / replay / delete or rewrite attribution | CanonicalWorkerFeedTests.test_crash_partial_append_replay_and_silent_deletion_or_attribution_rewrite |
| Source unavailable / stale content / timeout / retry | CanonicalWorkerFeedTests.test_unavailable_timeout_and_stale_source_are_explicit |
| Compute/source capacity policy / independent validation / authority | CanonicalWorkerFeedTests.test_configurable_health_and_compute_budget_fail_closed |
| Stale completion / lease expiry / source retry ceiling | CanonicalWorkerFeedTests.test_stale_completion_and_source_timeout_retry_exhaustion |

Additional canonical tests are unchanged:
`research/research_os/tests/test_oracle_worker.py` covers duplicate task execution,
competing writers, stale lease generations, source-worker retry limits, crash
boundaries and lost-publication acknowledgement. Multi-Source operational/truth
firewalls and passive semantics are covered by
`tests/test_multi_source_ideation_v2*.py`; canonical RI/Discovery admission by
`research/research_os/tests/test_mega_b_*.py` and `test_research_intelligence.py`.

Run:

```
PYTHONPATH=src:.:tests python -m unittest tests.test_giga_f_idea_feed -v
python scripts/demo_giga_f_idea_feed.py
python scripts/qualify_giga_f.py --remote-check --output /tmp/giga-f-exact-head.json
```

Full qualification runs both authoritative unittest discovery roots, exhaustive
pytest with importlib module isolation, Live Lab JavaScript tests, generated schema
and status freshness, the existing system demo, and deterministic receipt replay.
Importlib isolation avoids collisions between historical same-basename test modules.
No test expectation is weakened and no economic or prospective authority is opened.
