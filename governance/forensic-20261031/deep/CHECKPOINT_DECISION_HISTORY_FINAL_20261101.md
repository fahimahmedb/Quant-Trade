# Quant-Trade — final decision-history deep checkpoint

Date: 2026-11-01

Status: `HISTORY_RECONSTRUCTION_COMPLETE_FOR_DECISION_RELEVANT_SCOPE`

This checkpoint closes the historical reconstruction requested after the already-complete 6,393-commit chronological surface pass. It does **not** restart that chronology and it does **not** claim a semantic line-by-line reading of every blob ever produced.

## Closure law

The history is considered complete for project/convergence decisions when all of the following are true:

1. the full initial dated commit surface has been traversed;
2. the CP055→CP099 deep supplement is complete;
3. the decision-changing PR / issue / review threads have been read deeply enough to recover Owner decisions, builder claims, independent challenges, repairs, supersessions and terminal unknowns;
4. later evidence that contradicts an earlier PASS is preserved rather than normalized away;
5. remaining unknowns are bounded and cannot justify another global audit unless a specific future decision depends on them.

`BUILD != QUALIFIED != INTEGRATED != PROMOTED != ACTIVE != USED != PROVEN_END_TO_END` remains mandatory.

## Surface already closed before this pass

- commit traces in initial snapshot: `6393 / 6393`;
- active days surface-reviewed: `71` through `2026-10-31`;
- calendar days indexed: `111`;
- source occurrences indexed: `13471`;
- occurrences without exploitable date: `969`, deliberately retained as `UNKNOWN_BY_DATE` rather than assigned invented timestamps.

The 969 undated occurrences are **not** an authorization to restart the audit. They become relevant only if a concrete SHA/date contradiction could change a decision.

## Deep work already closed before this checkpoint

`deep/CHECKPOINT_CP055_CP099_20261031.md` closed the CP055→CP099 source-line reconstruction, exact-head qualification receipts and semantic lineage classes. This final pass continued from the open cursor in that checkpoint: decision-changing discussions, reviews, Owner directives and post-Wave2/autonomy descendants.

## Decision-history surfaces completed in this pass

Decision-changing material was reconciled across the following families rather than mechanically rereading all comments:

