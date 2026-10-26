# Weather V4 A2 — bounded offline runtime test evidence — 2026-10-05

MISSION_CLASS = BOUNDED_OFFLINE_A2_HARNESS_RUNTIME_TEST_IMPLEMENTATION_AND_EXECUTION  
OWNER_AUTHORIZES = BOUNDED_OFFLINE_HARNESS_RUNTIME_TESTING_ONLY  
TERMINAL_STATE = BOUNDED_OFFLINE_HARNESS_TEST_PASS  
NEXT_SAFE_ACTION = ASTRA_INDEPENDENT_RUNTIME_TEST_EVIDENCE_AUDIT_ONLY

## Exact authority and source identity

|Authority|Exact SHA / verified artifact|
|---|---|
|Owner runtime-test authority|45f5c940140788bb96c7b6da8581d9aa7c627dfa; research/weather_forward/v4/owner/OWNER_V4_A2_BOUNDED_OFFLINE_HARNESS_TEST_AUTHORITY_2026-10-05.md; blob 2201905c60b19c915cc9ae4ef655ff7c48fa16ec|
|Astra static PASS|976da7e0190b899bd9982e9e0565d68fecdddb6d; research/weather_forward/v4/audit/ASTRA_V4_A2_RESIDUAL_D5_FINAL_STATIC_RECHECK_2026-10-05.md; blob a703cbdbd76dcf14b903c12c96c8199376cbfbac|
|Audited harness|2bc718711d507b38176981c2b3e55dd607c9547b|

All three exact commit objects were independently resolved. Owner branch HEAD matched its required SHA. The direct chain is audited harness → Astra PASS → Owner test authority. Comparison from audited harness to Owner authority shows only the Astra report and Owner authority additions; no harness source change. The PASS is PASS_FOR_OWNER_CONSIDERATION_OF_BOUNDED_TEST_AUTHORITY, not an execution or deployed-effectiveness certificate.

The working copy was a minimal materialization of the five exact dedicated-harness files from the authority tree, not a default-branch checkout or an import of unrelated repository programs. The initial runner verified every production source/document Git blob before importing the package. It used no external dependency.

|File|Audited / initial blob|Final tested blob|
|---|---|---|
|contract.py|db978016cb2eab91e3b7569de350d0fc65641889|234c31b62b328fb906c2e2aa5054496a044b0746|
|harness.py|00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4|unchanged|
|trusted_root.py|9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94|unchanged|
|__init__.py|bf9a2bdba7658454ea10009a28c975024365cfe1|unchanged|
|README.md|b3b74326d2d41f1d88c9e891186a5af9a663f095|unchanged|

## Results, including the initial failure

TEST_FRAMEWORK = Python standard library unittest + unittest.mock

|Run|Collected|Run|Passed|Failed|Errors|Skipped|Process exit|
|---|---:|---:|---:|---:|---:|---:|---:|
|Initial, exact audited production code|145|145|144|1|0|0|1|
|Diagnostic after production repair|145|145|145|0|0|0|1|
|Final after test-runner guard accounting correction|145|145|145|0|0|0|0|

No expected failures, unexpected successes or skip waivers occurred. The test suite itself remained byte-identical across all three runs: blob aa0159c2a470da034c6611e207687997294fb236.

INITIAL_TEST_RESULT = FAIL — 144 passed / 1 failed / 0 errors / 0 skipped  
FINAL_TEST_RESULT = PASS — 145 passed / 0 failed / 0 errors / 0 skipped

The preserved raw transcripts are INITIAL_TEST_OUTPUT_2026-10-05.txt, DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt and FINAL_TEST_OUTPUT_2026-10-05.txt. Their source/test/runner blob headers bind each result to the code actually executed. They contain only structural test evidence.

### Runtime defect and bounded production repair

RUNTIME_DEFECTS_FOUND = 1  
PRODUCTION_REPAIR_REQUIRED = TRUE

The failing regression was:
DisclosureTests.test_global_blocked_precedes_ambiguous_requested_recipient.

On the audited code, a ledger containing a BLOCKED disclosure evaluated globally as BLOCKED, but evaluate_for(..., recipient_actor_id="UNRESOLVED", ...) returned UNRESOLVED before consulting that global state. This violated the preserved global BLOCKED precedence requirement.

