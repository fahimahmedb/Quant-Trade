# Work — continuous build workflow
Date: 2026-10-15
Repository: fahimahmedb/Quant-Trade
Build branch: builder/research-os-aggressive-architecture-20261015
Verified predecessor: 6130d6c4f97f76346760a5309ecc1efd32119eb6
Owner instruction: prepare a workflow and chain authorized build tasks without routine confirmation.

## Authority and scope
This is the Build Plane, not the research runtime. Follow AGENTS.md, the North Star and FINAL_SHAPE_CLOSURE_CHECKPOINT_20261015.md, with the Owner's current Research OS mission as scope.
NO_NEW_TOP_LEVEL_ARCHITECTURE = TRUE.
Keep HypothesisContract, ResearchTask, ExperimentResult, EvidenceAssessment, CandidateEconomicIdentity and WorkerEvent stable; WorkerReceipt remains their execution companion.
Do not change the production research branch, its five schedules, Live Lab deployment or unrelated Blue/Legacy work.
ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE.
PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE.
REAL_CAPITAL_AUTHORIZED = FALSE.
LIVE_TRADING_AUTHORIZED = FALSE.
No paid resources or credentials are authorized by this workflow.
Readiness is not permission. Architecture PASS is not economic validation.

## Resume protocol
1. Read fresh remote branch HEAD, applicable AGENTS.md, the closure checkpoint, this file and the latest lot receipt.
2. Verify the recorded implementation baseline exists in ancestry. Preserve newer commits; never reset the branch to the predecessor.
3. Inspect relevant code, existing tests and exact-head CI before editing. Reuse existing modules.
4. Find the first admissible nonterminal lot below. Reconcile any interrupted lot before starting another.
5. Never repeat completed research, reopen a closed economic look, fill historical UNKNOWN values, or infer activity from heartbeat.

## Execution loop
Select lot -> inspect existing implementation -> implement bounded depth -> run meaningful positive and negative checks -> commit/push -> verify remote HEAD and required CI on that implementation SHA -> persist receipt -> select next lot.
A green checkpoint is a recovery point, not a reason to ask the Owner to continue.
Do not append a new framework when the existing interface can carry the work.
When a patch changes evidence that a prior gate relied on, rerun that gate.
Use existing CI definitions where possible; never cancel an active useful run merely to refresh status.
If the connector cannot trigger a required gate, record CI_NOT_RUN and the missing action; never substitute an old green run.

## Ordered backlog
All lots below are PLANNED, not executed by this document.

| Lot | Existing subsystem | Concrete work and acceptance |
| --- | --- | --- |
| B01 | Fundamental + Event/Documents | Replace fixture-only dossier assumptions with admissible documentary inputs behind existing contracts. Bind each claim to source identity, clock, units/period, revision status and a disconfirming condition. Reject missing/conflicting evidence. No returns or future outcomes. Demonstrate that inputs change the candidate rather than merely its label. |
| B02 | Quant + Institutional Flows + Archaeology | Mechanism, payer/constraint, eligible instrument, horizon, falsification and legacy family screen. Preserve real implementability blockers. Reject historical duplicate before downstream execution. Do not tune to returns. |
| B03 | Experiment Infrastructure | Run deterministic outcome-free transformations from pinned admissible inputs through the existing runner, with code/input/protocol hashes. Prove replay equivalence, mismatch rejection and interrupted-run recovery. Distinguish an execution plan from an actually executed dry-run. |
| B04 | Independent Validator + Red Team | Validate actual B01–B03 artifacts. Demonstrate negative rights for timing, leakage, trials, source revision, cost/capacity gaps and producer/validator independence. Preserve frozen candidate hash. An insufficient dossier must BLOCK rather than acquire a higher claim by default. |
| B05 | Economic Identity + Portfolio | Compare multiple distinct candidates, identify common payer/mechanism/factor exposures and report missing estimates as UNKNOWN. Produce structural overlap with provenance. No return-series acquisition, fabricated correlation, sizing or capital allocation. |
| B06 | Forward Registry + Decay + Learning | Persist/reload immutable registrations; reject same-generation mutation, duplicate observations and all unauthorized observation ingestion. Test decay transitions with explicitly synthetic fixtures only. Record prospective-dependent functionality as BLOCKED_AUTHORITY rather than active. |
| B07 | Canonical integration + receipts | Feed strengthened artifacts through the existing canonical spine and Live Lab mapper. Prove early hard-stop, deterministic replay, immutable candidate and truthful blockers. Persist/reload state and show recovery without duplicate terminal receipts. No fabricated worker activity. |
| B08 | Release qualification | Consolidate evidence, known gaps, changed surfaces, exact candidate SHA and required green gates. Prepare reviewable release candidate and integration diff. Do not merge into or activate production merely because qualification passes. |

Dependencies: B01/B02 can advance independently; B03 follows admissible input work; B04 consumes B01–B03; B05 needs multiple dossiers; B06 can advance independently without observation authority; B07 integrates completed admissible lots; B08 qualifies the final candidate.
This dependency structure does not itself launch parallel agents.

## Lot receipt
Persist one small receipt under research/research_os/architecture/work_receipts/ after each meaningful lot:
- lot_id, status (IN_PROGRESS / COMPLETE / BLOCKED / DEFERRED)
- observed_head_before, implementation_sha, remote_head_verified
- scope, changed_files, artifacts
- validation commands and actual results
- CI workflow, run reference, head_sha, conclusion (or explicit NOT_RUN)
- evidence class (synthetic / documentary / executed dry-run)
- limitations, blocker, exact_reopen_condition, next_admissible_lot
- all four authority flags above, unchanged
A receipt commit must name the implementation SHA whose checks it reports. Do not claim those checks ran on the later receipt commit.
Do not create receipts that assert execution merely because this backlog exists.

## Failure and stop rules
- Routine test failure: diagnose and repair within scope; continue.
- Candidate failure: persist the negative and continue another admissible lot.
- Unavailable data/provider: record the first broken transition, avoid repeated identical probes, move to independent work.
- Branch moved concurrently: reread and reconcile, no force-push or overwriting other work.
- Credential/login, paid access, new architecture, production activation or missing scientific authority: isolate the blocked action; finish other authorized work, then present the concrete decision needed.
- All remaining work blocked or the finite backlog complete: persist a truthful final state and report it. Do not invent perpetual work.

## Runtime boundary
This file is a durable continuation protocol, not a scheduler, daemon or proof of an always-running Work session.
Within an active Work execution, continue admissible lots without routine Owner prompts. If the session ends or the platform interrupts it, resume from GitHub receipts on the next execution.
The existing five scheduled research workflows remain separate; this file does not repurpose or add a scheduled research worker.