- July directional / anti-snooping lineage and later closure evidence;
- September whole-system, Evidence Store and SEC adversarial hardening surfaces;
- Weather V4 / Edge coordination and Owner authority changes;
- F1 Stage A / Stage B and source-admission failures;
- Multi-Source reacquisition and Wave2 sealing;
- WP1 evidence/admissibility blocker;
- bounded-autonomy operating model (#37);
- WP2 single-lineage proof and independent challenges (#38, PR39, #40, PR41, #42);
- autonomy liveness / authority-envelope decision (#43);
- GPT-OSS→Codex bridge construction, adversarial repairs, hosted qualification and runtime claim ceiling (#44, PR46);
- proposed Astra security/operability gate (#45);
- final selective convergence diagnostic PR47.

## Historical findings that materially define the project

### 1. September SEC history is adversarial hardening, not a sequence of interchangeable green branches

PR17 is the clearest example. Blue found false-PASS/provenance/visibility defects; Builder repaired them and exposed additional seams; a later Blue pass still rejected a CI-green candidate because the actual `main()` path shadowed the host boot identity with a child boot identity. The tests had bypassed that path. This is durable evidence for the project law:

`CI_GREEN != INVARIANT_PROVEN`

and for consequence-scoped independent challenge.

### 2. Weather A2 was deliberately frozen as a safety rail, not lost

The Owner eventually set:

- `PRIMARY_OBJECTIVE=FIND_OR_FALSIFY_REAL_EDGE`;
- `CURRENT_ACTIVE_FAMILY=F1_CRYPTO_CARRY`;
- `A2=SAFETY_RAIL_DEFERRED`;
- `REAL_CAPITAL_AUTHORIZED=FALSE`;
- `LIVE_TRADING_AUTHORIZED=FALSE`;
- `RESEARCH_ONLY=TRUE`.

Astra lot-3 had not established a candidate defect but withheld PASS for incomplete evidence/Owner-only observations. The project itself recognized that A2 mainly measured safe feasibility, not economic effectiveness. Historical conclusion: retain A2 patterns where useful, but do not interpret their disappearance from the active path as capability loss or economic validation.

### 3. F1 Crypto Carry has a single sealed negative outcome lineage

Before outcome access, a decision-relevant ranking defect was caught: median 30-day quote volume was being used instead of the preregistered trailing aggregate. It was corrected and re-frozen before the outcome.

Stage A was a single atomic look and was inconclusive/weak; Stage B was then executed once on the full declared sample and failed the confirmation criteria. The terminal family state is `REJECT`. No retune/rerun is admissible as a hidden continuation of the same family.

COIN-M was stopped for causal/source timing before economic outcome rows; that is a source-admission failure, not evidence that the economic family itself was tested and failed.

Later EURUSD grid work remained frozen pre-outcome: zero archives/rows/results/looks at freeze. No forgotten positive edge exists in this lineage.

### 4. Multi-Source/Wave2 must be reacquired by qualified identity, not branch narrative

Issue35 prevented sealing C2 from a stale Multi-Source receipt. Issue34 supplied the qualified isolated anchor `7d7c7af5…` with hosted run `39673124384` PASS. The durable rule is:

`REACQUIRE_FROM_EXACT_QUALIFIED_SHA`

not implicit promotion of an isolated lane.

### 5. WP1 is blocked by historical evidence admissibility, not by a failed economic result

GitHub-native recovery found a historical BitMEX Swagger receipt (HTTP 200, size and SHA recorded), but the exact historical payload bytes were not retained/recovered. A rights/source contradiction also remains. Therefore:

`WP1_CONTINUATION_RESULT=BLOCK_EVIDENCE_ABSENT_OR_UNRECOVERED`

No live probe, historical-trial rerun, successor execution or outcome inference is authorized from that record.

### 6. Bounded autonomy converged on delegation + thin liveness, not another Quant control plane

Issue37 and Issue43 converge on the same architecture law:

- the root problem is `PRODUCT_ORCHESTRATION_LIVENESS_GAP`, not missing domain reasoning architecture;
- `IMPORTANT_DECISION != OWNER_GATE`;
- consequential but reversible engineering decisions should operate inside a preauthorized authority envelope;
- policy-denied actions should normally trigger repair/reroute/park/independent work rather than Owner interruption;
- human intervention is reserved for genuinely non-delegable boundary crossings.

The four retained boundary classes are:

1. new/expanded real-capital or live-trading authority;
2. first irreversible scientific unblinding/prospective outcome access;
3. semantic redefinition of frozen protocol/denominator/endpoint/lineage;
4. irreversible/non-compensatable external mutation outside the signed envelope.

The target was never unrestricted `FULL_AUTONOMY`; it was single-launch continuity for bounded preauthorized work.

## Material correction discovered by the deep history: WP2 is CONTESTED, not cleanly closed

Earlier surface/capability summaries classified the WP2 synthetic single-lineage route as a bounded engineering proof, largely because PR39 contained an independent bounded PASS on implementation head `d40053bd112164826273a866199e2941259919b0` and later hosted run `41069767444` succeeded on `8f8df47d184f0f1594280bec7e9e7941962cf1c5`.

The deep discussion history requires a stricter final classification.

### Evidence supporting the earlier bounded-PASS narrative

PR39 history shows that early local self-PASS claims were correctly rejected when not durably published. Exact bytes were frozen and transported. A real receipt-alias defect was then found independently and narrowly repaired. A review receipt `5709575146` later recorded `INDEPENDENT WP2 REVIEW — BOUNDED PASS` on `d40053…`. A later exact-head hosted run on `8f8df47…` was successful; the known Git delta from `d40053…` to `8f8df47…` was only `STATE.md`, so the implementation code was not changed by that final projection.

### Later independent counterevidence that was not closed

PR41 was explicitly created to review parent implementation `d40053…` from an exact descendant checkout. Its GitHub code review completed with `has_any_findings=true` and `has_unresolved_findings=true` and produced two concrete findings:

1. **P1 — execution/evaluation arrow not actually demonstrated.** The reviewer observed that `SyntheticWP2Binding.execute()` called `runner.plan()` and `verify_bindings()` but not `DryRunExperimentRunner.execute()`. Replacing `runner.execute` with an always-raising mock still yielded `COMPLETE` with zero execute calls. The review therefore challenged whether the receipt proves `runner -> executed result -> evaluator`, rather than only plan/rebinding consistency.

2. **P2 — fixture identity not durably pinned before claim/recovery.** After a crash post-claim, a replacement binding with different constructor inputs could complete generation 2 under a different fixture identity. The review also reported that changing a qualification snapshot input before execution could succeed while publishing the cached prior digest. The requested correction was to persist/recompute the frozen fixture identity from actually consumed inputs and reject drift on initial execution and recovery.

No subsequent implementation repair or explicit refutation of these PR41 findings was found on that review surface.

Issue42 later verified the hosted run identity and artifact metadata for `8f8df47…`, but its fresh-context semantic review remained `UNKNOWN` for causal single-lineage semantics, runner/evaluator binding, receipt integrity, sink isolation, authority membrane and unresolved critical/high findings because it still lacked primary semantic inspection.

### Correct final historical classification

`WP2_SYNTHETIC_SINGLE_LINEAGE = CONTESTED_ENGINEERING_EVIDENCE`

`PR39_INDEPENDENT_BOUNDED_PASS = EXISTS`

`PR41_LATER_P1_P2_FINDINGS = UNRESOLVED`

`ISSUE42_FRESH_CONTEXT_SEMANTIC_VERDICT = UNKNOWN`

`HOSTED_RUN_41069767444 = SUCCESS`

`WP2_GLOBAL_AUTONOMY_PROOF = FALSE`

Decision: preserve WP2 as useful synthetic evidence, but **do not use it as a clean independent closure proof** until the PR41 findings are explicitly repaired or falsified on exact code. This correction supersedes only the older simplified WP2 row in `CAPABILITY_MAP.md`; it does not invalidate unrelated Wave2/PR46/canonical qualification evidence.

## PR46 / Issue44 final historical classification

PR46 is a different lineage from WP2 and did undergo repeated adversarial repair on its own code:

- earlier heads exposed authority-envelope leakage, same-principal/self-review causality weakness, GitHub-actor preflight ordering, marker laundering, subject-state identity drift, and stale target-head acceptance;
- those findings drove bounded repairs rather than a new scheduler/control plane;
- a later nominal response-contract defect on `f100138…` was independently reproduced and narrowly repaired;
- final same-lineage repair `afedfd57986aa042e9e97aa53b9db53b4619764f` received hosted push run `41203216122 = SUCCESS` with exact-head verification, 387 unit tests, 267 SEC-lane tests, 35/35 V1 E2E checks, clean tree and preserved closed authorities.

Historical claim ceiling:

`PR46_BRIDGE=BUILT_AND_HOSTED_QUALIFIED`

`PR46_DEPLOYED=FALSE/NOT_PROVEN`

`REAL_GPT_OSS_CODEX_GPT_OSS_LOOP=NOT_PROVEN`

`WHOLE_QUANT_PRODUCT_COMPLETE_FROM_BRIDGE=FALSE`

The bridge is task-bounded. It does not by itself read the North Star/current router, select the globally next unmet project predicate, or create a new mission after terminal DONE/PARK.

## Issue45 classification

Issue45 requested an Astra security/operability gate but was closed `not_planned` with zero comments. Therefore:

`ASTRA_GATE_REQUEST=EXISTS`

`ASTRA_GATE_EXECUTED=FALSE`

`ASTRA_REVIEW_RESULT=ABSENT`

Do not cite Issue45 as a completed independent security review.

## PR47 classification

PR47 was a convergence diagnostic only. It tested direct CP099→Wave2 convergence and found the PR non-mergeable. It closed unmerged, with no comments. This supports the final convergence decision to use selective exact-blob/semantic ports instead of a wholesale merge. It is not a missing integration branch.

## Remaining historical unknowns and blocks after closure

These are intentionally bounded:

- `969` undated occurrences remain `UNKNOWN_BY_DATE`; inspect only if a future exact-SHA/date question makes one material;
- WP1 historical payload/admissibility remains `BLOCK_EVIDENCE_ABSENT_OR_UNRECOVERED`;
- WP2 synthetic semantics remain `CONTESTED` because of later unresolved PR41 P1/P2 findings;
- actual VM deployment/current health/multi-wake behavior is a runtime evidence problem, not unfinished history;
- scientific/economic validity cannot be inferred from engineering qualification.

None of these authorizes another repository-wide chronological audit.

## Final closure

`SURFACE_HISTORY_COMPLETE=TRUE`

`CP055_CP099_DEEP_SUPPLEMENT_COMPLETE=TRUE`

`DECISION_CHANGING_DISCUSSION_HISTORY_COMPLETE=TRUE`

`HISTORY_RECONSTRUCTION_COMPLETE_FOR_DECISION_RELEVANT_SCOPE=TRUE`

`FULL_SEMANTIC_READ_OF_EVERY_BLOB=FALSE`

`GLOBAL_FORENSIC_RESTART_AUTHORIZED=FALSE`

`DESTRUCTIVE_CLEANUP_AUTHORIZED=FALSE`

Historical work should now be resumed only for a **specific falsifiable contradiction** whose resolution can change a current decision. Otherwise use this checkpoint plus the existing surface/deep checkpoints as durable memory and follow `project/canonical` for the active project state.
