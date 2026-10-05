# ASTRA — D5 type-boundary repair and consolidated bounded runtime evidence — 2026-10-05

MISSION_CLASS = INDEPENDENT_D5_TYPE_BOUNDARY_REPAIR_AND_CONSOLIDATED_BOUNDED_RUNTIME_TEST_EVIDENCE_AUDIT
AUDIT_BRANCH = astra/weather-v4-a2-d5-type-repair-runtime-evidence-audit-2026-10-05
AUDIT_PARENT_SHA = 78d537de681363ed83a6c7787aba4319f3c73c4d
AUDIT_TARGET_SHA = 78d537de681363ed83a6c7787aba4319f3c73c4d
AUDIT_VERDICT = PASS_D5_TYPE_REPAIR_AND_BOUNDED_RUNTIME_EVIDENCE
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_A2_PREREQUISITES_ONLY

## Authority, direct lineage and scope

Owner artifact at 45f5c940140788bb96c7b6da8581d9aa7c627dfa was read directly; its blob is 2201905c60b19c915cc9ae4ef655ff7c48fa16ec. Sections 2 and 6 authorize bounded offline governance tests and necessary repairs of already-authorized invariants inside a2_harness. Section 4 explicitly requires that public direct construction cannot manufacture permissive/authorized completed state without acknowledged exact logging. The new regression and repair are within that authority.

The historical static report at 976da7e0190b899bd9982e9e0565d68fecdddb6d, blob a703cbdbd76dcf14b903c12c96c8199376cbfbac, was read as historical evidence only. Its verdict is PASS_FOR_OWNER_CONSIDERATION_OF_BOUNDED_TEST_AUTHORITY. It does not certify this repair, and neither that report nor the earlier 145-test evidence adequately covered raw-string state substitution. The present verdict is independently based on the exact new target.

Git commit objects establish this sole-parent chain, without merge:

45f5c940140788bb96c7b6da8581d9aa7c627dfa
→ 13f11dfd425534c58be79355b3ec81c7e45cfaab
→ 7bbae0bbb085269d63f4da5f356f203d3d5baed5
→ a13a15ff41b231628bb55613edc2fef060e35e48
→ d1126ba4f1ed044431633d8338fb5269c2133e06
→ 3752458336d349d425c7b9f8395871e31d08e35f
→ 78d537de681363ed83a6c7787aba4319f3c73c4d

The Owner commit's parent is 976da7e0190b899bd9982e9e0565d68fecdddb6d. Builder branch ref resolves exactly to 78d537de... . Owner-to-target comparison is six commits ahead and zero behind. Base-to-target comparison is three commits ahead and zero behind, containing only six new dedicated test/runner/transcript/report files and modified contract.py under research/weather_forward/v4/a2_harness/.

Regression evidence commit contains no production change. Repair commit modifies contract.py and adds the final transcript. Final target adds the documentary evidence report. No other production file, existing test, previous transcript, Owner/Blue/Astra artifact, fixture, src or historical runner is changed.

OWNER_AUTHORITY_VERIFIED = TRUE
LINEAGE_VERIFIED = TRUE
SCOPE_COMPLIANCE = PASS

## Independent source findings at the supported public boundary

D5_STATUS = CLOSED_UNDER_SUPPORTED_PUBLIC_API_STANDARD

HarnessDecision validates runtime enum families for validation, permit, quarantine, release and completion, and StopReason or None, before state comparisons or assignment. There is no string-to-enum conversion. Direct construction then requires permit exactly DENY and release exactly BLOCKED. The original counterexample with strings "PERMIT" and "AUTHORIZED" raises TypeError before it can be stored. Mixed typed/untyped variants also reject. Correctly typed denial/error states remain constructible; validation, quarantine or completion alone is not execution permission.

LoggedActionResult requires type(decision) exactly HarnessDecision, revalidates its states, requires an exact StructuredAuditLog, and requires type(log_acknowledged) exactly bool. It rejects permissive decisions, any acknowledgement other than exactly False, and any non-null linked record. Duck-typed decisions, decision subclasses, 0/1, None, strings and lists cannot supply a public acknowledged result. A denial-only log object does not grant permission; the public wrapper does not claim exhaustive validation of every nested denial-log field.

