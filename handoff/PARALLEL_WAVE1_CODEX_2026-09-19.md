# Parallel Wave 1 — Codex independent handoff

## Scope and authority

This Wave implements one bounded, outcome-blind economic decision slice. It does not
claim to complete Quant, does not consume prospective P0 data, does not modify the
Clock, does not select D07/D09 scientific parameters, and grants no real-capital
authority. The frozen EC1 coordinate is consumed rather than redefined.

## Workstream matrix (exactly 35 rows)

| ID | WORKSTREAM | BLUE_GATE | STATUS | FILES_ARTIFACTS | TESTS | COMMIT_SHA | NEW_FINDINGS | REMAINING_BLOCKER | NEXT_ACTION |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | D09 Economic Core restant | GO WITH FIREWALL | IMPLEMENTED | `src/quant/economics/engine.py` | `test_economic_engine.py` | fe4ebae | Executable conservative Phi-like net-value gate can remain outcome-blind | BEEE/MEUE authority values remain Blue-frozen inputs | Bind an authorized D09 parameter manifest |
| 2 | Modèle complet de frictions | GO | TESTED | `engine.py` required friction schema | missing/duplicate friction tests | fe4ebae | Omitted friction must fail closed | Calibration data absent | Calibrate without P0/prospective leakage |
| 3 | Capacity model | GO | IMPLEMENTED | capacity input and clipping | capacity/no-capacity tests | fe4ebae | Zero capacity is NO_TRADE, not no-edge | Capacity is supplied, not estimated | Add versioned non-P0 liquidity estimator |
| 4 | Signal → ordre → PnL net | GO WITH FIREWALL | DESIGNED | economic input/output contract | net-value tests | fe4ebae | Effect-to-value boundary is explicit | Not wired to Desk orders | Add event hook outside Clock/P0 files |
| 5 | Portfolio construction / sizing | GO | DESIGNED | requested versus executable exposure | clipping test | fe4ebae | Capacity changes the evaluated exposure | No covariance/Book interaction | Add portfolio-aware sizing consumer |
| 6 | Critères économiques continue / kill | GO WITH FIREWALL | TESTED | `Decision` and ordered reasons | continue/kill/no-trade tests | fe4ebae | Positive effect may correctly KILL after costs | Threshold provenance needs Blue-authorized source | Freeze parameter manifest before evidence |
| 7 | Execution simulator | GO | ALREADY_FROZEN | existing `quant/desk/execution.py` untouched | not rerun | base | Existing simulator already models spread/impact/capacity | Financing/borrow/latency integration absent | Feed realized shortfall to economic registry |
| 8 | Passive Forward Market Recorder | GO | NOT_STARTED | none | none | — | P0 boundary prevented scheduler work | Recorder architecture not implemented | Design non-P0 append-only recorder hook |
| 9 | Données externes non-Form-4 | GO WITH FIREWALL | NOT_STARTED | none | none | — | No dataset needed for bounded slice | Source selection not begun | Rank data by economic VOI |
| 10 | Parser Form-4 downstream | GO WITH FIREWALL | BLOCKED | none | none | — | Deliberately did not inspect P0 reservoir | Downstream visibility/admissibility gate | Await safe downstream interface |
| 11 | Qualification/admissibilité downstream | GO WITH FIREWALL | BLOCKED | none | none | — | Kept prospective values out of design | Frozen consumable protocol incomplete | Implement only after Blue gate |
| 12 | D07 Final Geometry | GO WITH FIREWALL | BLOCKED | governance reviewed only | none | — | No geometry selected from sealed values | Blue final selection authority required | Preserve open-space firewall |
| 13 | D05 discharge conditions | GO WITH FIREWALL | BLOCKED | governance reviewed only | none | — | No ceiling consulted | Governance dependencies remain | Blue-led discharge |
| 14 | D05-B / D08 protocol preparation | GO WITH FIREWALL | WAIT | none | none | — | Route-A D08 is inactive | Final Route-B protocol not frozen | Do not revive Route A |
| 15 | D19 specification | GO WITH FIREWALL | BLOCKED | governance reviewed only | none | — | D19 remains decided-not-consumable | Blue specification authority required | Preserve pending state |
| 16 | Route A vs Route B | WAIT / DO NOT REOPEN | WAIT | none | none | — | Route B treated as frozen | none; intentional wait | Never reopen in this lineage |
| 17 | Research Factory familles indépendantes | GO | NOT_STARTED | none | none | — | Breadth remains highest research need | No new family evaluated | Scout structurally independent lane |
| 18 | Hypothesis scouting / littérature | GO | NOT_STARTED | none | none | — | No web/literature values consulted | Search protocol absent | Predeclare search and stopping rules |
| 19 | Historical exploratory research | GO | NOT_STARTED | none | none | — | No dataset consulted | Independent family unavailable | Run exploration after registry exists |
| 20 | Benchmarks / null models | GO WITH FIREWALL | NOT_STARTED | none | none | — | Existing SPY scientific benchmark preserved | Null suite absent | Add beta/factor/placebo nulls |
| 21 | Statistical decision framework | GO WITH FIREWALL | DESIGNED | uncertainty charge is separate from margin | uncertainty kill test | fe4ebae | Statistical uncertainty cannot be hidden in economic margin | HAC/bootstrap absent | Implement predeclared dependent-data inference |
| 22 | Robustness methodology | GO WITH FIREWALL | NOT_STARTED | none | none | — | D19 blocks missingness authority | Consumable adverse set absent | Await/freeze D19 then implement |
| 23 | Regime / market-state methodology | GO WITH FIREWALL | NOT_STARTED | none | none | — | No post-hoc regime selection introduced | Method absent | Predeclare state taxonomy before outcomes |
| 24 | Economic falsifiers | GO WITH FIREWALL | TESTED | dominated-effect and uncertainty rules | adversarial kill tests | fe4ebae | Significance is insufficient for economic continuation | Scenario stress grid absent | Add predeclared joint scenarios |
| 25 | Capital-readiness framework V3 | GO | DESIGNED | provenance/fingerprint/SHADOW-only boundary | authority refusal test | fe4ebae | Missing provenance blocks readiness | Full readiness checklist absent | Compose with Book and validation evidence |
| 26 | Paper/shadow execution architecture | GO | IMPLEMENTED | `mode` authority boundary | REAL refusal test | fe4ebae | REAL is structurally rejected | Desk integration absent | Persist assessments before paper orders |
| 27 | Monitoring post-deployment | GO | NOT_STARTED | reason codes suitable for telemetry | none | — | Reasons are machine-readable | No monitor/history | Append assessments and outcomes |
| 28 | Research prioritization | GO WITH FIREWALL | DESIGNED | opportunity-cost review below | none | — | Independent breadth dominates more local tuning | No persistent priority update | Register next lane as capability gap |
| 29 | Builder allocation | GO | DESIGNED | opportunity-cost review below | none | — | Avoided low-value dashboard/Clock changes | No automated allocator | Persist ranked build tasks |
| 30 | Red Team méthodologique | GO | TESTED | adversarial tests + self red team | 8 tests | fe4ebae | Weak provenance and omitted frictions fail closed | Five open weaknesses below | Convert findings to tracked defects |
| 31 | Evidence / experiment registry | GO | DESIGNED | deterministic input fingerprint | order/version fingerprint test | fe4ebae | Same inputs canonicalize; version change changes identity | No durable append-only store | Add conflict-aware assessment journal |
| 32 | Economic dashboard minimal | GO LOW PRIORITY | NOT_STARTED | none | none | — | Correctly deferred behind economic truth | No view | Render only persisted state later |
| 33 | Broker/API sandbox | GO, PAPER/SANDBOX ONLY | NOT_STARTED | REAL mode refused | authority refusal test | fe4ebae | No irreversible integration attempted | Sandbox adapter absent | Add replay-only adapter first |
| 34 | Operational failure modelling | GO | DESIGNED | fail-closed validation | invalid schema/provenance tests | fe4ebae | Invalid/nonfinite/duplicate inputs cannot decide | Restart/idempotence not tested | Add persistent journal crash replay |
| 35 | Opportunity-cost review | GO VERY HIGH PRIORITY | TESTED | this handoff | scope review | final | Economic gate delivered before UI/broad scaffolding | Breadth and calibrated costs now dominate | Build registry, independent lane, calibration |

