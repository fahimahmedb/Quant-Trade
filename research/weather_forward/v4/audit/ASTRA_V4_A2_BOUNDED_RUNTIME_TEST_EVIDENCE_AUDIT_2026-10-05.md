# ASTRA — Weather V4 A2 bounded runtime-test evidence audit — 2026-10-05

MISSION_CLASS = INDEPENDENT_BOUNDED_OFFLINE_HARNESS_RUNTIME_TEST_EVIDENCE_AUDIT
AUDIT_BRANCH = astra/weather-v4-a2-bounded-runtime-test-evidence-audit-2026-10-05
AUDIT_PARENT_SHA = a13a15ff41b231628bb55613edc2fef060e35e48
AUDIT_TARGET_SHA = a13a15ff41b231628bb55613edc2fef060e35e48
AUDIT_VERDICT = PASS_BOUNDED_RUNTIME_TEST_EVIDENCE
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_A2_PREREQUISITES_ONLY

## Authority, ancestry and mutation scope

Git commit objects independently resolve this direct, single-parent chain:

2bc718711d507b38176981c2b3e55dd607c9547b
→ 976da7e0190b899bd9982e9e0565d68fecdddb6d
→ 45f5c940140788bb96c7b6da8581d9aa7c627dfa
→ 13f11dfd425534c58be79355b3ec81c7e45cfaab
→ 7bbae0bbb085269d63f4da5f356f203d3d5baed5
→ a13a15ff41b231628bb55613edc2fef060e35e48

The Builder branch ref was independently resolved to the exact target. The required Owner artifact at 45f5c940... has blob 2201905c60b19c915cc9ae4ef655ff7c48fa16ec. It explicitly authorizes bounded offline governance tests, synthetic structural dependencies and necessary production repairs of already-authorized invariants within a2_harness, followed by independent Astra review. The prior Astra report at 976da7e0... has blob a703cbdbd76dcf14b903c12c96c8199376cbfbac and verdict PASS_FOR_OWNER_CONSIDERATION_OF_BOUNDED_TEST_AUTHORITY. It binds the original harness 2bc71871... and provides no operational execution authority.

Owner-to-target Git comparison is ahead by three commits with no other intervening commits or merge. Its entire mutation set is six new test/runner/transcript/evidence files and contract.py, all under research/weather_forward/v4/a2_harness/. The sole production change is the three-line relocation in CumulativeDisclosureLedger.evaluate_for. harness.py, trusted_root.py, __init__.py and README.md are unchanged. No existing Owner, Blue, Astra, src, historical runner or fixture artifact is modified.

OWNER_AUTHORITY_VERIFIED = TRUE
STATIC_PASS_VERIFIED = TRUE
BUILDER_LINEAGE_VERIFIED = TRUE
SCOPE_COMPLIANCE = PASS_BOUNDED_SOURCE_AND_EVIDENCE_REVIEW

## Method and epistemic separation

Astra read Git source, metadata, patches and existing documentary transcripts. No Python was executed, no harness was imported, no test or CI was run, and no fixture payload was read. Git blob hashes were recomputed with git hash-object --stdin over retrieved UTF-8 content; this is identity verification, not execution of that content.

Independently verified facts: exact parent objects, branch ref, mutation paths, retrieved blob identities, byte-identical retained test module, identical 145 transcript test names, transcript contents and source semantics.

Transcript facts: named test outcomes, summaries, source headers and audit counters as recorded. These are existing Builder evidence, not independently observed execution.

Builder-reported process facts: command lines, minimal materialization, process exit statuses 1/1/0, external activity declarations and original process context. Raw transcripts do not independently attest OS exit status or completeness of the Builder's command history.

Source-derived conclusions: exercised gates, scoped/restored mocks, repaired semantics, runner accounting and the exit statuses implied by the recorded summaries. Source/header consistency cannot prove that a historical process actually ran those bytes, nor certify deployed controls.

## Source and transcript identities

|Artifact|Verified Git blob|
|---|---|
|test_bounded_runtime.py, initial and final|aa0159c2a470da034c6611e207687997294fb236|
|initial runner at 13f11dfd...|f8f33cd38e275b2c4271b1c93df72212e0b566c1|
|final runner|25b7d3bde54e412a51df45059a65283479420725|
|original contract.py|db978016cb2eab91e3b7569de350d0fc65641889|
|repaired contract.py|234c31b62b328fb906c2e2aa5054496a044b0746|
|harness.py|00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4|
|trusted_root.py|9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94|
|__init__.py|bf9a2bdba7658454ea10009a28c975024365cfe1|
|README.md|b3b74326d2d41f1d88c9e891186a5af9a663f095|
|initial transcript|8fd3df623bc621c4cd045dbe7061acfda683155b|
|diagnostic transcript|60f3f8e8e7e5fcb1fd7e441e72246c7ce64e2457|
|final transcript|6cd6ad8cf43f9dc17e24b5bff9d5177559a733d0|

Retrieved bytes independently hash to these Git API identities. All source headers agree with the corresponding original or repaired sources. The final runner/test headers agree with final committed runner/test blobs. Initial and final test contents are equal; the repair commit does not touch the test module. Each transcript contains the same 145 unique named cases in the same order.

