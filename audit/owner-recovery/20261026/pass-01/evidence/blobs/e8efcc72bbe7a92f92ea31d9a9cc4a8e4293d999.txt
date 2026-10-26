# D5 public state-type repair — bounded offline runtime evidence

MISSION_CLASS = BOUNDED_D5_PUBLIC_CONSTRUCTOR_TYPE_REPAIR_AND_REGRESSION_TESTS

TERMINAL_STATE = D5_PUBLIC_STATE_TYPE_REPAIR_BOUNDED_TEST_PASS

NEXT_SAFE_ACTION = ASTRA_INDEPENDENT_REPAIR_AND_RUNTIME_EVIDENCE_AUDIT_ONLY

## Exact authority and lineage

Repository: fahimahmedb/Quant-Trade.

Branch: builder/weather-v4-a2-d5-public-state-type-repair-tests-2026-10-05.

Independently resolved Owner test authority `45f5c940140788bb96c7b6da8581d9aa7c627dfa`, artifact
`research/weather_forward/v4/owner/OWNER_V4_A2_BOUNDED_OFFLINE_HARNESS_TEST_AUTHORITY_2026-10-05.md`
(blob `2201905c60b19c915cc9ae4ef655ff7c48fa16ec`), and historical Astra static pass
`976da7e0190b899bd9982e9e0565d68fecdddb6d`, artifact
`research/weather_forward/v4/audit/ASTRA_V4_A2_RESIDUAL_D5_FINAL_STATIC_RECHECK_2026-10-05.md`
(blob `a703cbdbd76dcf14b903c12c96c8199376cbfbac`).
The historical static pass is not a fresh audit of this repair.

Verified sole-parent chain:
`2bc718711d507b38176981c2b3e55dd607c9547b`
→ `976da7e0190b899bd9982e9e0565d68fecdddb6d`
→ `45f5c940140788bb96c7b6da8581d9aa7c627dfa`
→ `13f11dfd425534c58be79355b3ec81c7e45cfaab`
→ `7bbae0bbb085269d63f4da5f356f203d3d5baed5`
→ exact mission base `a13a15ff41b231628bb55613edc2fef060e35e48`.

No merge. New branch created at the exact base. New commit sequence:
1. `d1126ba4f1ed044431633d8338fb5269c2133e06`: regression tests, runner and two pre-repair transcripts; production unchanged.
2. `3752458336d349d425c7b9f8395871e31d08e35f`: sole production repair in contract.py, plus final complete-suite transcript.
3. Documentary evidence commit containing this report; its sole parent is the repair commit.

## Regression-first sequence and results

Only deterministic, metadata-only test structural objects were used. No fixtures or fixture payloads.
The original 145 tests and assertions are unchanged. The new module collects 134 distinct tests.

| Run | Collected/run | Passed | Failed | Errors | Skipped | Process exit |
| --- | --- | --- | --- | --- | --- | --- |
| First pre-repair run | 279 | 155 | 120 | 4 | 0 | 1 |
| Confirmed pre-repair run | 279 | 159 | 120 | 0 | 0 | 1 |
| Final complete suite | 279 | 279 | 0 | 0 | 0 | 0 |

The first run's four errors were test expectation mismatches: truthy non-boolean
acknowledgements (1 and "False"), including replace routes, were already rejected
with ValueError. The tests originally demanded TypeError. These assertions were
corrected to accept either rejection type; the unchanged-production suite was
rerun before repair, producing 120 intended boundary failures and no errors.
Both raw transcripts remain separately preserved. No xfails or skips.
The first-run test source blob was
`888a2167c6aeffb6d6d48f4fc24fd6a05d6813b7`; it differs from the committed regression source
only in those two assertRaises clauses (TypeError versus (TypeError, ValueError)).
All baseline tests passed in every run.