## Repository state and commits

BASE_SHA = 8d5dbb41559c4716e94d5290b6ae979a8b96143c

FINAL_SHA = branch tip; resolve immutably with `git rev-parse HEAD` (a commit cannot embed its own SHA)

BRANCH = parallel/codex-wave1-economic-system-2026-09-19

Commits:

1. `b7f427f` — `evidence: initialize Codex Wave 1 checkpoint`
2. `fe4ebae` — `economic: add provenance-bound net value gate`
3. final handoff/checkpoint commit (this artifact)

## Tests executed

- `python -m pytest -q tests/test_economic_engine.py` — 8 passed.
- Full suite intentionally not run: SEC/P0 tests cross the explicitly isolated mission boundary.

Number of new tests: **8**.

## Datasets and research

Datasets consulted/created: **none**. No Form-4/P0 reservoir, prospective count,
identity, locator, outcome, distribution, or proxy was accessed. Inputs in unit
tests are synthetic and carry explicit mock provenance.

Research families added: **none**. Positive empirical results: **none**. Negative
empirical results: **none**. The only positive result is engineering evidence that
a fully specified synthetic opportunity continues; negative adversarial cases show
that cost domination, missing capacity, missing friction, weak provenance, and real
capital mode are refused.

## Defects

### Existing defects found