The intermediate diagnostic runner header is 023a4de0fbaf40d9adc084863de2151423de948a. Direct Git blob retrieval returned 404: it is not recoverable as a committed intermediate runner through the inspected lineage. Astra recovered its bytes deterministically from the initial committed runner using only these three instrumentation additions:

1. Insert `blocked_code_paths = []` immediately before the audit_counts definition.
2. In the non-allowlisted-read branch, insert `blocked_code_paths.append(str(candidate))` before incrementing forbidden_file_attempts.
3. Add `"denied_read_paths": blocked_code_paths,` immediately after the summary's offline_audit entry.

All original bytes, indentation and LF newlines are otherwise retained. Independently recomputed Git blob identity of that reconstruction is exactly 023a4de0fbaf40d9adc084863de2151423de948a. This resolves the intermediate source semantics and header consistency without claiming retrieval of an original Git object or replay. The reconstruction adds diagnostics only; it does not change permission or exit logic. Lack of a directly persisted diagnostic runner is a nonmaterial archival limitation because exact bytes can be reconstructed and the final runner is committed and verified.

SOURCE_TRANSCRIPT_BINDING = VERIFIED_CONTENT_IDENTITIES_WITH_RECONSTRUCTED_DIAGNOSTIC_RUNNER

## Preserved runs and incident

|Run|Recorded run/pass/fail/error/skip|Expected failures / unexpected successes|Builder exit|Source-implied exit|
|---|---|---|---|---|
|Initial|145 / 144 / 1 / 0 / 0|0 / 0|1|1|
|Diagnostic|145 / 145 / 0 / 0 / 0|0 / 0|1|1|
|Final|145 / 145 / 0 / 0 / 0|0 / 0|0|0|

Initial failure is DisclosureTests.test_global_blocked_precedes_ambiguous_requested_recipient: UNRESOLVED is not BLOCKED. The same assertion remains in final source, comparing evaluate_for with ambiguous recipient "UNRESOLVED" against BLOCKED. Its final recorded result is ok. No skip, expected-failure decorator, waiver, weakened assertion or substitution of the production ledger evaluator exists.

Initial transcript records five forbidden reads but does not enumerate their paths. Diagnostic evidence enumerates the five exact importlib cache paths for __init__, contract, harness, trusted_root and the test module. Its guards_clear remains false, explaining exit 1 despite all tests passing. Source restoration through importlib fallback is consistent with the cache PermissionErrors and subsequent source imports; it is not independent interpreter tracing.

Final source computes the exact cache paths from the five allowlisted source files. Each matching read still raises PermissionError before bytes can be opened. It increments a separate blocked-cache counter rather than forbidden_file_attempts. Write detection precedes cache classification. Other forbidden reads still increment forbidden_file_attempts and fail; network and subprocess event handling precede open handling and are unchanged. The final summary records five blocked caches, zero forbidden reads, zero network attempts and zero subprocess attempts. No cache glob or general pyc allowance is introduced for local repository files.

--allow-in-scope-repair is an explicit argument, not an authority grant. It permits changed contract.py or harness.py, forbids trusted_root.py changes and any other enumerated production-file changes, and prints actual changed source identities. Actual final evidence reports only the authorized contract.py repair. The option does not pin a specific approved repair digest; manual exact-source/authority review is therefore necessary and is provided here. Preflight hashes and standard-library imports occur before installation of the audit hook. The hook is a bounded in-process test aid, not a deployed security sandbox or proof of absence of all possible hostile interpreter behavior.

RUNNER_ACCOUNTING_CHANGE_VALID = TRUE_FOR_REVIEWED_BOUNDED_RUN
INITIAL_FAILURE_PRESERVED = TRUE
TEST_ASSERTIONS_WEAKENED = FALSE

## Coverage and gate reachability

