# Horizontal findings — supplied Convergence #1 snapshot

BASE_SHA=97165db2faa3300cef1f23de0045ed93d25eb9cb
REPAIR_SOURCE_SHA=1342d6a0f11c0287f20049de7958d3922af68d5e
AUXILIARY_CONTRACT_REPAIR_SHA=d88107fb2d872d203ca6f361df1adbb5fb8d24e4
LATEST_REVIEW=CP004
NORTH_STAR_BLOB=a328b4e6d7d71dafd532938888ebf9818b1b610f

This is the intermediate review requested by the Owner after supplying this SHA.
Its own handoff identifies CP079-first Convergence #1. It is not the final
qualified integrated B/C0/D0/E + Multi-Source + convergence #2 architecture.

## Current horizontal repairs

H001 — CURRENT_REQUIRED_CAPABILITY / HORIZONTAL / REPAIRED.
The canonical ResearchTask enum admits FAILED, but `queue_summary` omitted it.
At the supplied SHA, a FAILED singleton had task_count=1, active_count=0 and
terminal_count=0. It is now counted as terminal while still permitting legitimate
followup. Historical KILLED remains supported. The test enumerates every actual
canonical task state; it does not infer the contract from the implementation.

H002 — CURRENT_REQUIRED_CAPABILITY / HORIZONTAL / REPAIRED.
At the supplied SHA, UNKNOWN, unsupported future spelling and missing status had
no accounting bucket or fail-closed refill disposition. This remained true with
the newly integrated MEGA A policy context: unknown queue state could derive work.
The existing queue summary now exposes `unknown_count`, and the existing refill
function returns `BLOCKED_UNKNOWN_TASK_STATUS` with no task before either legacy
or MEGA A derivation. Inactive frontier behavior remains its existing no-op.

Fresh tests cover missing/unknown/future states, with and without policy and source
catalog; FAILED followup retains policy hash/receipt, no novelty claim and closed
authority. A real disposable Git V2 worker persists the block, preserves it on
restart, and resumes legitimate followup after recognized-state correction. Known
active task selection is unchanged; this is a guard on attempted refill.

Both defects were re-proved against the new architecture before repair. No Phase-A
commit was merged or cherry-picked; current MEGA A paths and policy receipts were
re-evaluated. No new task state, scheduler, memory, store, cancellation producer or
control plane was created.

T001 — CURRENT_REQUIRED_CAPABILITY / HORIZONTAL QUALIFICATION / REPAIRED.
The untouched supplied base passed 799 root tests but failed 3 of 423 Research OS
tests. Their fixtures/assertions predated W1's stronger legitimate relationship
classes. Production `structural_pair` correctly reviews a known common exposure
even if payer/mechanism labels differ; unknown core data does not erase a known
common exposure; equal payer/mechanism with unknown clock is explicit related
review. Two fixtures now isolate genuine distinguishable/unknown states by removing
the conflicting shared-exposure premise. The integration assertion now checks
W1's explicit related-review pair and basis. The W1 tests still assert all those
stronger review cases. No production Portfolio logic changed or weakened.

## Confirmed cross-axis finding

```text
CROSS_AXIS_FINDING
id=L001
owner=LONGITUDINAL
classification=CURRENT_REQUIRED_CAPABILITY
from_module=EXPERIMENT_INFRASTRUCTURE_FROZEN_PROTOCOL
to_module=ECONOMIC_IDENTITY_PORTFOLIO
property=preserve_declared_instrument_universe_clock_horizon_with_provenance
status=OPEN_NOT_REPAIRED_ON_HORIZONTAL_RAIL
```

Evidence: the existing metadata-only readiness fixture returns
READY_FOR_AUTHORIZED_ECONOMIC_TEST; its current Factory-bound frozen expression
contains instrument SYNTHETIC_TEST_INSTRUMENT, universe
SYNTHETIC_ELIGIBLE_UNIVERSE, horizon "one declared clock interval" and explicit
entry/exit and decision/freeze clocks. Returned structural identity has UNKNOWN
instrument/universe/timing_clock and horizon "one interval" from the candidate.
The downstream structural contract independently represents all four dimensions.

The current composer calls `economic_identity_v1(output, identity_meta)` without
binding its frozen expression. Thus both endpoints exist; the loss is the handoff,
not an absent output type. Repair belongs to Longitudinal. Earlier CP084 diagnostic
history was not treated as proof or blindly imported. The loss was independently
reproduced at the supplied convergence SHA and remains present after the narrow
queue/test repairs.

Source locator: `research/research_os/expansion/economic_test_readiness_v1.py:213`
is the composer call; `research/research_os/expansion/final_shape.py` defines
`economic_identity_v1`; `research/research_os/expansion/portfolio_v2.py` defines
the independent `structural_identity` consumer representation. The probe returns
both the actual composed identity and the direct consumer representation.

Reproduce:

