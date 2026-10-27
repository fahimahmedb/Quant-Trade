# Exact-freeze regression failure classification

FACT: Ordinary unittest ran at product freeze `68f16c0f697f275f536e9c58afdc00b341ebee0a`: **1125 tests, 4 failures, 1 error**. Complete run remains FAIL. The process completed; no failures were suppressed.

FACT: All five failures have concrete stale test-data or stale qualification-metadata explanations, demonstrated below. This classification does not relabel the failed run PASS. No product or tracked file was changed. The independent current C0 confirmation-count invariant still blocks qualification.

## test_astra_pre_t0.Phase6ProofAndConcurrencyCampaign.test_published_test_inventory_matches_authoritative_package_discovery

Classification: **STALE_FIXTURE**.

FACT: STATE.md:16 publishes 1107; authoritative package discovery actually ran1125. Test itself enforces freshness and is correct.

Evidence: `/tmp/oneshot_runs/ordinary_regression.log:22-27`.

RECOMMENDATION: Evidence/documentation-only inventory correction may be lawful; preserve failed run. It does not alter product.

## test_research_os_canonical_identity.CanonicalIdentityTests.test_valid_epoch_trial_and_four_family_hashes_are_unchanged

Classification: **STALE_FIXTURE**.

FACT: tests/test_research_os_canonical_identity.py:40-41 expects old shared trial fixture hash dbb5e858d6e03796b26282cdbc4d442f7ec77798cd9dc9e81e43d35c9beae91b. CP02 attributed first proposal, so same builder on actual changed fixture emits a02058400aec467b836985f030f2a1694f5a0c78eedefa7c270b21c24b92ae47. Epoch/family hashes are independent.

Evidence: `/tmp/oneshot_regression_classification/fixture_only_demonstration.log`.

RECOMMENDATION: A test-only golden correction is lawful before candidate if desired; no product mutation.

## test_research_os_v2_pipeline.V2PipelineTests.test_end_to_end_pre_outcome_receipt

Classification: **STALE_FIXTURE**.

FACT: Independent inline V2PipelineTests.bundle() generated_proposals at tests/test_research_os_v2_pipeline.py:39 are id-only P1/P2; lack required hypothesis/generation/hash attribution. Product correctly blocks TRIAL_PROPOSAL_BINDING_MISMATCH before later gates.

Evidence: `/tmp/oneshot_regression_classification/fixture_only_demonstration.log`.

RECOMMENDATION: Evidence-only demonstration adding attribution to in-memory fixture makes all four tests pass, including validator BLOCK and broken-blinding expected gates. No tracked tests or product changed.

## test_research_os_v2_pipeline.V2PipelineTests.test_broken_blinding_cannot_export

Classification: **STALE_FIXTURE**.

FACT: Independent inline V2PipelineTests.bundle() generated_proposals at tests/test_research_os_v2_pipeline.py:39 are id-only P1/P2; lack required hypothesis/generation/hash attribution. Product correctly blocks TRIAL_PROPOSAL_BINDING_MISMATCH before later gates.

Evidence: `/tmp/oneshot_regression_classification/fixture_only_demonstration.log`.

RECOMMENDATION: Evidence-only demonstration adding attribution to in-memory fixture makes all four tests pass, including validator BLOCK and broken-blinding expected gates. No tracked tests or product changed.

## test_research_os_v2_pipeline.V2PipelineTests.test_validator_block_cannot_export

Classification: **STALE_FIXTURE**.

FACT: Independent inline V2PipelineTests.bundle() generated_proposals at tests/test_research_os_v2_pipeline.py:39 are id-only P1/P2; lack required hypothesis/generation/hash attribution. Product correctly blocks TRIAL_PROPOSAL_BINDING_MISMATCH before later gates.

Evidence: `/tmp/oneshot_regression_classification/fixture_only_demonstration.log`.

RECOMMENDATION: Evidence-only demonstration adding attribution to in-memory fixture makes all four tests pass, including validator BLOCK and broken-blinding expected gates. No tracked tests or product changed.

## Evidence-only classification probes

FACT: `/tmp/oneshot_fixture_classification_probe.py` changes only the inline unittest fixture in process memory by attributing P1 to the same candidate's hypothesis_id/generation_id/candidate_hash. It then executes the original four V2PipelineTests against unchanged frozen product. All four pass, preserving the original later-validator and blinding block assertions. This is causal evidence for a stale fixture, not a product repair and not a replacement for an actual qualification run.

FACT: The same probe runs unchanged current `build_research_trial` against the old W2 shared JSON fixture and the actual CP02 shared JSON fixture. It emits old hash `dbb5e858d6e03796b26282cdbc4d442f7ec77798cd9dc9e81e43d35c9beae91b` and new hash `a02058400aec467b836985f030f2a1694f5a0c78eedefa7c270b21c24b92ae47`. Their input diff is exactly proposal attribution; scientific identity hashing itself did not change.

FACT: Probe and selected-Q commands, environment, HEAD, start/end, status and logs are recorded in `/tmp/oneshot_regression_classification/TEST_RUNS.json`.

## Selected immutable H/V/Q attacks

- FACT: `6d9dc40b5833442c597f7e7ab8aa631b3d481e83:tests/test_research_os_evaluation_membrane_admission.py` — `DUPLICATE_TEST`; PASS in exact freeze retained_integrity run; source/target test bytes identical. Protects outcome firewall.
- FACT: `6d9dc40b5833442c597f7e7ab8aa631b3d481e83:tests/test_research_os_source_pit_clocks.py` — `DUPLICATE_TEST`; PASS in exact freeze retained_integrity run; source/target test bytes identical. Protects PIT.
- FACT: `5d628db2949144ca6abf94327de3146f3983ecea:tests/test_research_os_native_trial_lineage.py` — `DUPLICATE_TEST`; PASS in exact freeze retained_integrity run; source/target test bytes identical. Protects trial/proposal identity.
- FACT: `5d628db2949144ca6abf94327de3146f3983ecea:tests/test_research_os_frozen_envelope_binding.py` — `DUPLICATE_TEST`; PASS within ordinary suite (not among five failures); source/target bytes identical. Protects frozen identity.
- FACT: `4efadddf694eff0c0df00925b5b4b89194f32f8e:tests/test_giga_q_core_identity.py` — `CURRENT_INVARIANT`; 18 PASS, 7 unselected, exact source test bytes extracted to tmp; target synthetic fixture used; no product integration. Protects serializable outcome firewall and strict authority false.

FACT: Q was used as a bounded attack source. Only the 18 parameterized cases directly applicable to retained serializable-outcome and strict-authority invariants were selected; seven other source-file cases were unselected. No global Q PASS is claimed. The extracted source test body is unchanged. Its synthetic oracle fixture was copied from the frozen target so it tests the retained target contract rather than importing historical product state.

FACT: L_ATTACK_SCOPE=NOT_USED. No immutable L source was recovered; no moving L branch name was followed.

INFERENCE: The five ordinary failures do not require any new product code. Current C0 scientific-independence failure remains applicable and unresolved independently of these stale fixtures. Correcting tests/metadata cannot make that failure disappear. Do not reopen product after freeze.
