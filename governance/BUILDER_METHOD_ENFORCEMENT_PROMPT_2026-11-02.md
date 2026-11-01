# Quant-Trade — Builder prompt: real AI working-method enforcement

MISSION TYPE: METHOD ENFORCEMENT SEAM CLOSURE

Repository: fahimahmedb/Quant-Trade

## Objective

Close the gap between a working-method specification that passes unit/CI tests and a working method that is actually enforced on real AI missions.

Do NOT redesign the methodology. Do NOT restart the meta-audit. Do NOT create a new governance framework. Reuse and strengthen the existing canonical method.

The current correction is:

- METHOD_SPECIFICATION=PASS
- METHOD_UNIT_TESTS=PASS
- METHOD_ENTRYPOINT_WIRING=PASS
- METHOD_REAL_AGENT_ENFORCEMENT=NOT_PROVEN
- F1_RECOVERABLE_CANONICAL_STATE=NOT_PROVEN_BEHAVIORALLY

The evidence for this correction is that existing tests mainly validate synthetic mission fixtures and entrypoint consistency. A real agent was still able to begin creating a parallel post-resume program before explicitly reconciling the canonical working method, and the Owner had to redirect it. Therefore green tests were overinterpreted as behavioral enforcement.

## Mandatory bootstrap

Before mutating anything:

1. fetch/reconcile fresh `project/canonical` and `code/canonical`;
2. read `project/canonical:AGENTS.md`;
3. read `project/canonical:QUANT_NORTH_STAR.md`;
4. read `project/canonical:governance/AI_WORKING_METHOD_V1.md`;
5. read `project/canonical:governance/AI_WORKING_METHOD_V1.json`;
6. read `project/canonical:governance/CURRENT_PROJECT_STATE.md` plus any current overlay/receipt it explicitly delegates to;
7. read `project/canonical:governance/METHOD_ENFORCEMENT_GAP_2026-11-02.md` if present;
8. inspect `code/canonical:tests/test_ai_working_method.py` and `scripts/validate_ai_working_method.py` or their current equivalents;
9. reconcile against the fresh work of any concurrent Codex/Builder before publishing.

If the current operational-closeout Builder is mutating the same files/seam, do not overwrite it. Reconcile and either work on non-conflicting enforcement files or return `PARK_CONCURRENT_MUTATION` with the exact conflicting subject.

## Governing law

Use:

`REUSE > CONNECT > REPAIR > BUILD`

This mission is expected to be CONNECT/REPAIR, not a new architecture.

A solution that merely adds more prose or more synthetic unit tests is insufficient.

## Required result

A real material AI mission must not be able to proceed legitimately without first producing and validating a fresh mission-admission/bootstrap receipt against current canonical state.

The enforcement path must bind the real mission to:

- fresh `project/canonical` SHA;
- fresh `code/canonical` SHA;
- current router/current-state identity;
- current blocker or decision;
- target F0–F6 gate or current recorded blocker;
- existing-capability disposition: `REUSE | CONNECT | REPAIR | BUILD_REQUIRED | UNKNOWN`;
- why the proposed work can change the decision;
- minimal decisive test;
- one concrete counterexample;
- durable output required;
- next action after PASS/FAIL/BLOCK;
- Owner authorization requirement;
- concurrency/active-seam check.

The receipt must be a real input to the existing validator/enforcement path, not a documentation-only artifact.

## Minimum implementation requirements

### E1 — Real mission admission object

Create or reuse one compact machine-readable mission-admission schema/object.

Do not create a second methodology. It must be derived from `AI_WORKING_METHOD_V1.json` and the existing validator.

The object must identify the exact current canonical subjects and the real mission being proposed.

### E2 — Validator integration

Extend/reuse the existing validator so it can validate a real mission-admission object, not only internally created test fixtures.

It must fail closed at least for:

- stale project/code SHA;
- missing exact subject;
- missing blocker/decision;
- BUILD when equivalent capability is already established as REUSE/CONNECT/REPAIR;
- review with no new exact subject/evidence/counterexample/irreversible boundary;
- local-only/non-recoverable PASS claim;
- missing next action;
- unbounded global-stop caused by a local blocker;
- >2 active decision-changing lanes where the existing contract forbids it;
- missing required Owner authority for an irreversible action;
- completion claim while a required finish gate remains unresolved.

### E3 — Bootstrap receipt before substantive work

Define the smallest practical mechanism by which a Builder/Reviewer/Research/Operator mission records that it actually performed the mandatory bootstrap.

Do not rely on `AGENTS.md was present` as proof that it was read/applied.

The receipt must contain evidence values derived from fresh canonical state, so a copied/stale receipt cannot silently validate a new mission.

### E4 — Link admission to completion

A completion/PASS/handoff for a material mission must reference the validated mission-admission receipt or its immutable identity/hash.

A PASS without that link must be rejected or downgraded to an explicitly non-authoritative result.

Do not require this for trivial read-only informational queries that do not mutate project state or claim a project decision.

### E5 — Fresh-agent recovery test

Add a true behavioral acceptance test for F1.

Preferred form: launch/use a genuinely fresh agent/session with no conversation context and give it only the repository/bootstrap entrypoint. Ask it to recover:

1. project objective;
2. current authority pair;
3. fresh project/code SHAs;
4. current blocker/critical path;
5. current next action;
6. applicable working-method rules from the final meta-audit;
7. work that is already complete and must not be restarted;
8. whether its proposed next task is REUSE/CONNECT/REPAIR/BUILD;
9. what evidence would make it stop.

Acceptance requires the recovered answer to match durable canonical state and to avoid a parallel methodology/stale restart.

If the environment cannot launch an independent fresh agent/session, do NOT fake this test with another fixture in the same process. Return:

`F1_BEHAVIORAL_RECOVERY=BLOCK_ENVIRONMENT_FRESH_AGENT_UNAVAILABLE`

and still implement all other enforceable seams.

### E6 — Negative behavioral tests

Test at least these adversarial cases using the real admission interface:

A. stale SHA receipt;
B. copied receipt from an older mission;
C. BUILD proposal for an already-present capability;
D. duplicate review with no new evidence;
E. local-only result claiming PASS;
F. local blocker attempting to global-stop independent work;
G. missing next action;
H. false `QUANT_SYSTEM_V1_FINISHED` while any required gate is OPEN/BLOCK/UNKNOWN;
I. mission admission created before canonical head moves, then submission after head moves;
J. two concurrent Builders on the same seam if the state exposes that conflict.

For every test distinguish planned / executed / passed.

### E7 — CI/runtime enforcement

Wire the real mission-admission validation into the narrowest existing CI/workflow surface that can enforce it.

Do not claim server-side prevention if GitHub branch protections/rulesets are not available.

Distinguish:

- pre-work validation available to the agent;
- post-push CI detection;
- server-side required-check enforcement;
- behavioral enforcement by agent runtime.

If branch protection/admin permission remains unavailable, record:

`SERVER_SIDE_ENFORCEMENT=BLOCK_ADMIN_PERMISSION`

Do not call detection a prevention guarantee.

### E8 — No parallel memory layer

Do not make agents read a growing list of audits.

Promote only durable general rules to `AI_WORKING_METHOD_V1`/JSON.
Promote only current critical-path facts to `CURRENT_PROJECT_STATE` or its canonical machine-readable successor.
Keep detailed audit evidence historical.

If the recently created `POST_OPERATIONAL_RESUME_PROGRAM_2026-11-02.md` duplicates canonical method/router content, classify it and either:

- leave it as non-authoritative evidence with an explicit pointer/status; or
- fold only decision-changing deltas into canonical surfaces.

Do not create another mandatory bootstrap document.

## Acceptance criteria

The mission may return `PASS` only if all applicable points are demonstrated:

1. a real mission-admission object exists and binds fresh canonical identities;
2. the existing validator consumes that real object;
3. stale/copied/wrong-head receipts fail;
4. a material completion can be linked back to its admission identity;
5. negative adversarial tests actually execute and pass;
6. unit/CI tests remain green on the exact published SHA;
7. durable canonical state records the enforcement status and claim ceiling;
8. no new governance architecture was introduced;
9. a fresh-agent recovery test passes, OR it is explicitly BLOCKED because an independent fresh-agent execution surface is unavailable;
10. any unavailable server-side branch-protection enforcement is explicitly BLOCKED, not claimed.

## Claim ceiling

Do not report `AI_METHOD_FULLY_ENFORCED` unless BOTH are true:

- real-mission admission/completion enforcement is demonstrated; and
- fresh-agent behavioral recovery is demonstrated.

Otherwise use one of:

- `METHOD_ENFORCEMENT_PARTIAL`
- `METHOD_ENFORCEMENT_CODE_PASS_BEHAVIORAL_BLOCK`
- `BLOCK_CONCURRENT_MUTATION`
- `NO_CHANGE_REQUIRED`

## Required durable outputs

Prefer modifying existing canonical files/tests over adding documents.

At most add ONE compact enforcement receipt/status artifact if necessary.

Update the current router/machine-readable state only if the decision genuinely changes.

Do not generate a new audit corpus.

## Verification sequence

Before finalizing:

1. re-fetch fresh canonical heads;
2. ensure no concurrent work was overwritten;
3. execute targeted enforcement tests;
4. execute existing AI working-method regression tests;
5. execute the smallest relevant canonical regression suite;
6. verify remote exact SHA containing the changes;
7. verify CI/workflow result belongs to that exact SHA;
8. perform fresh-agent behavioral test if the environment supports it;
9. re-read the durable status from GitHub;
10. challenge the conclusion with one counterexample: “Can a material agent still legitimately begin and complete work without proving it reconciled current canonical state?”

If YES, mission is not complete.

## Final response contract

Return:

`MISSION_STATUS=`
`PROJECT_CANONICAL_SHA=`
`CODE_CANONICAL_SHA=`
`EXISTING_CAPABILITY_DISPOSITION=`
`REAL_MISSION_ADMISSION_IMPLEMENTED=`
`REAL_MISSION_VALIDATOR_INTEGRATED=`
`ADMISSION_TO_COMPLETION_BINDING=`
`STALE_RECEIPT_REJECTED=`
`WRONG_SHA_REJECTED=`
`DUPLICATE_REVIEW_REJECTED=`
`UNNECESSARY_BUILD_REJECTED=`
`LOCAL_ONLY_PASS_REJECTED=`
`LOCAL_BLOCKER_GLOBAL_STOP_REJECTED=`
`FALSE_FINISH_REJECTED=`
`FRESH_AGENT_RECOVERY_TEST=`
`SERVER_SIDE_ENFORCEMENT=`
`TESTS_PLANNED=`
`TESTS_EXECUTED=`
`TESTS_PASSED=`
`CI_EXACT_SHA=`
`DURABLE_STATE_UPDATED=`
`CLAIM_CEILING=`
`BLOCK=`
`PARK=`
`UNKNOWN=`
`NEXT_ACTION=`

Also list every file changed and the exact commit SHA.

## Stop law

Stop when the enforcement seam is proven or a bounded environmental/admin blocker is established.

Do not continue into host migration, mission selection, scientific experiments, capital, live trading, repository archaeology or another meta-audit.

The mission is only:

`DECLARATIVE_METHOD -> REAL_MISSION_ENFORCEMENT -> BEHAVIORAL_RECOVERY_PROOF`