The repair in contract.py moves global ledger evaluation before requested-recipient resolution. A non-CLEAR global result is returned first; only a globally CLEAR ledger proceeds to resolve the requested recipient and exact tuple. The change does not grant permission, add a root, change approved actors, alter logging finalization or permit an ambiguous recipient. Both old and new branches are non-permissive; the repaired branch preserves the stronger blocking classification.

The initial failing test was retained unchanged. The full suite was rerun after repair.

### Test-runner issue and diagnostic evidence

The initial guard reported five denied file-open attempts. The diagnostic run established their exact paths: importlib lookups for the dedicated package's __init__, contract, harness, trusted_root and test module bytecode caches. No cache content, fixture or data was opened. Python handled each refusal by reading the allowlisted source.

The final runner still DENIES these exact local cache paths. It classifies those expected importlib lookups separately as code_cache_reads_blocked rather than unsafe file reads. It does not allow local bytecode to replace verified sources. All other non-allowlisted reads remain prohibited.

The diagnostic suite passed but its process exited 1 because the original guard counter still counted the five code-cache refusals as forbidden reads. This intermediate process failure is preserved, not hidden. No second production defect was found.

|Final audit counter|Value|
|---|---:|
|Network attempts|0|
|Subprocess attempts|0|
|Forbidden file attempts|0|
|Blocked local code-cache read attempts|5|
|Allowed code reads|51|

The runner uses -I -S -B, rejects network/subprocess calls and writes in the test process, and permits only the enumerated local .py files plus standard-library code reads after installing its audit hook. Source hashes are checked before package import. Shell redirection creates only the three documentary test transcripts inside the authorized directory. This in-process test boundary is not claimed to be a deployed security mechanism or a complete hostile-interpreter sandbox.

## Coverage of every required runtime family

Every test uses deterministic, obviously TEST_ONLY, metadata-only structural objects. There is no fixture payload, real input, efficacy calibration, economic measurement or operational source. The synthetic root is supplied only through a scoped patch of the harness module's resolver; the production trusted_root.py stays unchanged and returns None.

|Family|Test class / final count|Exercised cases|
|---|---|---|
|D1 trusted root|TrustedRootTests / 11|Absent production root denies read/admission/release/resource paths; coordinated caller substitution cannot create or replace the independent root; synthetic root positive paths; policy/construction/harness/version/root-authority mismatches; wrong action execution authority; restoration after patch|
|D2 provenance|ProvenanceTests / 24|Exact valid metadata-only contract; missing contract; wrong ID/generator/version/digest; missing/wrong/ambiguous/duplicate lineage; empty/missing/unexpected/duplicate reproducibility keys; wrong/empty/duplicate/prohibited/unknown classes; UNKNOWN/contaminated states; unresolved/blocked admissibility; changed metadata value digest|
|D3 recipients|RecipientTests / 11|Exact actor+role success with other gates valid; same allowed role/wrong actor; wrong mapped role even when manifest role allowed; ambiguous actor; separately CLEAR cumulative history does not supply recipient permission|
|D4 release approval|ReleaseApprovalTests / 9|Required independent approver; same recipient/approver identity denied; wrong release role, actor, action, authority, state and authorization ID|
|D5 public construction and exact logging|LoggingTests / 39|Direct PERMIT/AUTHORIZED decision rejection; direct permissive/fake acknowledged result rejection; missing/ambiguous/duplicate log IDs; append failure; wrong acknowledgement ID; absent/duplicate stored record; same ID/different content; exact acknowledgement/context success; context tampering; AUTHORIZED requires PERMIT; permissive requires COMPLETED+VALID|
|Manifests and role authorization|ManifestBindingTests / 44|Exact input/output digests; wrong expected digests after root bound to policy; tampering of every material input/output field; canonical order; duplicate field integrity; actor/role/action/authority/state/ID mismatches|
|Cumulative disclosure|DisclosureTests / 4|Exact output+actor+role tuple; empty ledger UNRESOLVED; global BLOCKED over CLEAR/UNRESOLVED including ambiguous requested recipient; public release denial|
|Resources|ResourceTests / 3|WITHIN_AUTHORITY exact value; valid test-root positive boundary; UNRESOLVED/EXCEEDED fail closed|

