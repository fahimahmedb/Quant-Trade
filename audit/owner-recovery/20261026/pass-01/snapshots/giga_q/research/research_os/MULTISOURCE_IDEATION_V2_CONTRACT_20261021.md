# Multi-Source Ideation Intake V2 — isolated contract

## Immutable law

- Base: `2b99d8aeb8a342f1ef32544247d366cb8a26037e`.
- Branch: `builder/multi-source-ideation-intake-20261021`.
- This lane is pre-Discovery and stops at `ELIGIBLE_FOR_DISCOVERY`.
- `ELIGIBLE_FOR_DISCOVERY != READY`.
- Proposal Ledger is not a queue. IdeaProposal is not a Candidate or task.
- Existing Research Intelligence, Scientific Memory, source planner, replenisher and Control Plane remain authoritative.

## Same-cycle policies

All three policies consume one immutable `IdeationContextSnapshot` and must reach a terminal state before intake. The barrier waits for terminal status, not for three proposals.

A. `SYSTEMATIC_COVERAGE`: reuses the canonical frontier/source planner. A documentary source must be qualified and unused; content identity (`packet_hash`, then `blob_sha`, then `record_hash`) is used for claims. No admissible unused source returns `NO_ADMISSIBLE_NOVEL_SOURCE`; no synthetic mission is fabricated.

B. `INFORMATION_VALUE`: consumes an existing Research Intelligence decision. It does not rerank or recreate information-value truth. Non-executable/no-build/park/repair/validation decisions emit `NO_ACTION`; discovery-oriented executable decisions may emit only an `IDEATION_SEED` requiring downstream Discovery synthesis.

C. `DIVERGENT_EXPLORATION`: is bounded behind `ModelBackend`. The backend is not truth, scheduler, Control Plane or scientific evidence. A complete causal mechanism may emit one `IDEA_PROPOSAL`; incomplete output is a seed. Malformed output fails closed. Hidden semantic retry is forbidden and receipt-visible.

## GPT-OSS status law

`GPT_OSS_LIVE=TRUE` is forbidden unless this isolated build has evidence for backend identity, model identity, endpoint/runtime identity, a genuine request/response, provenance/response hash, and proof that no silent paid fallback occurred. Without that proof Policy C is `SOURCE_UNAVAILABLE`/`BLOCKED` with `EXTERNAL_RUNTIME_MISSING` and zero live GPT-OSS proposals. A deterministic fake backend is test infrastructure only.

## Terminal statuses

`PROPOSAL_EMITTED`, `SEED_EMITTED`, `NO_PROPOSAL`, `NO_ADMISSIBLE_NOVEL_SOURCE`, `FRONTIER_EXHAUSTED`, `BLOCKED`, `SOURCE_UNAVAILABLE`, `SOURCE_FAILED`, `INVALID_INPUT`, `NO_ACTION`.

## Durable records

The capability defines `IdeationContextSnapshot`, `IdeationCycle`, `RawProposalReceipt`, `RawIdeationArtifact`, `IDEATION_SEED`, `IDEA_PROPOSAL`, proposal identity/provenance, memory-lineage classification, ancestry/duplicate evidence, light implementability, passive source claims, proposal disposition and passive Proposal Ledger.

Claims are atomic but are deliberately not leases: no expiry, heartbeat, worker ownership or retry scheduling. Proposal persistence is immutable/idempotent and can be rehydrated from a durable snapshot without acquiring operational semantics.

## Scientific semantics

`BLOCKED != FAILED`. `UNEXECUTED != NEGATIVE`. `INVALID_PROTOCOL != NEGATIVE`. `UNKNOWN` is preserved. Wrapper/expression similarity is non-authoritative and cannot silently become exact duplication. Stale context requires requalification.

## Closed authorities

`REAL_CAPITAL_AUTHORIZED=FALSE`

`LIVE_TRADING_AUTHORIZED=FALSE`

`PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE`

`ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE`

`OUTCOME_ACCESSED=FALSE`

No READY task, Candidate, experiment, validator/red-team verdict, Economic Identity, portfolio object, Oracle task, producer execution, scheduler mutation, Control Plane mutation or live action may be created here.

## Qualification rule

The branch must not self-certify. Focused tests plus the repository exact-head CI/regression must pass on the final commit before `SAFE_TO_INTEGRATE=TRUE` or a final lane SHA is sealed. This isolated lane is never authorized to emit `WAVE2_INTEGRATED_SHA`.
