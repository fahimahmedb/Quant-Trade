# W1 FACTORY FINAL — 2026-10-21

STATUS: FINAL — SCOPED EXPERIMENT-INFRASTRUCTURE FRONTIER EXHAUSTED UNDER CURRENT AUTHORITY

BASE_SHA: fecd09e0839f1208d9f876c311331221bde3ab7d
FINAL_CODE_HEAD_SHA: 6a2fba61ca96060bc309acfac1ea0f9f48c4b01e
FINAL_HEAD_SHA: SELF — the commit containing this checkpoint; a Git commit cannot embed its own SHA without changing that SHA. The exact pushed branch-head SHA and exact-head CI run are the authoritative resolution.
PARENT: 6a2fba61ca96060bc309acfac1ea0f9f48c4b01e
BRANCH: builder/w1-factory-experiment-depth-20261021

MODULE_SCOPE:
- experiment / protocol registry semantics
- freeze / preregistration support connections
- outcome firewall boundaries
- geometry / power / trial-accounting support
- reproducibility identity
- immutable experiment / protocol references
- replay / derivation semantics relevant to experiments
- experiment-state lifecycle
- fail-closed transition rules
- exact Candidate / Canonical Research Core / Validator boundary connections

## FINAL MODULE TRUTH

The current Experiment Infrastructure is one connected pre-outcome capability rather than a historical sidecar. The qualified chain is:

canonical candidate / hypothesis identity
→ canonical frozen envelope / protocol
→ pure immutable registry identity
→ canonical trial-accounting + geometry/power declarations (or explicit UNKNOWN)
→ permanently closed outcome firewall
→ canonical runner execution plan
→ exact pre-outcome receipt
→ deterministic replay verification
→ native Validator / Evaluation membrane

The registry is a pure binding contract and persists no competing scientific state. Historical `src/quant/factory/{experiments,geometry,power,outcome_firewall}.py` surfaces are compatibility re-exports to the current canonical laws rather than duplicate implementations.

## CAPABILITIES_QUALIFIED

QUALIFIED_CURRENT:
- immutable experiment registry identity attributable to exact experiment, hypothesis, generation, candidate, protocol, runner bindings, trial accounting, geometry and power
- canonical freeze / preregistration connection without a second freeze authority
- deterministic lifecycle `FROZEN -> PREPARED -> RECEIPT_BOUND -> REPLAY_VERIFIED`
- exact execution-plan, receipt and replay cross-binding
- reproducibility binding across candidate, protocol, source snapshots, PIT metadata and code/environment bindings
- geometry declarations with fail-closed validation and explicit UNKNOWN semantics
- power declarations / derivation only from explicitly declared assumptions, with explicit UNKNOWN semantics
- one canonical trial-accounting law supporting UNKNOWN, KNOWN, ESTIMATED and PARTIALLY_BOUNDED while rejecting bool/nonfinite/invalid states
- canonical recursive pre-outcome firewall, including direct Validator membrane enforcement
- native Validator experiment-infrastructure qualification; producer cannot patch Validator verdict after validation
- public experiment-infrastructure contract synchronized to the live attestation shape
- compatibility imports routed to canonical current implementations

CAPABILITIES_PARTIAL:
- NONE_ACTIONABLE under current authority.
- Per-experiment geometry or power may legitimately remain UNKNOWN when the protocol owner has not declared sufficient assumptions; that is a qualified scientific state, not a module implementation gap.

CAPABILITIES_REUSED:
- current canonical candidate / hypothesis identity and `freeze_experiment_envelope`
- current `DryRunExperimentRunner`, pre-outcome receipt and replay guarantees
- current source qualification / PIT machinery
- current `sha256_json` canonical scientific hashing
- current Validator v3 / Evaluation membrane
- current trial-ledger semantics, consolidated into one canonical trial-accounting validator
- existing CI / exact-head verification rail

CAPABILITIES_IMPORTED:
- IMPORT_EXACT: NONE.
- Historical Factory semantics were dispositioned component-by-component and adapted/hardened where admissible rather than copied wholesale.
- ADAPT_EXISTING: historical registry identity/lifecycle intent, geometry/power planning intent, firewall adversarial intent.
- SUPERSEDED_WITH_PROOF: historical geometry that inspected realized return vectors.
- SEALED_BY_AUTHORITY: historical outcome-opening capability / Blue-style gate semantics.

