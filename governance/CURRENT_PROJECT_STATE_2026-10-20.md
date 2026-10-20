# CURRENT PROJECT STATE — 2026-10-20

Status: **CURRENT ROUTING AUTHORITY** for repository orientation and branch hygiene.

This document supersedes the September 2026 Blue routing documents **for current project navigation only**. Historical governance, scientific evidence, frozen decisions and negative results remain immutable evidence and must not be rewritten.

## 1. North Star

`QUANT_NORTH_STAR.md` remains the highest-level product specification.

Quant is a persistent quantitative research system whose long-term objective is genuine net economic value after realistic frictions. A runtime, research lane, Oracle worker, strategy, dashboard or branch is only a subsystem or evidence surface.

## 2. Current repository reality

The GitHub default branch is still:

`blue/master-v2-2026-09-20`

It is retained as a **routing / historical portal** during cleanup. Its code snapshot is not the current runtime authority and must not be used to infer the latest implementation state.

### Live V1 runtime line

Canonical live implementation branch:

`builder/oracle-economic-loop-recovery-20261019`

Last independently observed HEAD on 2026-10-20:

`291540c5d69f0f2b0638dab10ba61862e6715cc4`

The branch is autonomous and may advance after this document. Resolve its live HEAD before making implementation claims.

Qualified Oracle release evidence remains anchored to the V1 qualification lineage documented in the branch, including release `f3943830e20b05d926d3013501573b8b21fdace7` and the reboot / natural-wake proof chain.

V1 proves operational scheduling, persistence, claim/lease recovery and fail-closed authority behavior. It does **not** prove economic edge or authorize capital.

### Current independent audit line

`audit/forensic-checkpoint-20261019`

Current audit checkpoint:

`090076945ff4d3e8006757047bbc6d2716d2eea6`

Primary reconciliation document:

`CHECKPOINT_010.md`

CP10 updates CP7–CP9 against the qualified Oracle V1 implementation. It is the current forensic baseline for V2 cleanup/design work.

## 3. Permanent authority boundary

Unless a later explicit Owner decision changes these values, all remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- capital allocation / position sizing / real order authority = FALSE

Operational qualification, validator PASS, local-model output, frozen hypotheses or branch cleanup never grant these authorities.

## 4. V2 status

`V2_CANONICAL_TRUNK = NOT_YET_DECLARED`

V2 is being prepared in parallel with the live Oracle V1 line. Do **not** create another competing top-level architecture or silently rename an old branch as V2 authority.

Current V2 source/evidence branches that must survive branch cleanup until their unique content is explicitly reconciled include at least:

- `builder/research-os-aggressive-architecture-20261015`
- `builder/research-factory-core-v2`
- `research/edge-lab-continuous`
- `research/legacy-economic-reconciliation-20261015`
- `research/design-v1`
- `codex/test` — historical negative economic result / scientific memory
- `audit/forensic-checkpoint-20261019`
- `builder/oracle-economic-loop-recovery-20261019` — live V1 runtime

Weather V4, Gate A/B, Forward/Economic, Astra and other historical workstreams may contain unique evidence. Their branch refs are cleanup candidates only after ancestry/duplicate proof or after their tips are archived.

## 5. Branch hygiene policy

The repository currently contains far too many branches. The cleanup objective is **minimum active branch namespace without loss of reconstructable scientific or governance history**.

Classification:

- `KEEP_LIVE` — active runtime / current routing / current audit.
- `V2_SOURCE` — unique implementation/design material still useful for V2.
- `SCIENTIFIC_MEMORY` — positive or negative result that must remain reconstructable.
- `GOVERNANCE_EVIDENCE` — audit / Owner / Blue / Astra evidence whose exact tip still matters.
- `ABSORBED` — strict ancestor of a retained branch; branch ref can be deleted.
- `REDUNDANT_REF` — exact duplicate tip already retained elsewhere; branch ref can be deleted.
- `ARCHIVE_THEN_DELETE` — unique historical/diverged tip that is no longer an active branch but must remain reachable via an archive tag before branch deletion.
- `REVIEW_REQUIRED` — unresolved value; do not delete until classified.