dataclasses.replace re-enters the public constructor. Invalid states are revalidated; typed PERMIT/AUTHORIZED replacements are rejected by the denial-only condition. Replacing a guarded authorized decision or result therefore cannot copy or manufacture supported permissive state through ordinary replacement. The suite explicitly exercises invalid-state replacements, non-boolean acknowledgement replacements, valid denial replacements and rejection of replacing a guarded result. No new attack test uses object.__new__ or object.__setattr__.

Guarded finalization validates decision-state types first and returns None on invalid types. It requires exact LogAppendAcknowledgement, appended exactly True, exact StructuredAuditLog and LogRecord, tuple records containing actual LogRecord objects, and typed logged permit/quarantine/release states before linkage checks. Non-boolean truthy acknowledgements are rejected. Malformed checked objects return None, rather than allowing a permissive result.

The prior exact linkage requirements are retained: acknowledged record ID, exactly one stored record, complete dataclass content equality, construction/execution/authorization authorities, actor ID/role, authorization ID, action, target kind/ID, manifest/provenance identity, incident, cumulative state and recipient ID/role. Logged permit/release/quarantine must match the requested final states. AUTHORIZED requires PERMIT; DENY requires BLOCKED release; permissive results require VALID and COMPLETED. Exact successful guarded public paths remain structurally valid.

Private allocation/finalization helpers remain internal and absent from package exports. Deliberately invoking private allocation or circumventing frozen objects through low-level object-model manipulation is excluded by the specified supported-public-API standard; it is not claimed to be prevented by Python isolation.

PUBLIC_STRING_STATE_BYPASS = CLOSED
PUBLIC_DUCK_DECISION_BYPASS = CLOSED
NON_BOOLEAN_ACKNOWLEDGEMENT_BYPASS = CLOSED
EXACT_LOG_LINKAGE = PRESERVED
GUARDED_POSITIVE_PATH = PRESERVED

## Regression evidence and source identity

|Run|Recorded run/pass/fail/error/skip|Builder-reported exit|
|---|---|---|
|First pre-repair|279 / 155 / 120 / 4 / 0|1|
|Confirmed pre-repair|279 / 159 / 120 / 0 / 0|1|
|Final|279 / 279 / 0 / 0 / 0|0|

All transcripts contain the same 279 unique named tests, including the same original 145 tests. All 145 baseline cases are recorded ok in each new run. The same 120 tests fail in both pre-repair runs. Expected failures and unexpected successes are zero; no skip or xfail waiver is present.

The first four ERROR entries are ack_type_one, ack_type_false_string and their replace equivalents. Their tracebacks show ValueError: ACKNOWLEDGED_LOG_LINK_REQUIRES_GUARDED_FINALIZER. The original expectations required TypeError. Two parameterized assertRaises clauses were changed to accept (TypeError, ValueError), correcting those four outcomes without allowing construction. The unchanged 120 failures remain visible in the confirmed run. Confirmed pre-repair and final regression modules are byte-identical: the same rejection requirements are tested before and after repair.

|Artifact|Verified Git blob identity|
|---|---|
|pre-repair contract.py|234c31b62b328fb906c2e2aa5054496a044b0746|
|final contract.py|f6f94a4a472e3f6652a1502f6afb5825721364d0|
|confirmed/final D5 regression tests|52bb94ed7fa497bb9756afe02052b855dcd3d9f5|
|D5 runner, all three headers|f660a24d969e50db62ed6165c15272d90cb86b4b|
|original 145-test module|aa0159c2a470da034c6611e207687997294fb236|
|new initial transcript|e5f98e5bfa4d307353c2492f8531a5b38ed59feb|
|new confirmed initial transcript|c334e2e7aa2a8385b426ba5292ece6a3e57a0b63|
|new final transcript|f0fbf7f1b63fa44b8db178d740c8730962b637cc|
|harness.py|00ae81d2823b7d30d72aabe8d82ac051dbfcf5c4|
|trusted_root.py|9d8adeca4b61e42c40bd7f9ec85e4f3b676b1b94|
|__init__.py|bf9a2bdba7658454ea10009a28c975024365cfe1|