- `W1-ECON-001`: the existing execution simulator does not by itself express the
  complete forward friction schema (latency, financing, borrow, turnover).
  Classification: economic-model incompleteness. Not modified because this Wave
  introduced a separate decision contract first.
- `W1-EVID-001`: no durable conflict-aware economic-assessment registry currently
  binds a decision to its complete economic input fingerprint. Classification:
  audit/restart gap.

### Defects introduced by this Wave

- `W1-SELF-001`: cost amounts are supplied as already-computed currency values;
  the engine does not prove their functional dependence on order size.
- `W1-SELF-002`: the scalar uncertainty subtraction cannot represent asymmetric or
  correlated joint scenarios.
- `W1-SELF-003`: fixed costs remain unchanged after capacity clipping, which is
  conservative for some components but structurally wrong for variable costs.

None is marked CLOSED; each needs a red-to-green discriminating test with its fix.

## Self Red Team

1. **Cost scaling mismatch.** Reproduce with capacity halved while every supplied
   cost remains constant. Impact: distorted net value and potentially false kill or
   continue. Deployment relevance: high. Fix: typed fixed/per-notional/nonlinear
   cost functions. Blue authority: required for Form-4 coefficient sources, not for
   generic machinery.
2. **Correlation blindness.** Hypothesis: uncertainty and liquidity deterioration
   co-occur in stress. Impact: optimistic joint tail. Deployment relevance: high.
   Fix: predeclared joint scenario envelope. Blue authority: yes for D09 scenario
   authority.
3. **No persistent assessment journal.** Kill process after assessment and before
   Desk submission. Impact: duplicate or untraceable decisions. Deployment
   relevance: high. Fix: append-only idempotent journal keyed by assessment id and
   fingerprint. Blue authority: no.
4. **No portfolio interaction.** Two individually positive trades can breach shared
   factor/concentration limits. Impact: false CONTINUE at portfolio level.
   Deployment relevance: high. Fix: treat CONTINUE as economic eligibility only,
   then require RISK/Book acceptance. Blue authority: no for generic integration.
5. **Cost provenance authenticity is syntactic.** A nonempty source string can lie.
   Impact: false confidence in calibration. Deployment relevance: high. Fix: bind
   immutable dataset/artifact hashes and validation state. Blue authority: yes when
   selecting claim-authoritative D09 sources.

## Decisions refused as outside authority

- No Route-A reactivation or D08 floor search.
- No D07 geometry, alpha, power, estimator, robustness, regime, or cost coefficient
  selected from prospective information.
- No D19 adverse completion set invented.
- No P0 file, Clock, SEC acquisition file, scheduler, reservoir, or t0 changed.
- No real-capital route, credential, broker, or irreversible integration added.

## Opportunity-cost review

The highest-value next unit is **not** dashboard work or another parameter grid.
It is a persistent, conflict-aware economic assessment journal integrated between
validated research evidence and the existing Desk, followed by a structurally
independent research family and non-P0 calibration of friction/capacity. This
combination most directly reduces false continuation, improves restart safety, and
increases discovery breadth. P0-dependent downstream work remains gated rather
than being approximated from forbidden information.

## Top 10 contributions by expected net-economic value

1. Makes after-friction conservative net value—not significance—the action gate.
2. Fails closed if any major friction category is absent.
3. Separates CONTINUE, NO_TRADE, and KILL semantics.
4. Structurally refuses real-capital mode.
5. Binds decisions to deterministic complete-input fingerprints.
6. Requires provenance on capacity, margins, thresholds, and costs.
7. Applies capacity before net-value evaluation and reports clipping.
8. Keeps uncertainty distinct from the economic margin.
9. Preserves the frozen EC1 effect identity/version without redefining it.
10. Identifies persistence, joint-scenario, portfolio, and calibration gaps rather
    than overstating readiness.

## What the system should do next

Persist each assessment before Desk action, reject same-id/different-fingerprint
conflicts, and replay cleanly after crash. Then connect it to a predeclared,
structurally independent research lane and calibrated non-P0 market data. The Clock
hook should consume a future `ECONOMIC_ASSESSMENT_REQUESTED` event; this Wave does
not modify the Clock.

P0_RESERVOIR_ACCESSED   = FALSE
P0_PROTOCOL_MUTATED     = FALSE
ROUTE_A_REOPENED        = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
T0_TOUCHED              = FALSE
CLAUDE_BRANCH_ACCESSED  = FALSE