NO_BUILD_DECISIONS:
- no persistent experiment registry: would create a second scientific truth store
- no second frozen-experiment authority: canonical envelope/protocol remains authoritative
- no second queue, scheduler or orchestrator
- no second evidence/provenance store
- no registry-owned DRAFT state: draft belongs upstream candidate/protocol construction before canonical freeze
- no pre-outcome realized-return geometry or empirical effect estimation
- no outcome-open capability token or compatibility escape hatch
- no post-outcome ExperimentResult transition in this lane while outcome authority remains closed

## HISTORICAL_SOURCES_USED

- mandatory convergence base `fecd09e0839f1208d9f876c311331221bde3ab7d`
- authoritative North Star blob `a328b4e6d7d71dafd532938888ebf9818b1b610f`
- CP031–CP044 current/base integrity guarantees around frozen identity, envelopes, receipts, replay and trial accounting
- CP052 Factory archaeology/disposition identifying the unique historical Factory rail
- historical Factory rail `ca8ffe439953b063fb9d049773ce0b6245958c7d`
- historical Factory components semantically reviewed: `experiments.py`, `geometry.py`, `power.py`, `outcome_firewall.py` and their tests

## FILES_CHANGED

Base-to-final code/checkpoint surface is 32 files including this FINAL checkpoint:

CI / handoff:
- `.github/workflows/sec-p0-pre-t0-gate.yml`
- `handoff/W1_FACTORY_CP_001_20261021.md`
- `handoff/W1_FACTORY_CP_002_20261021.md`
- `handoff/W1_FACTORY_CP_003_20261021.md`
- `handoff/W1_FACTORY_CP_004_20261021.md`
- `handoff/W1_FACTORY_CP_005_20261021.md`
- `handoff/W1_FACTORY_CP_006_20261021.md`
- `handoff/W1_FACTORY_CP_007_20261021.md`
- `handoff/W1_FACTORY_CP_008_20261021.md`
- `handoff/W1_FACTORY_CP_009_20261021.md`
- `handoff/W1_FACTORY_CP_010_20261021.md`
- `handoff/W1_FACTORY_CP_011_20261021.md`
- `handoff/W1_FACTORY_CP_012_20261021.md`
- `handoff/W1_FACTORY_FINAL_20261021.md`

Canonical research / contracts:
- `research/research_os/contracts/experiment-infrastructure.schema.json`
- `research/research_os/expansion/economic_test_readiness_v1.py`
- `research/research_os/expansion/experiment_geometry.py`
- `research/research_os/expansion/experiment_infrastructure.py`
- `research/research_os/expansion/experiment_outcome_firewall.py`
- `research/research_os/expansion/experiment_power.py`
- `research/research_os/expansion/experiment_registry.py`
- `research/research_os/expansion/experiment_runner.py`
- `research/research_os/expansion/validation_readiness.py`

Tests:
- `research/research_os/tests/test_economic_readiness_validation.py`
- `research/research_os/tests/test_w1_factory_economic_integration.py`
- `research/research_os/tests/test_w1_factory_experiment_bridge.py`
- `research/research_os/tests/test_w1_factory_experiment_infrastructure.py`
- `research/research_os/tests/test_w1_factory_firewall_hardening.py`

Legacy compatibility surfaces:
- `src/quant/factory/experiments.py`
- `src/quant/factory/geometry.py`
- `src/quant/factory/outcome_firewall.py`
- `src/quant/factory/power.py`

## SHARED_SURFACES_TOUCHED

- `research/research_os/expansion/experiment_runner.py`
  - WHY_REQUIRED: W1 geometry/power/multiplicity declarations must participate in exact frozen protocol identity when present.
  - CONTRACT_CHANGE: optional W1 declarations are frozen/bound; legacy callers without them remain compatible.
- `research/research_os/expansion/validation_readiness.py`
  - WHY_REQUIRED: Validator is the Evaluation membrane and must own Factory qualification and recursive outcome-blindness.
  - CONTRACT_CHANGE: native `experiment_infrastructure` and `outcome_firewall` checks are readiness laws.