The retrieved new production/test/runner/transcript bytes independently recompute to their Git blob identities. Final headers match final committed sources. Pre-repair contract at regression commit matches the prior base identity. The original test module at a13a15ff... was compared directly with target contents and is byte-identical. No original assertion was changed.

First-run D5 test header is 888a2167c6aeffb6d6d48f4fc24fd6a05d6813b7. Git blob retrieval returned 404; that historical source object is not directly recoverable through the reviewed Git evidence. Deterministically replacing the two exact occurrences of self.assertRaises((TypeError, ValueError)) in the committed regression module with self.assertRaises(TypeError), preserving all other bytes and LF newlines, independently recomputes to that exact first-run Git blob identity using git hash-object. Thus the historical test bytes and correction scope are recovered, while direct availability of the original Git object is explicitly not claimed. The first-run production and runner identities are available and match committed pre-repair production and runner content.

REGRESSION_EVIDENCE_INTEGRITY = ADEQUATE_WITH_HASH_MATCHED_HISTORICAL_TEST_RECONSTRUCTION
ASSERTION_CORRECTIONS_ACCEPTABLE = TRUE
ORIGINAL_145_TESTS_PRESERVED = TRUE

## Gate reachability and consolidated coverage

New public constructor/type tests start with correctly typed DENY/BLOCKED arguments, change the target field, and require rejection. Replacement tests start from a valid constructible denial. Duck decisions and wrong-log tests retain valid remaining arguments, so rejection is attributable to the intended object/type boundary.

Finalizer tests derive an exact successful acknowledged context from original public positive paths. Invalid validation/completion cases switch to a matched typed denial log, avoiding unrelated permissive VALID/COMPLETED rejection. For permit/release/quarantine mutations the linked record is changed as well, avoiding mere state mismatch as the explanation. At the repaired target all invalid-state cases reach the entry type checks. Some malformed release cases were already rejected under pre-repair denial/release consistency: not every green negative case represents a newly closed defect. The preserved 120 failing cases provide the regression discrimination. Exact positive, same-ID/different-content, duck acknowledgement and replace-guarded-result controls supplement the matrix.

The original 145 cases independently remain relevant: D1 11, D2 24, D3 11, D4 9, prior D5 39, manifests/reader authorization 44, disclosure 4 and resource states 3. Positive root patches are scoped unittest.mock contexts and restoration is asserted. Mocks replace only the test dependency resolver or malicious append acknowledgements, not the checks under evaluation.

Wrong expected manifest/provenance digests use a synthetic root matching the changed policy so earlier root mismatch does not mask the intended gate. Provenance attacks retain valid policy/root/authorization. Recipient cases distinguish exact actor-role permission from CLEAR disclosure history; independent-approver tests retain matching authorization. Cumulative cases retain valid recipients and approval. Original append/linkage failures exercise otherwise valid public actions; internal exact-context tests have positive controls.

Earlier 145-test evidence is preserved at target: initial transcript 8fd3df623bc621c4cd045dbe7061acfda683155b records 144/145 passing and the global BLOCKED/ambiguous-recipient failure; diagnostic 60f3f8e8e7e5fcb1fd7e441e72246c7ce64e2457 records 145 passing with five forbidden cache attempts; final 6cd6ad8cf43f9dc17e24b5bff9d5177559a733d0 records 145 passing with cache denials separately accounted. Builder reports exits 1/1/0, consistent with recorded summaries and runner logic. The diagnostic intermediate runner's original Git object was unavailable in the prior evidence audit; exact source was recovered there with hash 023a4de0fbaf40d9adc084863de2151423de948a. This archival limitation remains distinct from the fully committed new D5 runner.

## Preservation, runner boundaries and limits

