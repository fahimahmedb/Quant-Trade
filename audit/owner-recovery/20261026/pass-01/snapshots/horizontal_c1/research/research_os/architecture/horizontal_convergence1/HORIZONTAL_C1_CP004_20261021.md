# Horizontal C1 CP004 — full auxiliary schema qualification

BASE_SHA=97165db2faa3300cef1f23de0045ed93d25eb9cb
HEAD_SHA=d88107fb2d872d203ca6f361df1adbb5fb8d24e4
REVIEW_START_SHA=bb854852283b13afe7821e3183ab5ba912e09c7f
BRANCH=codex/horizontal-completeness-convergence1-20261021
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

Modules reviewed: Early Implementability and Experiment Infrastructure auxiliary
contracts; structural identity/shared-wire binding scope; regression over the
existing 43-module inventory. No new base, merge, rebase or future Wave-2 import.

Expected surface: current legitimate assessment/envelope output classes and their
durable fields must be admitted by their declared auxiliary schemas. Known, blocked,
parked, unknown and nonfrozen states must remain representable without opening
authority. A required-key subset check is not full schema validation.

Found: actual ImplementabilityAssessment PASS/PARK/BLOCK/unknown records and actual
ExperimentEnvelope frozen-object/nonfrozen-null records were rejected by the closed
schema. Implementability lacked BLOCK_IMPLEMENTABILITY, UNKNOWN for four feasibility
families, exact-expression/detail/authority fields; envelope lacked protocol_payload.
The runtime already produced and consumed these states/fields. These are absent
contract surfaces, not new research features or deep parser robustness defects.

Repairs H003/H004: extend the two existing auxiliary definitions; retain the same
four named auxiliary records, additionalProperties=false, false authority/mutation
claims and readable legacy minimal records. No common contract was redefined and
no runtime output or decision changed. A full-schema test consumer and explicit
existing CI step now bind current producers to those durable definitions.

Tests use pinned development-only jsonschema 4.26.0 Draft202012Validator against
actual producers and real JSON round trips, not schema-shaped replicas or a custom
partial validator. Six methods cover PASS/PARK/BLOCK, all unknown feasibility fields,
both envelope body classes, all registered auxiliary families, legacy readability
and negative authority/mutation/undeclared-field controls. Before repair: 6 methods
ran, 21 failing subcases. After repair: focused 34 PASS.

Full current source qualification:

| Check | Result |
| --- | --- |
| Root regression | 799 passed |
| Research OS regression | 433 passed |
| Explicit MEGA A bridge | 94 passed, including 24 function tests |
| Live Lab JavaScript | 57 passed |
| Schema generator | No drift |
| Status reconstruction | CHIEF_BRIEF.md and STATE.md fresh; unchanged |
| Declared test dependency | jsonschema 4.26.0 present; offline requirements check passed |
| Changed Python compilation / Git whitespace | Passed |

The active CP004 matrix has 43 rows and 95 overlapping family entries: 59 qualified
narrow source behaviors, 4 partial, 21 future, 10 intentionally deferred and 1
documentary-only binding question. All 577 method + 24 function selectors resolve
and belong to fully passing suites. Every listed source byte matches HEAD_SHA.
Logs, source/matrix hashes, dependency version and commands are archived in the
CP004 validation JSON and evidence/cp004/. Counts overlap and are not additive.

The prior V1 disposable replay passed 35/35 at 1342d6a; its implementation/data were
unchanged and it was not redundantly rerun at CP004. Current root regression and
status reconstruction cover their existing checks. Earlier CP002 matrix/validation
remain historical evidence; current consumers should use the CP004 revision.

U002: the registered stable shared CandidateEconomicIdentity wire schema and the
current native identity/structural output are distinct shapes. A qualified current
wire adapter/consumer is not established. The matrix marks this binding documentary-
only with UNKNOWN_OWNERSHIP rather than treating a filename as conformity proof.
No concrete current requirement justifies inventing that adapter on this rail.
Final cross-lane convergence must resolve the intended interface explicitly.

Missing current horizontal surfaces: H001/H002 remain repaired; H003/H004 now closed.
Future B/C0/D0/E, Multi-Source and final bindings remain future, not current defects.
Cross-axis: L001 was re-probed and remains open, owner LONGITUDINAL. No handoff fix
was absorbed; no new Vertical finding established. Empirical outcomes, economic
truth, real observations and deployment were not created to qualify these surfaces.

SECOND_CONTROL_PLANE_CREATED=FALSE
SECOND_SCHEDULER_CREATED=FALSE
SECOND_MEMORY_CREATED=FALSE
ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
SAFE_TO_CONTINUE=TRUE
SAFE_AS_DIAGNOSTIC_INPUT_TO_WAVE2=TRUE
FINAL_WAVE2_PHASE_B_STARTED=FALSE
PHASE_B_REQUIRED=TRUE

Next legitimate event: resolve L001 and U002 on their appropriate integration/
interface ownership; later repeat Phase B from the Owner's qualified final Wave-2
SHA on a new branch. Do not automatically merge, rebase or cherry-pick this branch.
