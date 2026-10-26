# BUILDER — POST-P0 FIRST VERTICAL SHADOW LOOP — FINAL HANDOFF — 2026-09-21

Mission: `governance/BLUE_FIRST_VERTICAL_ONE_BIG_BUILD_FROZEN_SPEC_2026-09-21.md`.
Branch: `builder/post-p0-first-vertical-shadow-loop-2026-09-21`. One Builder, four
internal milestones (M1-M4). This file is the mission's required final
handoff; it is the only file added under `handoff/` by this checkpoint.

```text
BUILD_BASE_SHA = aa6a5c1
BUILDER_FINAL_SHA = 1624b534866b798dcfa05198f348af46b7d81941
  (the M4 code/test commit; this handoff file itself lands in one further
  commit on top, per the mission's "may add a second commit for the handoff
  file" allowance -- the branch tip after both commits is the true final
  state, and `git log -1` on the pushed branch is authoritative over this
  static string.)

SELECTIVE_IMPORT_MANIFEST_VERIFIED = TRUE
  (verified during M1, cited here rather than redone: all 30 REUSE_AS_IS
  files in governance/BLUE_ONE_BIG_BUILD_IMPORT_MANIFEST_2026-09-21.md §2-4
  were vendored byte-identical to their pinned blobs and all 30 modules
  import cleanly -- committed/pushed at 2bc80e4, restated in STATE.md's
  "Builder checkpoint -- first vertical shadow loop" section.)
IMPORTED_SOURCE_SHA_FORWARD  = 83521dbfdd90027c90d04adfb7d814593c2355c5
  (parallel/claude-forward-data-2026-09-20)
IMPORTED_SOURCE_SHA_ECONOMIC = 35dff27b8fac53618da434ee6d31febbddcc0e69
  (parallel/claude-economic-v2-2026-09-20)
IMPORTED_FILE_BLOB_MAP = governance/BLUE_ONE_BIG_BUILD_IMPORT_MANIFEST_2026-09-21.md
  §2-4 (30 files: dataplane admissibility/form4_parse/forward_admissibility/
  forward_recorder + the full science/ package from IMPORTED_SOURCE_SHA_FORWARD;
  the full economics/ package, 19 files, from IMPORTED_SOURCE_SHA_ECONOMIC).
  Not re-verified this checkpoint -- no vendored file was touched by M4.

M1_SCIENTIFIC_ARTIFACT     = GREEN
  (src/quant/science/effect.py: assemble_form4_effect, cohort accumulation/
  registration, one-look quarantine, component construction, G/concentration
  guard, method qualification artifact, D19 handling, DeltaCoordinateBinding,
  evidence-label adjudication. Landed before this checkpoint; unmodified by M4
  except for the import this checkpoint added -- STRUCTURAL_INSUFFICIENT is
  now imported by quant.integration.econ_bridge and quant.learning.durable's
  callers to classify the durable INSUFFICIENT Learning outcome.)
M2_RESEARCH_ECONOMIC_BOUNDARY = GREEN
  (src/quant/integration/{forward_adapter,econ_bridge}.py,
  quant.economics.journal. Landed at 590011f. Extended this checkpoint with an
  optional learning= parameter on assess_and_admit; no change to its admission
  logic, refusal vocabulary or idempotence contract.)
M3_DESK_BOOK_BOUNDARY = GREEN
  (src/quant/desk/economic_size.py run_lane_entry/run_lane_scheduled_exit,
  src/quant/desk/execution.py phase parameter, src/quant/economics/
  {consistency,sizing}.py, src/quant/book/ledger.py FillConflict fingerprint.
  Landed at e8b9ff2. Extended this checkpoint with an optional learning=
  parameter on both lane functions; no change to SIZE/RISK/FILLS/BOOK logic.)
M4_LEARNING_E2E = GREEN

COHORT_PROTOCOL = FORM4_FIRST_VERTICAL_MULTI_COHORT_V1 (unchanged by M4; M1's
  frozen protocol_id/K_target/K_max/inter_cohort_gap/component_construction/
  minimum_information_guard are read, never altered, by this checkpoint).
METHOD_QUALIFICATION_STATE = UNCHANGED_FROM_M1
  (no interval method, qualification artifact or stress matrix was touched;
  M4 is downstream Learning wiring only).
ONE_LOOK_QUARANTINE_PROVEN = TRUE (M1 property, re-asserted by the full suite
  staying green; M4 added no new access path to outcome-bearing pre-stop
  records).
DELTA_COORDINATE_BINDING_PROVEN = TRUE (M1/M2 property; M4's only touch is
  reading DELTA_COORDINATE_UNRESOLVED/_MISMATCH/EFFECT_UNAVAILABLE reason
  codes off an already-computed AdmissionOutcome to classify a durable
  Learning record -- it does not evaluate or alter the binding itself).
FORWARD_IDENTITY_PROVEN = TRUE (M2 property, unchanged; this checkpoint's
  processed_id for an economic-assessment Learning outcome IS the same
  assessment_id forward_adapter.assessment_id_for derives, so Learning
  idempotence rides the same scoped identity rather than inventing a second
  one).
PRE_SIZE_COST_CHECK = UNCHANGED_FROM_M3 (economic_size.pre_size_cost_check;
  M4 only records the NO_TRADE outcome it already produces).
POST_SIZE_COST_CHECK = UNCHANGED_FROM_M3 (economic_size.post_size_cost_check;
  same).
RISK_INDEPENDENCE = UNCHANGED_FROM_M3 (desk.risk.evaluate/verify_final called
  exactly as M3 left them; M4 records their VETOED outcome, never influences
  the verdict).
SOLE_EXECUTION_AUTHORITY = PROVEN
  (tests/test_vertical_e2e.py::SoleAuthorityAndIsolationTests asserts exactly
  one ExecutionModel class definition exists under src/quant, by AST-level
  source-tree search, not by convention alone).
SOLE_BOOK_AUTHORITY = PROVEN
  (same test class asserts exactly one Ledger class definition and exactly
  one CapitalDesk class definition exist under src/quant).
LEARNING_DURABLE_IDEMPOTENCE = PROVEN
  (src/quant/learning/durable.py::DurableOutcomeStore -- processed_id keyed,
  payload-digest compared, NOOP on identical replay, LearningConflict raised
  and store left byte-for-byte unchanged on a same-id/different-payload
  replay, no rewrite of an original record ever -- a rejection-counterfactual
  evaluation gets its own processed_id and links back via `links`).
RESTART_REPLAY_MATRIX = GREEN
  (tests/test_learning_durable.py: >200-later-entries + restart + old-id
  replay for both a synthetic fixture and a true end-to-end
  econ_bridge/economic_size chain (test_e2e_true_replay_survives_
  200_later_entries_and_restart); crash-and-retry replay through
  run_lane_entry with the same opportunity_id produces one Ledger fill and
  one durable BOOKED record, not two, in
  test_e2e_booked_produces_exactly_one_durable_outcome).

CHANGED_PATHS =
  src/quant/learning/durable.py (new; ported from the pre-M2/M3 draft in
    .claude/worktrees/agent-a1f3b1232a841ab76, plus one addition: a KILL kind,
    which the draft did not carry because economic_gate's KILL verdict is a
    real M2 outcome the draft predates)
  src/quant/learning/__init__.py (re-exports DurableOutcomeStore/
    LearningConflict/payload_digest/KINDS incl. the new KILL)
  src/quant/paths.py (QuantPaths.learning_outcomes -> var/learning_outcomes.json)
  src/quant/integration/econ_bridge.py (assess_and_admit gained an optional
    learning= parameter; every terminal branch -- refusal-before-identity,
    NO_TRADE, KILL, CONTINUE(any eligibility) -- durably records exactly one
    outcome keyed by the assessment/refusal identity the boundary already
    computed; STRUCTURAL_INSUFFICIENT in the artifact's reason codes routes to
    the INSUFFICIENT kind rather than the generic ECONOMIC_ASSESSMENT kind)
  src/quant/desk/economic_size.py (run_lane_entry/run_lane_scheduled_exit
    gained an optional learning= parameter; new _terminal()/_record_lane_
    outcome() helpers record exactly one NO_TRADE/RISK_VETO/BOOKED outcome per
    terminal LaneDecisionCard, keyed by opportunity_id:phase:action)
  src/quant/desk/desk.py (CapitalDesk gained an optional learning= parameter,
    threaded to the existing run_lane_scheduled_exit call site)
  src/quant/clock.py (QuantSystem constructs one DurableOutcomeStore, shares
    it with CapitalDesk, and records a RESEARCH_RESULT outcome keyed by
    ticket_id whenever a research lane's outcome is VALIDATED)
  tests/test_learning_durable.py (ported draft's 10 tests, extended with 7
    RealEndToEndWiringTests exercising the real assess_and_admit/
    run_lane_entry call sites rather than DurableOutcomeStore in isolation)
  tests/test_vertical_e2e.py (new; the mission's full vertical-slice E2E list:
    negative/unavailable-evidence path, synthetic positive plumbing fixture
    end to end, Risk-veto/zero-size/post-size-cost-failure E2E paths, sole-
    authority AST assertions, no-network-import assertions)
  STATE.md (M4 section below; proof-inventory line 450 -> 478)

TEST_COMMANDS =
  PYTHONPATH=src python3 -m unittest discover -s tests -v
  python3 -m compileall src
  python3 scripts/generate_schemas.py --check
  python3 scripts/demo_quant_system.py

TEST_RESULTS =
  unittest discover: 478 tests, all green (up from 450 at M3)
  compileall: OK, no syntax errors
  generate_schemas.py --check: "schemas checked", no drift
  demo_quant_system.py: full run completed, all [PASS] assertions passed

FULL_SUITE_RESULT = GREEN (478/478)

REAL_DATA_POSITIVE_PATH_AVAILABLE = FALSE
  (unchanged from M1/M2: the ETF cross-sectional research lanes carry no
  Form4 cohort evidence, so a real VALIDATED strategy correctly refuses at
  the econ_bridge boundary with EFFECT_ESTIMATE_ON_FROZEN_COORDINATE_
  UNAVAILABLE until a Form4-evidenced cohort exists and matures -- the
  ~3.6-5.0 year structural timeline the frozen science geometry names. This
  is the intended fail-closed behaviour, not a defect this checkpoint could
  or should manufacture around.)
SYNTHETIC_POSITIVE_PATH_LABEL = SYNTHETIC_POSITIVE_PLUMBING_FIXTURE
  (tests/test_vertical_e2e.py::VerticalSliceEndToEndTests::
  test_synthetic_positive_path_continue_shadow_size_risk_fill_book_learning;
  a fabricated EffectEstimate/ScientificEffectArtifact clearing economic_gate
  as CONTINUE, walked through the real SHADOW promotion, SIZE, Risk, one
  real ExecutionModel.fill and one real Ledger.apply_fill, to exactly two
  durable Learning records -- this proves the wiring end to end, not a
  market edge, and is labeled as such in the test's own docstring.)

KNOWN_DEFERRED_LIMITATIONS =
  - CapitalDesk._run_strategy's inline entry path (SCAN/VET/SIZE/RISK/FILLS
    stages, still the one actually driven by QuantSystem.run_session) does
    not itself call economic_size.run_lane_entry and therefore does not
    durably record a Learning outcome for a live production entry through
    that path -- only economic_size.run_lane_scheduled_exit's already-spliced
    call site does, via CapitalDesk.learning. This mirrors the exact M3
    deferral already on record in STATE.md ("splicing this into
    CapitalDesk._run_strategy ... is a small, local change" -- still not
    done) and was kept out of scope here because the mission's M4 bullet list
    names economic_size.run_lane_entry/run_lane_scheduled_exit explicitly as
    the Desk/Risk call sites, not the pre-M3 inline duplicate. Both functions
    are wired for real and covered end to end by tests; only the production
    desk.py entry loop's use of the naive path (unchanged since before M3)
    means a real desk session today would not yet emit a durable Learning
    record for an inline SIZE/RISK/FILLS entry outcome.
  - No Control-Plane/Clock call site invokes econ_bridge.assess_and_admit
    automatically ahead of a Desk session; unchanged from M2/M3 (still a
    library call an operator/test invokes explicitly).
  - REAL_DATA_POSITIVE_PATH_AVAILABLE is FALSE per the frozen science
    geometry's own multi-year structural timeline, not a gap this checkpoint
    could close.

TARGET_HOST_TOUCHED = FALSE
P0_RUNTIME_MUTATED = FALSE
REAL_SEC_NETWORK_REQUESTS_MADE = 0
REAL_CAPITAL_AUTHORIZED = FALSE
t0 = NOT_DECLARED

BUILDER_VERTICAL_SHADOW_LOOP = READY_FOR_INDEPENDENT_REVIEW
```
