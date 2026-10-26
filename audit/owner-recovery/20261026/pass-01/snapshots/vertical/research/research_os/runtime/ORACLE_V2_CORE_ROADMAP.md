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

### V2-1 — Core scientific contracts — IMPLEMENTED / BASELINE CI PASS

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

### V2-2 — Repository integration — IMPLEMENTED / RUNTIME QUALIFICATION PENDING

Goal: bind V2 contracts to durable Research OS surfaces without invalidating V1 evidence.

- [x] Add canonical V2 policy/config artifacts.
- [x] Add bounded end-to-end pre-outcome pipeline adapter.
- [x] Bind V2 trial/epoch/candidate metadata into new V2 pipeline artifacts.
- [x] Preserve existing V1 worker behavior unless explicitly routed to V2.
- [x] Prove no outcome access and four authorities false in fixture and real read-only integration.

### V2-3 — Adversarial verification — BASELINE CI PASS / EXTENSIONS LOCALLY PASS

- [x] Run V2 contract tests in repository CI.
- [x] Run relevant V1/Research OS regression suite.
- [x] Fix integration regressions.
- [x] Verify forbidden reverse-channel cases.
- [x] Verify infrastructure-error != scientific BLOCK.
- [x] Verify post-export epoch mutation fails closed.
- [x] Verify model-policy escape fails closed.
- [x] Verify candidate family mismatch fails closed.

### V2-4 — Whole pre-outcome qualification — PENDING

- [x] Produce one deterministic V2 end-to-end fixture:
  epoch -> trial -> candidate -> validator -> export intent -> ingest receipt.
- [x] Confirm no economic/prospective outcome is accessed in that fixture.
- [x] Produce fixture-scoped V2 qualification receipt.
- [x] Bind baseline exact implementation SHA and CI.
- [ ] Qualify actual Oracle V2 writes, recovery, natural wakes and reboot.

### V2-5 — Deployment decision — PENDING

V2 Core code completion is not deployment authorization by itself.

Before replacing the qualified V1 runtime, determine whether the V2 changes materially affect V1 runtime properties. If yes, rerun only affected operational gates and deploy through the exact-release discipline already qualified in V1.

No V2-E/economic/prospective activation is included.

Prepared path: `deploy/oracle_v2_host_prepare.py` -> three fixed, no-argument
root controls (`quant-v2-qualify`, `quant-v2-activate`, `quant-v2-status`).
Preparation leaves V1 running. The qualifier temporarily quiesces V1, migrates
fresh GitHub state with conflict checks, tests a real process crash before
ideation, and restores V1. Activation requires all eleven live gates and a fresh
transfer before enabling the separate V2 timer. V1 executable remains the
qualified rollback release; state reconciliation is required after V2 writes.

## Reconciled evidence — 2026-10-20

- Baseline executable: `a313dbe57e47c7cf50802a4b8a118f0dc9e52097`.
- Oracle V2 Core CI: `39357185710`, SUCCESS.
- SEC P0 pre-t0 CI: `39357185733`, SUCCESS.
- Real public GitHub dry-run: PASS, two fetches, zero pushes/writes; model not
  configured. This proves read-only integration, not runtime activation.
- Extensions: 42 local V2 tests PASS, including real Git migration/conflicts,
  claim-intent persistence before crash, lease recovery and primary evidence
  reconstruction. 73 combined worker/preflight/V2 tests PASS; 24 additional
  portfolio/producer readiness tests PASS.
- Epoch policy hashes now bind the actual versioned policy objects. This
  pre-activation correction occurs before any accepted evaluation export.
- Validator process identity includes boot ID/PID/start ticks. A separate
  validator independently reads the fresh primary-source blob and reconstructs
  the candidate. Decision scope is R0 structural checks; semantic diverse review
  is NOT_PROVEN. Different worker names alone cannot grant PASS.
- All four authorities remain false; evaluation remains SEALED.
- Remaining: exact extension CI, live Oracle V2 read-only proof, then the real
  Owner/root preparation boundary and gated live execution. No V2 operational
  or economic qualification is asserted by these local tests.

## Definition of Done

V2 Core can be marked complete only when:

`AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED = TRUE`

is supported by repository tests and a bounded whole-loop pre-outcome receipt, with all four authority flags still false.

`READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY` remains an eligibility status, never a profitability claim.

## Exact release checkpoint — a67ffec48fff895d5edc42171855e2213e49cf0d

Both exact-release CI gates passed: Oracle V2 Core `39360664488` and SEC P0
`39360664487`. The actual Oracle read-only entrypoint passed on this exact SHA:
two fresh fetches, zero push attempts/writes, all authorities false. The V1
timer remained active. Full hash-verified report and the independently probed
`ocarun` root boundary are preserved in `v2_evidence/`.

See `CP_V2_CORE_ORACLE_READONLY_20261020.json` for exact scope and remaining
operational gates. The single Owner command is
`V2_OWNER_ROOT_PREPARATION_20261020.sh`; its shell and Python syntax were checked.
It prepares V2 assets disabled and leaves V1 running. Actual V2 qualification,
activation, natural wakes and reboot remain pending; no final V2 verdict yet.
