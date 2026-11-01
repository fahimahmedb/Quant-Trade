# Quant-Trade — No-Repeat Operating System

DATE=`2026-11-01`
STATUS=`ACTIVE_RECOMMENDATION_METHOD`
PURPOSE=`Prevent recurrence of the failure modes already proven by the retrospective and forensic reconstruction while keeping Quant-Trade moving toward economic value.`

This is not a new governance layer. It is the minimum admission filter for recommendations, missions, reviews and autonomous work.

## 1. Governing objective

Every recommendation must answer one question first:

> What current decision, blocker or measurable project outcome can this action change?

If the answer is unclear, the default disposition is `PARK` or `NO_CHANGE_REQUIRED`.

Progress is preferred over activity.

The current ordering remains:

`REUSE > CONNECT > REPAIR > BUILD`

Valid non-action results remain:

`NO_CHANGE_REQUIRED`, `PARK`, `BLOCK`, `UNKNOWN`.

## 2. Recommendation admission gate

No recommendation becomes executable until all eight fields below are filled.

1. `CURRENT_SUBJECT`
   - exact branch / SHA / issue / runtime / scientific object concerned;
   - never act on a stale prompt or narrative without reconciling current durable state.

2. `CURRENT_DECISION_OR_BLOCKER`
   - one sentence;
   - classify it as `CODE`, `INTEGRATION`, `RUNTIME`, `EVIDENCE`, `AUTHORITY`, `SCIENCE`, `DATA`, `ECONOMICS`, or `EXTERNAL_ACCESS`.

3. `EXISTING_CAPABILITY_CHECK`
   - prove whether equivalent capability already exists;
   - outcome must be `REUSE`, `CONNECT`, `REPAIR`, `BUILD_REQUIRED`, or `UNKNOWN`.

4. `DECISION_IMPACT`
   - state exactly what becomes decidable after the action;
   - if the action cannot change a decision, move it to `PARK`.

5. `MINIMAL_DECISIVE_TEST`
   - smallest test or observation capable of proving or falsifying the recommendation;
   - no broad audit when a bounded test can decide.

6. `COUNTEREXAMPLE`
   - one concrete way the recommendation could be wrong;
   - perform this challenge before expansion.

7. `DURABLE_OUTPUT`
   - exact SHA, file, run, receipt, state record or runtime proof that must exist before the work is called complete;
   - local-only work is never completion.

8. `NEXT_ACTION_AFTER_RESULT`
   - define PASS / FAIL / BLOCK / NO_CHANGE_REQUIRED transitions before execution;
   - do not improvise a new architecture after a negative result.

A recommendation missing one of these fields is advice, not an executable mission.

## 3. Priority system — no false precision

Use four classes only.

### P0 — CURRENT CRITICAL PATH
Required to change the current top-level blocker or prove the next end-to-end property.

### P1 — REPEAT-PREVENTION
Prevents a failure mode already demonstrated to have caused lost work, false progress or restart.

### P2 — EFFICIENCY / QUALITY
Improves speed, observability or ergonomics but does not block the current critical path.

### PARK
Useful only after another event, permission or proof.

Do not use numerical scoring to manufacture certainty.

## 4. Seven hard anti-repeat laws

### Law 1 — Remote truth before action
Before substantive work after any interruption, fetch fresh durable state.

A local checkout, old chat, prior prompt, branch name or prior summary is not current authority.

If durable state proves the requested work is already done, answer `NO_CHANGE_REQUIRED`.

### Law 2 — Durable bytes/state before PASS
A build is not durable because it existed in a worker.

Before claiming PASS, the decisive material must be recoverable from a durable surface:
- remote commit;
- GitHub issue/PR exact-byte transport when remote commit is impossible;
- durable artifact/receipt;
- runtime state with identity.

`LOCAL_ONLY_PASS` is not PASS.

### Law 3 — Exact-subject qualification
Every qualification/review binds to an exact subject.

A review, CI run or test for SHA A cannot qualify SHA B.

When the subject moves, old evidence becomes historical unless equivalence is explicitly proven.

### Law 4 — One critical path, WIP <= 2
Keep:
- one primary lane that can change the top-level project state;
- at most one parallel evidence/data lane when it does not compete for the same authority or subject.

Do not create a third active lane merely because the first two are blocked.

If one lane is externally blocked, `PARK` it and continue only with an independent useful lane.

### Law 5 — Review must be decision-changing
A new review is justified only if at least one is true:
- new exact head;
- new evidence;
- new counterexample class;
- previously unavailable primary object becomes accessible;
- irreversible boundary is about to be crossed.

Otherwise: `NO_CHANGE_REQUIRED`.

Do not launch multiple reviewers who lack access to the exact object.

### Law 6 — Owner gates only for truly nondelegable boundaries
Routine engineering, reversible repair, bounded evidence collection and deterministic continuation should not return to Owner merely because they are important.

Owner authorization remains required for genuinely nondelegable boundaries such as:
- real-capital/live-trading authority;
- first irreversible scientific unblinding/exposure where the protocol requires Owner authority;
- changing frozen scientific semantics/protocol after freeze;
- irreversible external mutation outside an already authorized envelope;
- destructive repository action when not already explicitly authorized.

Everything else should prefer objective predicates and durable policy.

### Law 7 — Economic value outranks framework expansion
Do not build a new scheduler, control plane, Research OS, framework, board, registry or governance surface unless a currently admissible economic/scientific experiment or required E2E proof is demonstrably blocked by its absence.

