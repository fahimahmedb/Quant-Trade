# Quant-Trade — Deep Reconstruction Plan

STATUS=AUTHORIZED_METHOD
MODE=DEEP_SELECTIVE_RECONSTRUCTION
GLOBAL_FORENSIC_RESTART=FALSE
BRANCH_DELETION_AUTHORIZED=FALSE
WEEKLY_CHECKPOINT_REQUIRED=TRUE
WEEKLY_HANDOFF_REQUIRED=TRUE
WEEK_BOUNDARY=MONDAY_TO_SUNDAY_EUROPE_PARIS

## Objective

Use the completed surface chronology as an index, then perform a deeper reconstruction only where it can change the canonical project decision.

The purpose is to recover hidden value and hidden gaps, not to repeat the 6,393-commit chronology.

## Governing rule

For every capability or historical cluster:

1. identify the strongest primary evidence available;
2. distinguish BUILT / QUALIFIED / INTEGRATED / PROMOTED / ACTIVE / USED / END_TO_END_PROVEN;
3. compare the historical capability with `code/canonical` and `project/canonical`;
4. identify whether the surface audit missed a stronger implementation, a later correction, a contradiction, a missing integration seam, or a supersession;
5. classify the result as one of:
   - NO_CHANGE_REQUIRED
   - CONNECT
   - PORT_SELECTIVELY
   - REPAIR
   - GOVERNANCE_ONLY
   - PARK
   - RETIRE_FROM_ACTIVE_SCOPE
   - BLOCK
   - UNKNOWN
6. never restore a whole historical branch merely because it contains useful evidence;
7. port only a proven missing semantic or invariant;
8. preserve negative scientific memory and superseded conclusions so they cannot be rediscovered as new work.

## Deep evidence standard

Prefer, in order:

- exact commit SHA and ancestry;
- exact file/blob content;
- executed workflow run and job logs;
- issue/PR review evidence and unresolved findings;
- runtime receipts and host state;
- branch names / commit messages only as navigation aids, never as proof by themselves.

Construction != qualification != integration != promotion != activation != use != end-to-end proof.

## Reconstruction units

The pass should be capability-centered, not commit-centered. At minimum inspect:

1. scientific memory / experiment identity / negative results;
2. research factory / experiment execution / anti-snooping;
3. PIT data identity / evidence store / source pinning;
4. portfolio / book / risk / economic readiness;
5. Weather and other transport / scientific bridge layers;
6. Research OS / autonomous loop / liveness / fencing;
7. GPT-OSS -> Codex -> GPT-OSS orchestration and VM runtime;
8. Wave / Mega / Multi-Source / GIGA hardenings;
9. authority / Owner gates / Blue / Astra / trusted-root semantics;
10. deployment / scheduler / recovery / continuity;
11. economic experiment rails and rejected hypotheses;
12. support infrastructure that may be useful but should not remain active architecture.

## Weekly checkpoint and handoff law

Historical work is grouped by calendar week, Monday through Sunday in `Europe/Paris`.

After EVERY historical week inspected, push BOTH:

1. `governance/deep-reconstruction/DEEP_WEEK_<YYYY-MM-DD>_<YYYY-MM-DD>.md`
2. `governance/deep-reconstruction/HANDOFF_WEEK_<YYYY-MM-DD>_<YYYY-MM-DD>.md`

The weekly deep checkpoint must contain:

- exact week bounds and active days actually present;
- source surface checkpoints reused;
- exact commits / PRs / issues / blobs / workflow runs inspected where decision-relevant;
- capability identities reconstructed;
- BUILT / QUALIFIED / INTEGRATED / PROMOTED / ACTIVE / USED / END_TO_END_PROVEN distinctions;
- recovered value;
- negative / superseded scientific memory;
- contradictions and later corrections;
- comparison against `code/canonical` and `project/canonical`;
- classification for each material object;
- canonical gap candidates discovered;
- whether any port / repair is justified;
- unresolved UNKNOWNs and why they do or do not block;
- exact next week.

The weekly handoff must be deliberately shorter and sufficient for another AI to resume without rereading the full week. It must contain:

- authoritative branch heads observed;
- completed historical week;
- decisions that MUST NOT be reopened absent contradictory primary evidence;
- open gaps / blockers;
- exact next week and first evidence objects to inspect;
- any pending mutation or qualification run;
- explicit statement that global forensic restart is forbidden.

Publishing a weekly checkpoint never pauses the mission.

## Efficiency without quality loss

Allowed optimizations:

- reuse existing surface chronology, capability maps, crosswalks and exact-SHA checkpoints as navigation indices;
- batch related commit / file / run lookups when the evidence question is shared;
- compare ancestry or file diffs before opening full branches;
- use one representative primary proof when multiple later artifacts are byte-for-byte or semantically equivalent;
- stop descending into an object once a stronger later proof demonstrably supersedes it and no hidden value can change the canonical decision;
- mark `NO_CHANGE_REQUIRED`, `PARK`, `RETIRE_FROM_ACTIVE_SCOPE` or bounded `UNKNOWN` rather than auditing low-value detail indefinitely.

Forbidden shortcuts:

- treating summaries, branch names, commit messages or CI green as sufficient proof;
- inferring integration from construction, promotion from qualification, activation from deployment intent, or end-to-end use from unit tests;
- skipping a known contradiction because a later summary looks cleaner;
- restoring a historical system wholesale instead of isolating the missing semantic;
- reducing evidence depth merely to finish faster.

Optimization is valid only when it preserves or increases confidence in the canonical decision.

## Final outputs

The pass is complete only when these are reconciled against the canonical branches:

- `DEEP_VALUE_RECOVERY_LEDGER.md`
- `DEEP_CANONICAL_GAP_LIST.md`
- `PROJECT_CLOSURE_GATE.md`
- `ECONOMIC_FOCUS_BACKLOG.md`
- one canonical HANDOFF / resume surface

## Stop condition

Stop deep reconstruction when additional historical inspection can no longer change:

- the canonical code content;
- the canonical governance state;
- the project closure gate;
- or the economic backlog.

Unresolved low-value details may remain UNKNOWN without reopening global archaeology.

## Current known boundary

The currently demonstrated engineering candidate remains separate from actual VM multi-wake proof. Host/runtime evidence must not be inferred from hosted CI.

NEXT_ACTION=DEEP_CAPABILITY_RECONSTRUCTION
