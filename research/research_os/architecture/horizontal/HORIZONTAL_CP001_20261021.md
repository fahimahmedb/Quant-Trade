# Horizontal CP001 — current task-state surface omission

BASE_SHA=01c2e520fa4116645870f96acf6770ea83f1881c
HEAD_SHA=01c2e520fa4116645870f96acf6770ea83f1881c
BRANCH=codex/horizontal-completeness-prewave2-20261021
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

Module reviewed: control plane / task state / queue observability.

Expected: every legitimate current task state has an accounting disposition;
unsupported/unknown state cannot imply an admissibly empty queue. Basis: North
Star §§5 (task contracts, blockers, explainable scheduling), 12 (truthful durable
state), 15 (fail closed); canonical `contracts/research-task.schema.json` permits
READY, CLAIMED, BLOCKED, COMPLETE, FAILED, CANCELLED.

Found: `queue_summary` has active and terminal counts; the worker persists queue
summaries in stage receipts and idle wake documents. Terminal coverage includes
COMPLETE/BLOCKED/CANCELLED and historical KILLED, but omits FAILED. No unknown
input-state bucket or unknown-state refill disposition exists.

Current omissions H001/H002: FAILED is unaccounted for; an unsupported state is
silently treated as no active work by `derive_refill_task`. These are absent input
classes/dispositions inside one module, not a semantic field loss across modules
or an adversarial parser defect. Required current capability, horizontal owner.

Baseline reproduction (direct existing API, no model/network): singleton FAILED,
UNKNOWN and FUTURE_UNSUPPORTED queues each report task_count=1, active_count=0,
terminal_count=0. Each returns DERIVED_ONE_READY_TASK. FAILED should remain eligible
for legitimate followup, but must be counted. Unknown must have an explicit block.

Planned repair: include FAILED in existing terminal accounting, add unknown_count,
return BLOCKED_UNKNOWN_TASK_STATUS with no task from refill; use existing worker
wake persistence. No task state, scheduler, registry or cancellation command added.

Future Wave-2: task cancellation production and expanded runtime/recovery remain
E review questions. A CANCELLED schema spelling alone does not qualify a producer.
No cross-axis defect established by this checkpoint.

Tests: contract-state enumeration, unknown/missing-state refusal, FAILED followup,
and disposable real-Git worker durable wake/restart/correction test added before
repair. Baseline Research OS regression has 1 failure / 3 errors / 1 skip because
the documented ignored pinned Legacy ledger is not materialized; restore exact
blob ba9b165aaf96956776672df51233bb9bf1e6cbc9, do not change scientific history.
Baseline JS: 57/57 pass. Root regression still running at this checkpoint.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
SAFE_TO_CONTINUE=TRUE