Private finalizer calls are bounded unit tests of the audited internal invariant; they are not asserted to be supported public API bypasses. The guarded-path tests also exercise public atomic action methods with append acknowledgements and exact context checks.

Final statuses:
D1_RUNTIME_STATUS = PASS_BOUNDED  
D2_RUNTIME_STATUS = PASS_BOUNDED  
D3_RUNTIME_STATUS = PASS_BOUNDED  
D4_RUNTIME_STATUS = PASS_BOUNDED  
D5_RUNTIME_STATUS = PASS_BOUNDED  
INPUT_MANIFEST_BINDING_RUNTIME_STATUS = PASS_BOUNDED  
OUTPUT_MANIFEST_BINDING_RUNTIME_STATUS = PASS_BOUNDED  
CUMULATIVE_DISCLOSURE_RUNTIME_STATUS = PASS_BOUNDED_AFTER_REPAIR  
RESOURCE_BOUNDARY_RUNTIME_STATUS = PASS_BOUNDED

## Exact commands and process context

Every shell command executed in this mission is recorded below, including setup and documentary reads. Repository materialization/edits used the patch tool; authority retrieval and publication used the GitHub governance connector. No shell clone, package install, network utility, unrelated program, pytest suite or hidden test run occurred.

Commands 1–2 used /workspace/scratch/eb92e26a9e5c. Commands 3–9 used /workspace/scratch/eb92e26a9e5c/a2_runtime_45f5c940. The initial rg inventory returned no matching local files (exit 1); it was not a test failure.

Command 1:

```bash
pwd
```

Command 2:

```bash
rg --files -g AGENTS.md -g pyproject.toml -g '*a2_harness*' -g '!data/**' -g '!results/**'
```

Command 3:

```bash
python -I -S -B research/weather_forward/v4/a2_harness/run_bounded_runtime_tests.py > research/weather_forward/v4/a2_harness/INITIAL_TEST_OUTPUT_2026-10-05.txt 2>&1
```

Command 4:

```bash
cat research/weather_forward/v4/a2_harness/INITIAL_TEST_OUTPUT_2026-10-05.txt
```

Command 5:

```bash
python -I -S -B research/weather_forward/v4/a2_harness/run_bounded_runtime_tests.py --allow-in-scope-repair > research/weather_forward/v4/a2_harness/DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt 2>&1
```

Command 6:

```bash
tail -n 8 research/weather_forward/v4/a2_harness/DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt
```

Command 7:

```bash
python -I -S -B research/weather_forward/v4/a2_harness/run_bounded_runtime_tests.py --allow-in-scope-repair > research/weather_forward/v4/a2_harness/FINAL_TEST_OUTPUT_2026-10-05.txt 2>&1
```

Command 8:

```bash
tail -n 8 research/weather_forward/v4/a2_harness/FINAL_TEST_OUTPUT_2026-10-05.txt
```

Command 9:

```bash
python -I -S -B -c 'import hashlib,json,pathlib; p=pathlib.Path("research/weather_forward/v4/a2_harness"); names=("test_bounded_runtime.py","run_bounded_runtime_tests.py","contract.py","INITIAL_TEST_OUTPUT_2026-10-05.txt","DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt","FINAL_TEST_OUTPUT_2026-10-05.txt"); result={}; [(result.update({n:{"content":(p/n).read_text(),"git_blob":hashlib.sha1(b"blob "+str(len((p/n).read_bytes())).encode()+b"\0"+(p/n).read_bytes()).hexdigest()}})) for n in names]; print(json.dumps(result))'
```


Commands 3, 5 and 7 are the only test-suite executions. Their process exits are shown above. All other shell commands completed with exit 0 except command 2. The final documentary read in command 9 reads only the explicit six source/test/transcript files and computes Git blob identities for publication verification; it invokes no harness behavior.

## Commit lineage and mutation scope

Base / mandatory Owner authority:
45f5c940140788bb96c7b6da8581d9aa7c627dfa

Initial tests and immutable initial failure evidence:
13f11dfd425534c58be79355b3ec81c7e45cfaab

Production repair plus diagnostic/final test evidence:
7bbae0bbb085269d63f4da5f356f203d3d5baed5