```sh
python research/research_os/architecture/horizontal_convergence1/probe_frozen_identity.py
```

The adjacent archived probe JSON records actual values, direct consumer
representation and four closed authority values. The probe uses existing synthetic
metadata only; it is diagnostic, not a qualification test granting readiness or
creating economic truth. Passing test totals do not close L001.

VERTICAL_FINDINGS=0_NEW_CONFIRMED
LONGITUDINAL_FINDINGS=1_OPEN_L001

No exhaustive parser/concurrency/lease/fault stress campaign was performed. Zero
new Vertical findings means no defect was established on that axis in this review.

## Phase-A diagnostics re-evaluated

| Prior topic | Current classification and observed surface | Remaining limit |
| --- | --- | --- |
| Scientific Memory convergence | CURRENT_REQUIRED_CAPABILITY, present: seven disposition classes, canonical/review ceiling, provenance, query/index, proof-bound supersession and candidate feedback | Full historical primary recovery remains PARTIAL; no old outcome is rewritten. |
| Archaeology | CURRENT_REQUIRED_CAPABILITY, present: immutable anchors vs branch locators, history/terminal dispositions, read-only catalog and qualified memory bridge | BOX-OFFICE/weather/nearby-protocol gaps remain review-only where exact evidence is missing. |
| Data / Evidence / PIT | CURRENT_REQUIRED_CAPABILITY, present: raw capture before parse, source/product identity, receipt/CAS binding, usable-data checks and strict instants | Missing external permission/source/dataset stays missing. |
| Factory | CURRENT_REQUIRED_CAPABILITY, present: protocol/data/code/trial bindings, registry/receipt/replay lifecycle, geometry/power declarations, role/alias/lineage outcome firewall | UNKNOWN declarations are valid disclosed unknowns, not empirical adequacy or permission. |
| Economic structural portfolio | CURRENT_REQUIRED_CAPABILITY, present: known/unknown/conflicted/not-applicable fields, provenance, canonical mechanism identity, relationship signals and memory side context | L001 remains open. Correlation is UNAVAILABLE and marginal contribution NOT_ESTIMATED. |
| MEGA A | CURRENT_REQUIRED_CAPABILITY, present: semantic memory relation, action admission, budget/route/capability states, frontier dispositions and explicit ranking inputs | `plan_research_chain` is a pure API with tests; a production worker consumer/persistent full-chain sink is not established. Final cross-lane binding remains future scope. |
| Phase-A H001/H002 | CURRENT_REQUIRED_CAPABILITY, independently re-proved and repaired against current policy | No blind cherry-pick. Cancellation production still belongs to future E review. |
| CP081/084 prior fixes | HISTORICAL_ONLY as repair implementations; diagnostic only | Current Economic surface differs. L001 is a fresh factual handoff finding, not permission to transplant old code. |

## Future / deferred ledger

| ID | Capability family | Classification | Disposition |
| --- | --- | --- | --- |
| F001 | Multi-Source ideation intake | FUTURE_WAVE2_CAPABILITY | Current packet/source machinery is not complete multi-source intake. |
| F002 | Broad Quant/mechanism Discovery | FUTURE_WAVE2_CAPABILITY | Quant contract exists; missing real qualified catalog is truthful no-source, not an invented producer. |
| F003 | Event novelty, valuation/expectations and fundamental mispricing Discovery | FUTURE_WAVE2_CAPABILITY | Existing arithmetic/dossiers are not economic novelty or mispricing proof. |
| F004 | Forced-flow economic Discovery | FUTURE_WAVE2_CAPABILITY | Rule/FAQ constraint surface exists; real eligible quantity, actor pressure and payoff remain unresolved. |
| F005 | MEGA C0 semantic scientific adjudication | FUTURE_WAVE2_CAPABILITY | R0 independent reconstruction/process/source checks do not establish semantic diversity. |
| F006 | MEGA D0 lifecycle/decay/replacement lineage | FUTURE_WAVE2_CAPABILITY | Structural identity and inactive guard are represented; active detector/replacement breadth remains future. |
| F007 | MEGA E task operations / cancellation producer | FUTURE_WAVE2_CAPABILITY | CANCELLED enum is not an actual cancellation command or receipt producer. |
| F008 | MEGA E outbox/recovery/whole-lifecycle Live Lab | FUTURE_WAVE2_CAPABILITY | Current pending/ACK evidence and no-stale-start behavior are present; full restart reconciliation and production visibility not claimed. |
| F009 | Final full-chain/cross-lane bindings | FUTURE_WAVE2_CAPABILITY | Full-chain pure planning API has executable tests; production consumer/persistence remains PARTIAL. Do not create a second scheduler to fill the table. |
| D001 | Unrecovered historical primary provenance / external datasets | INTENTIONALLY_DEFERRED | Preserve exact blockers and reopen only on admissible immutable evidence/access; never fill gaps from nearby artifacts. |
| D002 | Empirical sample adequacy, real outcomes, prospective observation, correlation/marginal value and economic learning | INTENTIONALLY_DEFERRED | Four authority gates remain FALSE; fixtures and declared assumptions do not create empirical truth. |
| D003 | Real capital / broker execution / live trading | INTENTIONALLY_DEFERRED | Existing V1 synthetic-paper chain remains fixture-qualified only. |
| D004 | VM/Site/D1/SSE/deployment qualification | INTENTIONALLY_DEFERRED | No production deployment or service probe performed. |
| U001 | Specific global VOI allocator / starvation aging | UNKNOWN_OWNERSHIP | Canonical control has bounded priorities/resources and A accepts declared action costs. A particular optimizer/fairness algorithm is not justified by current evidence. |