- `research/research_os/expansion/economic_test_readiness_v1.py`
  - WHY_REQUIRED: connect canonical envelope/runner/trial objects to W1 infrastructure before Validator handoff.
  - CONTRACT_CHANGE: reproducibility payload binds registry/infrastructure identity; producer-side post-validation verdict patching removed.
- `.github/workflows/sec-p0-pre-t0-gate.yml`
  - WHY_REQUIRED: exact-head CI now runs the W1 Factory suite explicitly.

EXPECTED_CROSS_LANE_IMPACT:
- integration must preserve current exact-binding guarantees and W1 added registry/declaration/firewall semantics
- callers providing prohibited outcome-bearing ignored extensions now BLOCK instead of being silently ignored
- callers mutating geometry, power, multiplicity, plan, receipt, replay, trial accounting or registry identity after freeze now fail closed
- safe pre-outcome extension metadata remains admissible

## PUBLIC_CONTRACTS_CHANGED

- public `experiment-infrastructure` attestation exists and is schema-bound
- runner frozen protocol identity includes optional W1 `geometry_declaration`, `power_declaration`, and `multiplicity_method` when present
- reproducibility binding includes experiment registry and infrastructure identity
- Validator v3 natively requires a cryptographically/coherently bound Experiment Infrastructure
- Validator v3 natively requires recursive canonical outcome-firewall PASS in addition to explicit outcome-state closure
- compatibility `quant.factory` imports resolve to the same canonical laws, not parallel implementations

SCHEMAS_CHANGED:
- ADDED and synchronized `research/research_os/contracts/experiment-infrastructure.schema.json`
- no second readiness schema was created: repository contract archaeology found no separate public Validator/readiness-result schema requiring synchronization
- `experiment-result.schema.json` remains a separate post-observation/result contract and is not pulled into this pre-outcome lane

## TESTS_ADDED

Dedicated W1 suites added:
- `test_w1_factory_experiment_infrastructure.py`
- `test_w1_factory_experiment_bridge.py`
- `test_w1_factory_economic_integration.py`
- `test_w1_factory_firewall_hardening.py`

Existing Validator readiness tests were expanded/migrated to exercise the native W1 contract.

Material adversarial falsifications include:
- foreign registry entry / wrong candidate / wrong protocol
- protocol mutation after registration
- foreign or mutated execution plan, receipt and replay
- self-consistent outer-hash rebuild after declaration/plan tampering
- stale/forged geometry/power declarations
- bool, NaN, Infinity and semantic-null abuse
- UNKNOWN carrying illicit numeric claims
- invalid lifecycle transitions
- trial-accounting invalid states and nonfinite/bool estimates
- historical outcome-gate/environment-token bypass attempts
- role/alias/derived-lineage outcome leakage
- top-level and nested ignored-field outcome payloads at direct Validator boundary
- safe provenance controls to prevent over-broad firewall rejection
- live public-schema drift

FOCUSED_TEST_RESULT:
- CP012 exact-head W1 Factory experiment-infrastructure suite: PASS.
- CP012 exact-head SEC P0 lane suite: PASS.

BROADER_TEST_RESULT:
On exact code head `6a2fba61ca96060bc309acfac1ea0f9f48c4b01e`, GitHub Actions run `39578983345` completed SUCCESS:
- fail-closed no-SEC-identity check: PASS
- generated schema drift: PASS
- status artifact freshness: PASS
- full unit suite: PASS
- W1 Factory suite: PASS
- SEC P0 suite: PASS
- V1 end-to-end regression: PASS
- exact-head verification artifact generation: PASS
- artifact upload: PASS
- committed placeholder restore: PASS
- clean working tree: PASS

The FINAL commit changes only this handoff document; its own exact-head CI run remains the authoritative final branch-head verification and is intentionally not self-referentially embedded here.

## SCIENTIFIC_CLAIM_LIMITS

- READY means structurally ready for a later separately authorized economic test; READY != PROFITABLE.
- geometry/power declarations are planning assumptions, not empirical effects, observed volatility, edge evidence or profitability claims.
- DERIVED power is derived only from declared assumptions, never outcome data.
- UNKNOWN remains UNKNOWN when assumptions/data are insufficient.
- no future outcome was read, inferred or fabricated.
- no historical raw bytes, provider identity, deployment proof or host/reboot proof was invented.
- no economic outcome evaluation was performed.
- no prospective observation was activated.
- no real-capital or live-trading authority was created.