This report is added in a subsequent documentary commit whose sole parent is the repair commit above. No merge is performed. The exact report commit and branch HEAD are provided in the terminal handoff and can be resolved from Git history.

PRODUCTION_REPAIR_COMMITS = 7bbae0bbb085269d63f4da5f356f203d3d5baed5  
PRODUCTION_HARNESS_FILES_MODIFIED = research/weather_forward/v4/a2_harness/contract.py  
PRODUCTION_TRUSTED_ROOT_MODIFIED = FALSE  
EXTERNAL_DEPENDENCIES_ADDED = NONE  
FILES_MODIFIED_OUTSIDE_SCOPE = NONE

New files: test_bounded_runtime.py; run_bounded_runtime_tests.py; INITIAL_TEST_OUTPUT_2026-10-05.txt; DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt; FINAL_TEST_OUTPUT_2026-10-05.txt; BOUNDED_RUNTIME_TEST_EVIDENCE_2026-10-05.md, all under research/weather_forward/v4/a2_harness/.

|Final persisted artifact|Git blob before report publication|
|---|---|
|test_bounded_runtime.py|aa0159c2a470da034c6611e207687997294fb236|
|run_bounded_runtime_tests.py|25b7d3bde54e412a51df45059a65283479420725|
|contract.py|234c31b62b328fb906c2e2aa5054496a044b0746|
|INITIAL_TEST_OUTPUT_2026-10-05.txt|8fd3df623bc621c4cd045dbe7061acfda683155b|
|DIAGNOSTIC_TEST_OUTPUT_2026-10-05.txt|60f3f8e8e7e5fcb1fd7e441e72246c7ce64e2457|
|FINAL_TEST_OUTPUT_2026-10-05.txt|6cd6ad8cf43f9dc17e24b5bff9d5177559a733d0|

## Authority boundaries and evidence limits

TEST_ONLY_TRUSTED_ROOT_USED = TRUE  
TEST_ONLY_TRUSTED_ROOT != EXECUTION_POLICY_AUTHORITY  
PRODUCTION_TRUSTED_ROOT_MODIFIED = FALSE

NETWORK_ACCESSED_BY_TEST_PROCESS = NO  
GOVERNANCE_CONNECTOR_USED = AUTHORITY_READS_AND_GIT_PUBLICATION_ONLY  
FIXTURES_ACCESSED = NONE  
RESEARCH_FIXTURES_CREATED = NONE  
REAL_DATA_ACCESSED = NONE  
REAL_METADATA_ACCESSED = NONE  
ENDPOINTS_QUERIED = NONE_OPERATIONAL  
CREDENTIALS_USED = NONE_OPERATIONAL

The connector's mandatory authority/source retrieval and Git publication are separately disclosed and are not operational endpoint testing or network use by the harness. No operational credentials were acquired, inspected or passed to test code.

BUILDER_AUTHORITY = BOUNDED_OFFLINE_HARNESS_TEST_SCOPE_ONLY  
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE  
A2_FIXTURE_TESTING_AUTHORIZED = FALSE  
RESEARCH_FIXTURE_GENERATION_AUTHORIZED = FALSE  
A2_EXECUTION_AUTHORIZED = FALSE  
ECONOMIC_AUTHORITY = 0  
CAPTURE_AUTHORIZATION = NONE  
DATA_T0 = NOT_DECLARED  
EXPERIMENT_T0 = NOT_DECLARED  
REAL_CAPITAL_AUTHORIZED = FALSE  
LIVE_TRADING_AUTHORIZED = FALSE

BOUNDED_OFFLINE_HARNESS_TEST_PASS is limited to the exercised governance cases and interpreter/process context. It does not establish exhaustive runtime correctness, full deployed-control effectiveness, fixture approval, A2 execution readiness or economic validation.

ECONOMIC_PROGRESS = bounded evidence separates working governance invariants from a runtime classification defect, with the defect repaired without outcome exposure.  
REMAINING_BLOCKER = independent Astra runtime-test evidence audit; any later phase retains its own exact prerequisites and Owner authority.  
EXIT_CONDITION = ASTRA_INDEPENDENT_RUNTIME_TEST_EVIDENCE_AUDIT_ONLY.
