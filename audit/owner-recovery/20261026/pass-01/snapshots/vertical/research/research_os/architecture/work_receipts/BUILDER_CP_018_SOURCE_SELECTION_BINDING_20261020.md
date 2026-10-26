# Builder CP018 — source selection → producer binding

STATUS=IMPLEMENTED_TARGETED_TESTS_PASS_BROADER_QUALIFICATION_PENDING
BASE=538cd48e2e5969621e1ba164dda4397b553f56b4
HEAD=commit containing this checkpoint
NORTH_STAR_SHA=a328b4e6d7d71dafd532938888ebf9818b1b610f (Git blob)
ORACLE_HEAD=21bec213b756d7ca0338849eba0e47e300d5b325 (fresh remote observation)

DONE: reused the existing derived-task validation in a lease-independent
validate_source_binding helper. Worker checks it before any source read, both
at selection and resumed lease verification. Source-aware refill tasks cannot
silently lose their derivation binding while retaining source inputs; differing
path, packet, record or declared Git blob bindings BLOCK with StateConflict.
Historical tasks with no explicit source selection retain prior behavior.
An optional absent Git blob remains valid for local catalogs with exact
packet+record binding. This is integrity, not cryptographic task authentication;
wholesale replacement of both task declarations is not covered by this check.

EVIDENCE: CP017's accepted inconsistent-source reproduction; 23 targeted
planner/worker tests PASS, including three new tests with adversarial subcases,
actual derive_refill_task output, both worker hooks and a no-read guard.
Pyflakes and diff whitespace checks PASS. Full/research/hosted qualification
will be recorded on the next stable code checkpoint. No active Oracle changes.

ARCHITECTURE UPDATE / NO_BUILD: suspicion that legacy screening silently runs
without its ledger was falsified at the runtime boundary. GitHubStateStore
fetches the exact manifest source_commit, materializes bytes and verifies the
pinned Git blob; run_worker_preflight.verify_materialized_legacy rejects absent,
empty, malformed or mismatched materialization. LegacyKnowledgeBase's standalone
empty instance is not proof that the runtime lacks memory. Global historical
reconciliation remains Integrator scope; direct V2 sidecar→search consumption
remains unproven. Preserve existing memory mechanism rather than rebuild it.

NEXT_BEST_WORK: early implementability accepts entry_clock=False as PASS because
_known treats every scalar other than None as specified. Reproduced with the
existing complete implementation fixture. Investigate/harden invalid declaration
values before expensive experiment preparation, without changing candidate or
authority. Source-aware task binding and early implementability are separate
connections; qualify both together after their bounded patches stabilize.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE
SAFE_TO_CONTINUE=TRUE