The production diff adds type/object checks and tightens public denial and acknowledgement conditions. It does not modify manifests, provenance, root resolution, actor/role/action authorization, recipient mapping, release independence or resource boundaries. Cumulative disclosure still evaluates global non-CLEAR state before ambiguous recipient resolution and still matches output_id + recipient_actor_id + recipient_role exactly. No permission widening or material D1–D4/prior-D5 regression attributable to this repair was found.

trusted_root.py and package exports are unchanged. Both production current-root constants remain None and the resolver returns None. Synthetic roots are test-only structural dependencies, not authority. No real fixture payload or outcome is present in the reviewed new tests.

The new runner allows only the six local source modules plus permitted standard-library code reads after installing the in-process hook. All six exact local bytecode-cache paths still raise PermissionError. Writes are rejected before cache classification; unrelated forbidden reads still count and fail. Network/subprocess event checks and zero-counter exit requirements remain. The final transcript records six denied caches and zero network, subprocess and forbidden-file attempts. --allow-in-scope-repair permits changes only to contract.py, prints exact source differences, and refuses trusted_root.py or other production changes. It is an explicit source-review escape hatch, not Owner authorization or automatic validation of an arbitrary repair digest.

Preflight source reads and standard-library imports precede hook installation. Neither that hook nor recorded counters constitute deployed isolation, complete hostile-interpreter defense or independent observation of all historical activity.

Nonmaterial coverage gaps: no exhaustive input combinations, subclass/metaclass attacks, concurrency or hostile object-model tests; not every malformed nested log container has a dedicated negative test; some older generated negatives lack exact denial/detail-code assertions. Source checks supplement those bounded tests. Denial/error objects may contain correctly typed VALID or COMPLETED states without permission; DENY/BLOCKED remains mandatory. Resource-state tests establish enum-state fail-closed behavior only and do not prove numerical CPU/memory/time/volume enforcement. No unrelated resource redesign is required by this audit.

D1_D4_REGRESSIONS = NONE_FOUND_WITHIN_SCOPE
OTHER_MATERIAL_REGRESSIONS = NONE_FOUND_WITHIN_SCOPE

## Epistemic separation and terminal boundaries

Independently verified: exact Git parent/ref identities, mutation paths, source/transcript content identities, hash-matched first-run test reconstruction, identical confirmed/final regression source, preserved baseline bytes, named outcomes and source semantics.

Printed transcript facts: counts, named successes/failures/errors, source headers and audit counters. These are existing evidence; their internal consistency is verified.

Builder-reported facts: executed commands, OS process exits 1/1/0, original materialization and absence of out-of-scope external activity. The runner source implies those exits given the recorded summaries, but Astra did not observe the processes or independently attest complete historical execution.

Source-derived conclusion: ordinary supported constructors and dataclasses.replace cannot manufacture PERMIT/AUTHORIZED state without guarded exact acknowledged linkage. PASS is bounded to the reviewed source and exercised synthetic cases. It is not independent replay, exhaustive correctness, historical-process authenticity, deployed-control effectiveness, fixture approval, A2 readiness or economic validation.

INDEPENDENT_REPLAY_PERFORMED = FALSE
CODE_EXECUTED = NO
TESTS_RUN_BY_ASTRA = NO
PRODUCTION_TRUSTED_ROOT_MODIFIED = FALSE
A2_FIXTURE_GENERATION_AUTHORIZED = FALSE
A2_FIXTURE_TESTING_AUTHORIZED = FALSE
A2_EXECUTION_AUTHORIZED = FALSE
ECONOMIC_AUTHORITY = 0
CAPTURE_AUTHORIZATION = NONE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED
EXPERIMENT_T0 = NOT_DECLARED

Astra performed source/evidence review and content hashing only; no Python, harness import, test or CI execution, fixture access, operational endpoint, credential or economic activity occurred. Git governance retrieval and this report publication are distinct from operational activity.

AUDIT_VERDICT = PASS_D5_TYPE_REPAIR_AND_BOUNDED_RUNTIME_EVIDENCE
NEXT_SAFE_ACTION = OWNER_REVIEW_OF_A2_PREREQUISITES_ONLY
