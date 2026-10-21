# WAVE 2 CONVERGENCE #2 — MULTI-SOURCE IDEATION INTAKE ACCEPTANCE PACK

Date: 2026-10-21
Owner role: Integration Foreman / pre-convergence accelerator
Status: PRE-CONVERGENCE CONTRACT — NOT A MULTI-SOURCE IMPLEMENTATION

## Immutable anchors

- `WAVE2_IMMUTABLE_BASE_SHA=2b99d8aeb8a342f1ef32544247d366cb8a26037e`
- observed Multi-Source branch: `builder/multi-source-ideation-intake-20261021`
- observed Multi-Source head at pack creation: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`
- qualified MEGA B source: `7ef088bb30ece88cf96f4514e8c581a95ca4b091`

The observed Multi-Source branch exists and is correctly rooted at the sealed Wave-2 base, but currently has no implementation delta. This pack does not implement that lane, does not move its ref, does not create a second replenisher, and does not emit `WAVE2_INTEGRATED_SHA`.

## Foreman finding: existing intake law is already source-aware

The sealed base already contains the primitives that must remain authoritative:

- `frontier_source_planner_v2.py` qualifies documentary packets, binds `source_ref`, `content_hash`, record hash and optional blob identity, prefers stronger evidence authority, and treats content identity rather than path as scientific consumption identity;
- `research_refill_policy.py` treats a frontier as a generation mandate, not as proof of candidate novelty, and emits only a pure `GENERATE_MECHANISM` preflight decision with `scheduler_mutation=false`;
- `queue_replenisher.py` is the bounded operational adapter that may derive at most one canonical ResearchTask `READY` only after its source/Research-Intelligence preflights; Multi-Source must not duplicate this authority;
- `research_intelligence.py` owns semantic identity, Scientific Memory screening and the later `RUN_PRODUCER` decision;
- MEGA B consumes only an already-qualified `RUN_PRODUCER`, `executable=true`, `scheduler_mutation=false` decision and then performs producer-level discovery.

Therefore the admissible chain is:

`qualified source/document observations`
→ `Multi-Source proposal/intake envelope`
→ `Research Intelligence generation/identity/memory screening`
→ `canonical operational admission when applicable`
→ `qualified RUN_PRODUCER decision`
→ `MEGA B`

Multi-Source is not a shortcut from documents to B and is not a second Control Plane.

## Source/document identity law

Every source used to justify an ideation proposal must retain enough immutable identity to distinguish provenance from location. At minimum:

- `source_ref`;
- documentary evidence class;
- qualified `content_hash` / packet identity;
- record/snapshot identity;
- captured blob identity when available;
- `published_at` / `available_at` / `effective_at` when applicable;
- retrieval/freeze time;
- revision/version/period metadata when applicable;
- issuer/actor/security identity where the family requires it;
- qualifier status and blockers.

A rename, copy or alternate repository path is not a novel source when the qualified content identity is the same.

A source whose `source_ref`, packet identity, clocks, revision state or factual payload changes materially must be treated as a new/requalified snapshot. It must not silently inherit qualification from the previous snapshot.

Missing or conflicting identity/clocks fail closed. UNKNOWN is preserved; it is not converted into novelty.

## Proposal identity law

Multi-Source may aggregate more than one qualified source into one ideation proposal, but the proposal identity must be stable and tamper-evident.

The proposal binding must include:

- proposal schema/version;
- normalized ideation/mechanism hypothesis material;
- sorted qualified source snapshot identities;
- source family / evidence-role metadata;
- provenance and clock binding;
- generation/ancestry when the proposal supersedes an earlier proposal;
- Scientific Memory screening reference/status once semantic identity is sufficiently resolved;
- authority/outcome membrane.

Proposal identity MUST NOT be derived from branch name, file path, prompt text or source count alone.

Material source-set or proposal-semantic mutation must produce a new binding/generation; it cannot reuse the old intake receipt.

## Multi-source composition law

Multiple sources do not automatically increase epistemic status.

The intake must preserve per-source roles such as primary authority, corroboration, explanation, amendment/revision, or conflict. It must not average incompatible sources into a synthetic fact.

If two qualified sources disagree materially on identity, clock, revision state, actor/security, causal claim or operative rule, the proposal remains blocked/UNKNOWN until the conflict is explicitly resolved. Source count is not a vote.

For duplicate content exposed at multiple URLs/paths, the intake must deduplicate by content/snapshot identity and preserve all provenance references without multiplying scientific support.

## Scientific Memory / negative-knowledge seam

Multi-Source must not create a second memory store. Once candidate semantic identity is sufficiently resolved, existing canonical Scientific Memory remains the screening authority.

Existing dispositions retain their meaning:

- `NEGATIVE` for the same qualified semantic family may close a redundant build path;
- `BLOCKED` is not NEGATIVE and may reopen only when the blocker is demonstrably resolved;
- `INVALIDATED_PROTOCOL` requires protocol repair/change, not a rerun under the same invalid protocol;
- `UNEXECUTED` is not failure;
- `POSITIVE_BUT_INSUFFICIENT` is not proof;
- unresolved identity is not novelty.

Multi-Source may reference memory evidence and screening receipts; it must not mutate canonical Scientific Memory as a side effect of intake.

## Research Intelligence seam

A Multi-Source proposal is not itself a `RUN_PRODUCER` authorization.

Before B can consume the idea, canonical Research Intelligence must resolve the relevant semantic identity and issue an executable action under its existing law. MEGA B must continue to reject anything that is not:

- `action=RUN_PRODUCER`;
- `executable=true`;
- `scheduler_mutation=false`;
- correctly bound to the origin candidate/proposal and selected producer capability.

The existing `GENERATE_MECHANISM` preflight is earlier than `RUN_PRODUCER`; these states must never be collapsed.

## Operational authority membrane

Scientific/ideation eligibility is not operational task admission.

Multi-Source MUST NOT directly:

- mint a ResearchTask `READY`;
- claim a lease;
- mutate queue state;
- mutate Control Plane capability state;
- run a producer in the same intake action;
- create recursive refill;
- grant economic experiment, prospective observation, real-capital or live-trading authority.

The existing bounded `queue_replenisher.py` remains the only observed adapter in this seam that may derive a canonical `READY` task, and only under its existing zero-active-queue / bounded-refill / source-policy / Research-Intelligence checks.

## Outcome firewall

Multi-Source is pre-outcome research intake. It must reject or quarantine outcome-bearing material used as justification for ideation when that would leak economic results into pre-registration/discovery.

The intake may record factual documentary observations available at their qualified clocks; it may not open, infer, optimize against, or backfill economic outcomes.

Required invariant:

`OUTCOME_ACCESSED=FALSE`

## Fail-closed acceptance cases

The normative foreman intent is encoded in `handoff/fixtures/WAVE2_MULTI_SOURCE_ACCEPTANCE_MATRIX.v1.json`.

At minimum a future Multi-Source exact head must prove:

1. a qualified documentary snapshot can enter intake with exact provenance/clocks;
2. source-ref mismatch rejects;
3. missing content identity rejects;
4. a path rename/copy does not create source novelty;
5. already-consumed content is not reissued as novel within the same frontier scope;
6. material source revision/snapshot mutation requires requalification/new binding;
7. duplicate multi-URL content is one scientific source identity with multiple provenance refs;
8. conflicting qualified sources remain blocked/UNKNOWN rather than majority-voted;
9. unresolved candidate identity is not novelty and does not bypass Scientific Memory;
10. known-negative / blocked / invalidated-protocol / unexecuted memory states remain distinct;
11. no proposal reaches B without canonical executable `RUN_PRODUCER` qualification;
12. no intake/scientific state directly becomes operational ResearchTask `READY` and no authority/outcome membrane opens.

## Qualification evidence required before canonical Convergence #2

Multi-Source is acceptable for canonical integration only after one exact sibling head demonstrates:

- ancestry from sealed `2b99d8aeb8a342f1ef32544247d366cb8a26037e`;
- deterministic intake proposal identity;
- qualified per-source identity/provenance/clock fixtures;
- duplicate-content/path-rename tests;
- stale/revision/requalification tests;
- conflict-preservation tests;
- Scientific Memory seam tests;
- Research Intelligence `GENERATE_MECHANISM -> ... -> RUN_PRODUCER` seam proof;
- MEGA B rejection of any bypass/unqualified decision;
- no scheduler/queue/Control Plane mutation from intake itself;
- authority flags all false;
- `OUTCOME_ACCESSED=FALSE`;
- exact-head workflow receipt naming the tested SHA.

Until that evidence exists:

`MULTI_SOURCE_IMPLEMENTATION_QUALIFIED=FALSE`

`READY_FOR_CANONICAL_CONVERGENCE2=FALSE`

`WAVE2_INTEGRATED_SHA=NOT_AUTHORIZED_TO_EMIT`