The confirmed failures include the exact PERMIT/AUTHORIZED string counterexample;
state-value strings, None where disallowed, wrong enum families and ordinary invalid objects;
mixed typed/invalid states; dataclasses.replace; duck decisions; falsey non-boolean
acknowledgements; malformed internal helper/finalizer state routes and truthy
non-boolean finalizer acknowledgements. Finalizer negative cases start with a
valid exact acknowledged context and a correctly matched denial log, so failures
are not attributable to an unrelated permissive VALID/COMPLETED gate.
No low-level object allocation or attribute mutation is used by the new attack tests.

## Conservative production repair

Only contract.py changed:

- Shared state validation requires ValidationState, PermitState, QuarantineState,
  ReleaseState and CompletionState membership; stop_reason is StopReason or None.
  Invalid types raise TypeError without conversion.
- Direct HarnessDecision validates types before checking that permit is exactly
  DENY and release exactly BLOCKED. Other correctly typed denial/error states are
  preserved, rather than imposing new policy constraints.
- The internal decision allocator validates the same types before constructing
  guarded results. The permissiveness helper also rejects invalid permit/release types.
- Direct LoggedActionResult requires an exact HarnessDecision and StructuredAuditLog,
  validates all decision states, rejects permissive decisions, requires a boolean
  acknowledgement exactly False, and log_record None. Duck decisions and falsey
  non-boolean acknowledgement values no longer pass.
- The finalizer returns None for invalid decision-state types; requires exact
  LogAppendAcknowledgement, StructuredAuditLog and LogRecord types, a tuple of
  actual log records, acknowledgement.appended exactly True, and typed logged
  permit/quarantine/release states. Existing unique-record, exact-content and
  exact-context linkage checks remain in place.
- Successful guarded authorization still requires PERMIT, VALID and COMPLETED
  with exact acknowledged logging. A same-ID/different-content record still fails.

Production trusted_root.py is unchanged. No permissive production root. No new
CPU, memory, duration or volume enforcement and no resource-control redesign.

## Preserved invariants

| Coverage | Existing tests | Final result |
| --- | --- | --- |
| D1 trusted root | 11 | PASS |
| D2 provenance | 24 | PASS |
| D3 recipient | 11 | PASS |
| D4 independent release approval | 9 | PASS |
| D5 prior logging/final-state coverage | 39 | PASS |
| Input/output manifest bindings | 44 | PASS |
| Disclosure exact tuple and global BLOCKED precedence | 4 | PASS |
| Resources, including WITHIN_AUTHORITY literal and fail-closed states | 3 | PASS |
| New D5 type regressions | 134 | PASS |

Exact guarded positive paths, log acknowledgement, missing/duplicate IDs, same-ID
content mismatch, authority/actor/role/action mismatches, cumulative disclosure,
manifest digests, provenance, recipients, release independence and resources
retain their original assertions. Test-only root injection remains isolated to
the test process and is not execution-policy authority.

## Source, test, runner and transcript identities

All identities below are Git blob SHA-1s, verified against the published repair tree.
The final runner printed the exact executed source/test/runner identities.

| Path relative to a2_harness | Blob |
| --- | --- |
| D5_TYPE_REPAIR_CONFIRMED_INITIAL_TEST_OUTPUT_2026-10-05.txt | `c334e2e7aa2a8385b426ba5292ece6a3e57a0b63` |
| D5_TYPE_REPAIR_FINAL_TEST_OUTPUT_2026-10-05.txt | `f0fbf7f1b63fa44b8db178d740c8730962b637cc` |
| D5_TYPE_REPAIR_INITIAL_TEST_OUTPUT_2026-10-05.txt | `e5f98e5bfa4d307353c2492f8531a5b38ed59feb` |
| contract.py | `f6f94a4a472e3f6652a1502f6afb5825721364d0` |
| run_d5_type_regression_tests.py | `f660a24d969e50db62ed6165c15272d90cb86b4b` |
| test_d5_public_state_types.py | `52bb94ed7fa497bb9756afe02052b855dcd3d9f5` |
| test_bounded_runtime.py (unchanged) | `aa0159c2a470da034c6611e207687997294fb236` |
| run_bounded_runtime_tests.py (unchanged) | `25b7d3bde54e412a51df45059a65283479420725` |
| harness.py (unchanged) | `00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4` |
| trusted_root.py (unchanged) | `9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94` |
| __init__.py (unchanged) | `bf9a2bdba7658454ea10009a28c975024365cfe1` |
| README.md (unchanged) | `b3b74326d2d41f1d88c9e891186a5af9a663f095` |