Rules:

1. old or negative does not mean deletable;
2. strict ancestor of retained authority is normally branch-delete safe;
3. exact duplicate tip is branch-delete safe when one reachable ref remains;
4. diverged unique branches are archived before branch deletion unless explicitly retained as V2 source;
5. historical scientific results are never rewritten to make cleanup easier;
6. do not mutate the live Oracle V1 branch as part of repository hygiene;
7. do not use branch cleanup to authorize economic experiments or real capital.

Operational cleanup procedure is documented in:

`governance/REPOSITORY_HYGIENE_V2_2026-10-20.md`

## 6. Current known reconciliation facts

Verified against the live repository during the 2026-10-20 audit:

- branch count observed: approximately 227 before the new cleanup pass;
- old Blue cleanup had previously reduced the repository to 40 branches, so branch sprawl re-accumulated materially;
- `builder/research-os-autonomous-loop-20261015` is a strict ancestor of the modern Oracle line;
- `builder/research-os-autonomous-econ-readiness-port-20261016` is a strict ancestor of the modern Oracle line;
- `builder/research-os-econ-readiness-activation-20261017` is a strict ancestor of the modern Oracle line;
- `builder/econ-test-flow-ust-auction-20261019` is a strict ancestor of the modern Oracle line;
- `builder/research-os-aggressive-architecture-20261015` remains diverged with unique history and is a V2 source, not deletion noise;
- `builder/research-factory-core-v2` remains diverged with unique product/research-factory history;
- `research/edge-lab-continuous` remains diverged with substantial unique research history;
- `research/legacy-economic-reconciliation-20261015` remains diverged with unique Legacy reconciliation history;
- `ops/oci-one-shot-install-20261019` and `builder/research-os-vm-autonomy-20261019` are historical side rails whose useful content must be either already ported or archived before their branch refs disappear.

## 7. Scientific state carried into V2

CP10 establishes the following current interpretation:

- real Legacy bootstrap is fail-closed in V1;
- current hypothesis corpus normalization exists;
- ASML-like current-lineage overlap is detected;
- new-candidate anti-redetection exists;
- unresolved portfolio overlap can block economic readiness;
- canonical worker challenge/readiness paths receive current-lineage context;
- pre-existing unresolved corpus overlap does not globally halt every Oracle wake;
- that global-overlap policy remains a V2 governance/design question;
- Legacy reconciliation remains `PARTIAL_WITH_EXPLICIT_GAPS`;
- structural similarity must never be converted into empirical correlation without admissible return history;
- marginal portfolio contribution remains `NOT_ESTIMATED` without admissible evidence.

## 8. Mandatory read order for new agents

Before substantial work:

1. `QUANT_NORTH_STAR.md`
2. `governance/CURRENT_PROJECT_STATE_2026-10-20.md`
3. resolve the exact current branch + live HEAD
4. if working on scientific architecture / V2: `audit/forensic-checkpoint-20261019` -> `CHECKPOINT_010.md`
5. if working on Oracle V1: read the current Oracle branch runtime handoff/scope and exact latest state
6. read only the branch-specific architecture, tests and evidence needed for the assigned mission

Do not use September Blue handoffs as current routing authority. They are historical evidence.

## 9. Current project objective

Near-term repository objective:

`CLEAN_REPOSITORY -> PRESERVE_EVIDENCE -> DECLARE_SMALL_V2_TRUNK -> CONTINUE_V2_FROM_RECONCILED_SOURCES`

The intended end state is a small number of understandable active branches, durable archived evidence, one explicit live V1 line, and one future V2 trunk whose ancestry and imported capabilities are documented rather than inferred.