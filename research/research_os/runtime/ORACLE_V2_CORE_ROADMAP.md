# Oracle Research OS V2 Core — Execution Roadmap

Status: ACTIVE IMPLEMENTATION
Branch: `builder/oracle-v2-core-20261020`
Owner implementation authorization: 2026-10-20

Canonical architecture: `research/research_os/architecture/ORACLE_V2_CORE_SPEC.md`

## Permanent closed authorities

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

## Owner override

P0-D server-side branch protection is lifted. It is not a V2 DoD gate.

Normal no-force/no-rewind/no-reset operating discipline remains in force.

## Work packages

### V2-0 — Mission routing and specification — CLOSED PASS

- [x] Dedicated V2 branch created.
- [x] `CLAUDE.md` routes builders into V2 Core.
- [x] Owner implementation authorization recorded.
- [x] P0-D override recorded.
- [x] Canonical V2 Core architecture written.

### V2-1 — Core scientific contracts — IMPLEMENTED / CI PENDING

- [x] Closed authority assertion.
- [x] Research Epoch contract and hash.
- [x] Pre-export vs post-export mutation rule.
- [x] Model routing envelope check.
- [x] `SOURCE_PIT` / `MODEL_PIT` distinction.
- [x] Trial accounting from ideation.
- [x] CandidateCore + family-specific extensions.
- [x] Validator execution/decision separation.
- [x] Multidimensional scientific status.
- [x] Explainable priority decision contract.
- [x] Scoped Negative Memory contract.
- [x] Frozen export intent with outcome-key rejection.
- [x] Evaluation ingest receipt / reverse-channel allowlist.
- [x] Human/Supervisor blinding state.
- [x] Successor-only feedback release.
- [x] Fail-closed V2 Core qualification gate.

Implementation: `research/research_os/expansion/v2_core.py`
Tests: `tests/test_research_os_v2_core.py`

### V2-2 — Repository integration — ACTIVE

Goal: bind V2 contracts to durable Research OS surfaces without invalidating V1 evidence.

- [ ] Add canonical V2 policy/config artifacts.
- [ ] Add bounded end-to-end pre-outcome pipeline adapter.
- [ ] Bind V2 trial/epoch/candidate metadata into new V2 pipeline artifacts.
- [ ] Preserve existing V1 worker behavior unless explicitly routed to V2.
- [ ] Prove no outcome access and four authorities false.

### V2-3 — Adversarial verification — PENDING

- [ ] Run V2 contract tests in repository CI.
- [ ] Run relevant V1/Research OS regression suite.
- [ ] Fix integration regressions.
- [ ] Verify forbidden reverse-channel cases.
- [ ] Verify infrastructure-error != scientific BLOCK.
- [ ] Verify post-export epoch mutation fails closed.
- [ ] Verify model-policy escape fails closed.
- [ ] Verify candidate family mismatch fails closed.

### V2-4 — Whole pre-outcome qualification — PENDING

- [ ] Produce one deterministic V2 end-to-end fixture:
  epoch -> trial -> candidate -> validator -> export intent -> ingest receipt.
- [ ] Confirm no economic/prospective outcome is accessed.
- [ ] Produce V2 qualification receipt.
- [ ] Bind exact implementation SHA and CI.

### V2-5 — Deployment decision — PENDING

V2 Core code completion is not deployment authorization by itself.

Before replacing the qualified V1 runtime, determine whether the V2 changes materially affect V1 runtime properties. If yes, rerun only affected operational gates and deploy through the exact-release discipline already qualified in V1.

No V2-E/economic/prospective activation is included.

## Definition of Done

V2 Core can be marked complete only when:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED = TRUE`

is supported by repository tests and a bounded whole-loop pre-outcome receipt, with all four authority flags still false.

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY` remains an eligibility status, never a profitability claim.