Pre-repair contract blob: `234c31b62b328fb906c2e2aa5054496a044b0746`.
Each old INITIAL/DIAGNOSTIC/FINAL transcript and the prior evidence report retain
their exact base blob identity; none was opened, overwritten or amended.

## Every shell command executed

Working directory for all commands:
`/workspace/scratch/eb92e26a9e5c/a2_d5_type_a13a15ff`.

1. `sed -n '300,650p' research/weather_forward/v4/a2_harness/contract.py`
2. `cat research/weather_forward/v4/a2_harness/run_bounded_runtime_tests.py`
3. `python -I -S -B research/weather_forward/v4/a2_harness/run_d5_type_regression_tests.py > research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_INITIAL_TEST_OUTPUT_2026-10-05.txt 2>&1`
4. `tail -n 7 research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_INITIAL_TEST_OUTPUT_2026-10-05.txt`
5. `rg -n -A 18 '^ERROR:' research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_INITIAL_TEST_OUTPUT_2026-10-05.txt`
6. `python -I -S -B research/weather_forward/v4/a2_harness/run_d5_type_regression_tests.py > research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_CONFIRMED_INITIAL_TEST_OUTPUT_2026-10-05.txt 2>&1`
7. `cat research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_INITIAL_TEST_OUTPUT_2026-10-05.txt`
8. `cat research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_CONFIRMED_INITIAL_TEST_OUTPUT_2026-10-05.txt`
9. `python -I -S -B research/weather_forward/v4/a2_harness/run_d5_type_regression_tests.py --allow-in-scope-repair > research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_FINAL_TEST_OUTPUT_2026-10-05.txt 2>&1`
10. `cat research/weather_forward/v4/a2_harness/D5_TYPE_REPAIR_FINAL_TEST_OUTPUT_2026-10-05.txt`

All Python executions used standard-library unittest/unittest.mock, -I -S -B,
and the dedicated bounded runner. No unrelated test suite or CI was executed.
Repository file materialization and editing used apply_patch. Repository authority
reads, branch creation and commit/tree publication used the GitHub connector;
they did not access operational sources or credentials.

## Scope, access and evidence limits

The runner rejected local bytecode cache reads and loaded allowlisted source
instead. Each final audit counter for network, subprocess and forbidden file
access is zero. Six rejected code-cache reads are expected importlib fallback,
not fixture access. No test data writes; outer shell redirection saved transcripts.
This in-process audit mechanism is bounded test evidence, not deployed isolation
or proof of technical-control effectiveness.

FILES_MODIFIED_OUTSIDE_SCOPE = NONE
PRODUCTION_HARNESS_FILES_MODIFIED = contract.py
EXTERNAL_DEPENDENCIES_ADDED = NONE
TEST_ONLY_TRUSTED_ROOT_USED = TRUE
PRODUCTION_TRUSTED_ROOT_MODIFIED = FALSE
NETWORK_ACCESSED_BY_TESTS = NO
FIXTURES_ACCESSED = NONE
RESEARCH_FIXTURES_CREATED = NONE
REAL_DATA_ACCESSED = NONE
REAL_METADATA_ACCESSED = NONE
ENDPOINTS_QUERIED = NONE
CREDENTIALS_USED = NONE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

No unresolved defect was observed in the bounded suite after repair. This is not
exhaustive runtime correctness, a suitability certification for a research
experiment, an approval of fixtures, or verification of deployed controls.
No economic validation or operational phase is authorized by this result.
The independent repair/runtime evidence audit remains outstanding.