|Family|Recorded cases|Assessment|
|---|---:|---|
|D1 trusted root|11|Absent production root denies read, metadata admission, release and resource validation. Coordinated caller substitution cannot provide a root. Scoped synthetic-root positives exercise all three public authority-bearing paths, with restoration asserted. Root mismatches change the root alone and reach root validation.|
|D2 provenance|24|Metadata-only positive admission; missing contract and wrong contract digest use a root matching the changed policy, so they reach provenance validation. Provenance mutations leave root/policy/binding/authorization/log valid, reaching the intended provenance gate. Identity, generator/version, classes, lineage, reproducibility keys/values, contamination, admissibility and digest are covered.|
|D3 exact recipient|11|Positive release and wrong actor/role/ambiguous identities. A separately CLEAR ledger for a different actor still denies recipient authorization. A wrong mapped role remains allowed by the manifest so it reaches the exact actor-role gate.|
|D4 independent approval|9|Same recipient/approver identity uses matching authorization and is denied for RELEASE_INDEPENDENCE_VIOLATION. Wrong approver role uses matching authorization role. Remaining authorization mutations retain valid manifests, independent approver and recipient, reaching role/action/authority/state/ID validation.|
|D5 final logging|39|Public direct permissive construction rejects. Public valid paths have exact acknowledged linkage. Append refusal, wrong acknowledgement ID, missing/duplicate stored records and same-ID/different-content fail closed. Internal finalizer mutations have a valid baseline and change one expected context/state; unique record/equality, authorities, actors, action, target, manifest, incident, cumulative and recipient contexts are covered. AUTHORIZED implies PERMIT and permissive implies COMPLETED + VALID are tested.|
|Manifest binding|44|Positive exact bindings; wrong policy digests bind the test root to the changed policy before reaching manifest checks. All 17 input and 13 output fields receive tampering and digest inequality checks. Canonical field order remains accepted; duplicate fields remain bound rather than deduplicated. Reader authorization mutations exercise valid earlier gates.|
|Cumulative disclosure|4|Exact output/actor/role tuple misses, empty UNRESOLVED ledger, global BLOCKED over CLEAR/UNRESOLVED and ambiguous requested recipient. Public release cases use a valid authorized recipient and approval; they reach cumulative disclosure rather than an earlier recipient gate.|
|Resource boundary|3|Exact WITHIN_AUTHORITY enum/value and positive validation under synthetic root; UNRESOLVED and EXCEEDED deny with RESOURCE_BOUNDARY_UNRESOLVED after valid authority.|

Tests use only deterministic TEST_ONLY structural objects and metadata; no outcome-bearing fixture exists in them. unittest.mock.patch.object substitutes only the imported trusted-root resolver, and malicious append acknowledgements for D5 dependency-failure tests. It does not replace ledger evaluation, manifest/provenance validation, role/recipient checks or finalization. Resolver patches are context managed; positive restoration assertions observe None afterwards. Production trusted_root.py still returns None and both current-root constants remain None.

Some parameterized tests assert DENY/BLOCKED/non-VALID without an exact reason or detail code. This is less diagnostic than exact denial assertions but source inspection confirms valid unchanged earlier gates and the intended changed validation family. Certain manifest mutations intentionally reach a structural prerequisite within manifest validation before its final digest comparison; their digest inequality is independently asserted. They prove tamper binding and fail-closed rejection, not separate coverage of every downstream semantic branch. D5 private helper tests supplement public paths; they do not claim unsupported internal mechanisms are public APIs.

Required bounded families have adequate positive and negative coverage. Nonmaterial gaps include lack of exact detail-code assertions in every generated negative, no exhaustive permutation/type/concurrency testing, no actual byte/time/resource-consumption ceiling enforcement tests, and no separately root-rebound tests of every output semantic restriction after matching a modified manifest digest. Resource evidence concerns the authorized enum boundary contract, not numerical consumption limits.

## Production repair and regressions

Owner sections 2 and 6 authorize necessary repairs of already-audited invariants inside a2_harness. The retained initial failure exposes global BLOCKED precedence required explicitly by Owner section 4. This exact repair is authorized.

Previously evaluate_for returned UNRESOLVED for an ambiguous requested recipient before consulting a globally BLOCKED ledger. It now calls evaluate first and returns any non-CLEAR global result before recipient resolution. A globally CLEAR ledger still checks recipient ambiguity and still requires exact output_id + recipient_actor_id + recipient_role matching. Empty or globally UNRESOLVED ledgers remain UNRESOLVED. No new path from a previously denied input to CLEAR is introduced by the relocation.

Both BLOCKED and UNRESOLVED remain nonpermissive at output release. A public ambiguous recipient is denied earlier by exact recipient authorization; the direct ledger regression correctly tests the repaired ledger classification independently. D1 root, D2 provenance, D3 recipient authorization, D4 approval, D5 logging and resource code are unchanged. No material regression or authority widening attributable to this repair was found.

PRODUCTION_REPAIR_ACCEPTABLE = TRUE
MATERIAL_REGRESSIONS = NONE_FOUND_WITHIN_REVIEWED_SCOPE
PRODUCTION_TRUSTED_ROOT_MODIFIED = FALSE

## Limits, verdict and continued boundaries

PASS accepts adequate bounded synthetic runtime-test evidence and the reviewed repair. It does not certify independent replay, exhaustive runtime correctness, historical-process authenticity, adversarial sandbox completeness, numerical resource enforcement, actual fixtures, A2 execution readiness or economic gain.

Scope compliance is established from reviewed source and documentary evidence; external-activity absence outside those observations remains Builder-reported. Mandatory Git governance reads and this documentary publication are distinct from operational endpoints or harness network use. No operational data, metadata, credential, endpoint, fixture or economics was accessed by Astra.

INDEPENDENT_REPLAY_PERFORMED = FALSE
CODE_EXECUTED = NO
TESTS_RUN_BY_ASTRA = NO
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED

AUDIT_VERDICT = PASS_BOUNDED_RUNTIME_TEST_EVIDENCE
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_A2_PREREQUISITES_ONLY

The reviewed control-plane evidence is a prerequisite contribution to Quant's research integrity, not empirical edge or economic validation. Any later phase requires its own exact prerequisites and Owner authority.