## DEPENDENCIES_ON_OTHER_LANES

- No merge, cherry-pick or runtime dependency on another Wave-1 builder branch was introduced.
- Semantic dependencies are only on canonical contracts already present on the mandatory base/current convergence rail: Candidate identity, canonical envelope/freeze, source/PIT qualification, runner bindings, scientific hashing and Validator membrane.
- Future integration may encounter shared-file edits from other lanes, but this lane does not require another lane branch to function.

## EXPECTED_INTEGRATION_CONFLICTS

Potential merge hotspots:
- `research/research_os/expansion/validation_readiness.py`
- `research/research_os/expansion/experiment_runner.py`
- `research/research_os/expansion/economic_test_readiness_v1.py`
- `.github/workflows/sec-p0-pre-t0-gate.yml`
- `research/research_os/contracts/experiment-infrastructure.schema.json`

Integration rule: resolve semantically, preserving CP031–CP044 exact candidate/protocol/source/PIT/code-environment bindings plus W1 registry/declaration/trial/replay/firewall laws. Do not resolve conflicts by restoring duplicate legacy Factory authorities.

## REMAINING_GAPS

No additional high-value scientifically justified implementation gap in the owned pre-outcome Experiment Infrastructure is currently actionable.

REMAINING_GAP_CLASSIFICATION:
- economic outcome access / economic result evaluation: SEALED_BY_AUTHORITY
- prospective observation activation: SEALED_BY_AUTHORITY
- real capital: SEALED_BY_AUTHORITY
- live trading: SEALED_BY_AUTHORITY
- real future outcome/data bytes: EXTERNAL_ACCESS_REQUIRED and SEALED_BY_AUTHORITY for this campaign
- post-outcome `ExperimentResult` transition: SEALED_BY_AUTHORITY
- registry-owned DRAFT lifecycle: NO_BUILD_REQUIRED; upstream candidate/protocol construction owns draft semantics
- persistent second registry/store: NO_BUILD_REQUIRED
- second scheduler/orchestrator: NO_BUILD_REQUIRED
- historical realized-return geometry: SUPERSEDED_WITH_PROOF
- historical outcome-opening gate: SEALED_BY_AUTHORITY

There is no silent MISSING state in the scoped capability inventory.

## INTEGRATION MANIFEST

SOURCE_BRANCH: `builder/w1-factory-experiment-depth-20261021`
MANDATORY_BASE: `fecd09e0839f1208d9f876c311331221bde3ab7d`
QUALIFIED_CODE_HEAD: `6a2fba61ca96060bc309acfac1ea0f9f48c4b01e`
NORTH_STAR_BLOB: `a328b4e6d7d71dafd532938888ebf9818b1b610f`
HISTORICAL_FACTORY_RAIL: `ca8ffe439953b063fb9d049773ce0b6245958c7d`

INTEGRATION_ORDER_RECOMMENDATION:
1. preserve canonical envelope/runner exact-binding code
2. integrate canonical W1 registry/geometry/power/firewall/infrastructure modules
3. integrate Validator/economic-readiness connections
4. integrate public schema + compatibility re-exports
5. integrate W1 tests and CI entry
6. rerun generated-schema/status checks, full unit, W1 suite, broader regression and exact-head verification

DO_NOT_IMPORT_AS_AUTHORITY:
- historical persistent/in-memory registry state
- historical realized-outcome geometry
- historical outcome-opening capability gate

## AUTHORITY_STATUS

ECONOMIC_EXPERIMENT_AUTHORIZED=FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED=FALSE
REAL_CAPITAL_AUTHORIZED=FALSE
LIVE_TRADING_AUTHORIZED=FALSE
OUTCOME_ACCESSED=FALSE

SAFE_TO_INTEGRATE: TRUE, contingent on semantic conflict resolution and green integration-rail tests.
SAFE_TO_CONTINUE_THIS_MODULE: FALSE under current authority and dependencies; reopen only if a new evidenced pre-outcome gap appears or authority/dependency context materially changes.

GLOBAL_NORTH_STAR_COMPLETION_CLAIMED: FALSE