A safe architecture with no decision-changing experiment is not progress toward the economic objective.

## 5. Failure-mode specific guards

### A. Lost local work
Trigger: useful code/tests exist only in an ephemeral workspace.
Guard: publish exact bytes/commit before further review or PASS.

### B. Stale prompt restart
Trigger: instruction refers to an older SHA/state than durable current state.
Guard: reconcile current state first; if already solved, `NO_CHANGE_REQUIRED`.

### C. CI over-claim
Trigger: green/red workflow summarized without job/step/subject inspection.
Guard: distinguish `NOT_EXECUTED`, `POLICY_GATE`, `PROJECTION_FAILURE`, `TEST_FAILURE`, `PASS`.

### D. Review over-claim
Trigger: reviewer lacks exact code/artifact/runtime evidence.
Guard: verdict is `BLOCK_EVIDENCE` or `UNKNOWN`, never semantic PASS/FAIL.

### E. Parallel rebuilds
Trigger: two workers can modify the same seam or build equivalent capability.
Guard: one subject + one builder; others challenge/read only until durable convergence.

### F. Architecture expansion during external block
Trigger: host/data/permission unavailable.
Guard: classify `BLOCK_EXTERNAL_*`; do not substitute new architecture.

### G. Duplicate science
Trigger: proposed experiment resembles a prior family/expression/window.
Guard: check scientific memory before freeze; classify `NEW_FAMILY`, `NEW_EXPRESSION`, `REPLICATION`, `CONTAMINATED`, or `DUPLICATE`.

### H. Multiplicity over-correction
Trigger: global counters make unrelated new mechanisms progressively impossible to validate.
Guard: preserve full disclosed history but apply multiplicity to the relevant family/selection process; underpowered is not automatically rejected.

### I. Endless negative exploration
Trigger: local admissible frontier is exhausted.
Guard: emit `NOOP_FRONTIER_EXHAUSTED`, `BLOCK_DATA`, or Owner-gated new-data request; do not invent another nearby variant.

### J. Governance/activity without value
Trigger: proposed artifact cannot change a decision, proof, recovery or authorization.
Guard: `DO_NOT_DO_IT` / `PARK`.

## 6. Standard recommendation format

Every future recommendation should fit this compact form:

```text
RECOMMENDATION_ID=
PRIORITY=P0|P1|P2|PARK
CURRENT_SUBJECT=
CURRENT_STATE=
CURRENT_BLOCKER_OR_DECISION=
PRIMARY_EVIDENCE=
EXISTING_CAPABILITY=REUSE|CONNECT|REPAIR|BUILD_REQUIRED|UNKNOWN
RECOMMENDED_ACTION=
WHY_THIS_CHANGES_A_DECISION=
MINIMAL_DECISIVE_TEST=
COUNTEREXAMPLE=
DURABLE_OUTPUT_REQUIRED=
PASS_NEXT_ACTION=
FAIL_NEXT_ACTION=
BLOCK_NEXT_ACTION=
OWNER_AUTHORIZATION_REQUIRED=TRUE|FALSE
STOP_CONDITION=
```

If this cannot be filled compactly, the recommendation is probably too broad and must be split.

## 7. Completion definition for a work unit

A work unit is complete only when all applicable levels are explicitly classified:

`BUILT`
`TESTED`
`QUALIFIED`
`INTEGRATED`
`PROMOTED`
`ACTIVE`
`USED`
`END_TO_END_PROVEN`

Do not infer later levels from earlier ones.

A green CI normally proves only the level its executed tests actually cover.

## 8. Checkpoint law

After each material decision-changing unit, persist one compact checkpoint containing:
- current exact subject;
- evidence produced;
- tests actually executed and their result;
- decisions changed;
- unresolved blockers;
- next single action.

Do not create checkpoint noise after purely mechanical reads or no-change operations.

The checkpoint exists to make a fresh agent resume without chat reconstruction.

## 9. Challenge before expansion

Before any build larger than a small repair, ask:

1. Is this already present elsewhere?
2. Can wiring close the seam?
3. Can a smaller repair close it?
4. What concrete evidence proves a new build is required?
5. What is the smallest counterexample that could falsify the design?
6. If this succeeds, which decision changes immediately?

If question 6 has no concrete answer, stop.

## 10. Recommendation effectiveness test

A recommendation system is working if, over subsequent work, the following trends appear:
- fewer local-only lost implementations;
- fewer stale-prompt restarts;
- fewer parallel implementations of the same seam;
- fewer reviews with no new evidence;
- fewer Owner interruptions on reversible work;
- higher ratio of decision-changing outputs to governance artifacts;
- more negative results preserved without retune;
- fewer claims that collapse when exact SHA/run/runtime is checked;
- faster movement from admissible hypothesis to bounded economic information;
- durable recovery after interruption without re-audit.

If these do not improve, challenge this method instead of adding more rules.

## 11. Current application

Current project router remains authoritative for execution.

At the time this method is introduced, the existing router states that engineering connection is qualified while actual VM multi-wake autonomy remains unproven and externally blocked by missing authenticated host access.

Therefore this method does NOT authorize a new scheduler, new autonomy architecture, economic experiment, deployment, live trading, capital, destructive cleanup or scientific unblinding.

It changes how future recommendations are admitted and executed, not current authority.

## 12. Final operating maxim

`BUILD LESS. PROVE THE NEXT DECISION. PERSIST BEFORE HANDOFF. REUSE BEFORE REBUILD. STOP WHEN MORE WORK CANNOT CHANGE THE CONCLUSION.`