The CP002 matrix had 43 rows and 92 family entries: 57 narrowly qualified,
4 partial, 21 future and 10 intentionally deferred. Entries overlap by submodule;
counts are not a percentage of final completeness. One current partial is the
Longitudinal-owned frozen declaration handoff. Other partials preserve incomplete
historical/external evidence without pretending it exists.

FINAL_WAVE2_PHASE_B_STARTED=FALSE
PHASE_B_REQUIRED=TRUE
PHASE_B_START_CONDITION=OWNER_SUPPLIES_QUALIFIED_FINAL_WAVE2_INTEGRATED_SHA
SAFE_AS_DIAGNOSTIC_INPUT_TO_WAVE2=TRUE
FINAL_WAVE2_COMPLETENESS_QUALIFIED=FALSE

No rebase or future merge follows automatically. The final Wave-2 review must start
on a new exact integrated SHA and re-evaluate every finding, including H001/H002
and L001, against that architecture.

## CP004 — additional current contract surfaces repaired

H003 — CURRENT_REQUIRED_CAPABILITY / HORIZONTAL / REPAIRED.
`ImplementabilityAssessment` in the existing auxiliary schema did not represent
BLOCK_IMPLEMENTABILITY, UNKNOWN feasibility for source/PIT/expression/cost, or
the producer's exact-expression, blocker, candidate-mutation and authority fields.
Because additionalProperties=false, even ordinary complete PASS and PARK objects
failed full Draft 2020-12 validation. The old required-key inclusion test did not
detect the incompatibility. The schema now represents the actual emitted state
and detail families, retaining closed additional properties, false authority and
false mutation assertions. No implementation decision or model output changed.

H004 — CURRENT_REQUIRED_CAPABILITY / HORIZONTAL / REPAIRED.
The actual experiment producer emits protocol_payload as the frozen protocol
object, or null when not frozen. The auxiliary ExperimentEnvelope definition had
no property for either legitimate representation and rejected both outputs. Its
existing definition now includes the object/null field. Frozen-body integrity and
readiness remain the responsibility of existing freeze/hash/validator gates;
schema acceptance is representation, never execution or authority grant.

Six new tests validate actual producer outputs and JSON round trips using
jsonschema 4.26.0 Draft202012Validator: PASS/PARK/BLOCK, every unknown feasibility
family, frozen/nonfrozen envelopes, all four registered auxiliary producer families,
legacy minimal-record readability, and negative controls for newly represented
authority/mutation/undeclared fields. Before repair, 21 subcases failed across the
6 methods. Afterwards the focused 34-test suite and full regression pass.

The test requirement is declared in
`research/research_os/tests/requirements-contract-tests.txt`; the existing SEC P0
canonical CI gate explicitly installs it and runs the new contract suite. There
is no runtime dependency, new validator service, new registry or redefinition of
the six stable common contracts. Legacy minimal auxiliary records remain readable.

U002 — UNKNOWN_OWNERSHIP / DOCUMENTARY_ONLY binding, no feature built.
The registered shared `CandidateEconomicIdentity` schema requires a stable common
wire shape (hypothesis_generation, asset_class, beta/momentum/etc. exposure fields).
The current native economic_identity_v1 and structural_identity use a different
Python/JSON shape. Native producer and consumer behavior exists and is tested;
conformance of a current native-to-shared-wire adapter is not established. Parsing
the shared schema or checking that its filename exists cannot qualify that binding.
The CP004 matrix records this distinction explicitly and marks that binding
documentary-only/unknown ownership. No current qualified requirement justifies
inventing an adapter or redefining the stable common schema on this rail. Final
convergence must resolve the intended interface and ownership before claiming it.

The active matrix is now
`HORIZONTAL_C1_COVERAGE_MATRIX_CP004_20261021.json`: 43 rows, 95 overlapping family
entries, 59 narrowly qualified, 4 partial, 21 future, 10 intentionally deferred
and 1 documentary-only binding question. The CP002 JSON/validation/logs remain
historical evidence at their original source; they are not overwritten or treated
as current full-schema qualification. L001 remains open, owner LONGITUDINAL.

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
