# BUILDER CP010 — Read-only evidence/acquisition composition

CHECKPOINT_ID: BUILDER_CP_010_ACQUISITION_OBSERVABILITY_20261020
WORKING_BRANCH: builder/v2-forward-20261020
TASK_BASE_SHA: 56961b2aa9b0f88a2719e867b334a0a7f95acc91
CP009_SHA: c4604f21d1a7b0e1d8e0973c2073538614a7b5bf
IMPLEMENTATION_AND_TEST_SHA: 4ffb8809fdc0faac5d70c319309e0e17b8f30ac8
CURRENT_BUILDER_HEAD_DESCRIBED: 4ffb8809fdc0faac5d70c319309e0e17b8f30ac8
FRESH_OBSERVED_ORACLE_V2_HEAD: c564699c8876bf1cf99ee5dd2387874b96a5baef
SAFE_TO_CONTINUE: TRUE
HOSTED_CI_STATUS: UNCONFIRMED_NETWORK_ACCESS_BLOCKED

## Objective / prior evidence

Complete CP008's owner-observability audit and implement only the CP009-confirmed
repository composition gap. CP009 records the exact inspected Builder, Oracle,
canonical/integration Live Lab and Oracle/Site bridge trees. CP12–CP16 and the
North Star retain their authority. This is isolated Builder work, not operational
closure, global history reconciliation or canonicalization.

## Minimal capability added

Extended the existing `build_edge_observability_projection` in
`research/research_os/expansion/edge_observability_v2.py` with optional
`producer_readiness`, `declared_routes`, and `validated_adapters` inputs.

The function invokes the existing CP008 bridge, which requalifies the exact
producer specification and delegates plan authority to the existing acquisition
firewall. No duplicate routing, provider discovery or firewall implementation
was introduced. No independent state store or new runtime component was added.

The optional `evidence_acquisition` vector exposes:

- exact explicit requirement text and intent status;
- ready/blocked/unresolved counts and their distinct overall state;
- actual plan firewall status/blockers, or `NOT_PLANNED` when absent;
- adapter/route/request/plan identities and exact readiness/intent hashes;
- network execution authorization FALSE and network calls FALSE;
- network connectivity `NOT_INSPECTED`, never a fabricated proxy/host verdict.

Raw locator parameters and source payloads are not copied into the owner vector.
Explicit conflicting hypothesis IDs are rejected. Callers remain responsible for
supplying the correct durable artifacts and lineage; this capability is not a
repository collector or epoch/state loader.

Producer readiness is separate from V2 validation readiness: `READY_PLAN_ONLY`
does not make documentary evidence supported, scientific maturity validated, an
experiment ready, or any authority open. Example synthetic fixture result:
`eligibility_rule=UNKNOWN`, acquisition `READY_PLAN_ONLY`, scientific maturity
`EVIDENCE_BOUND`, experiment readiness `INCOMPLETE`, network FALSE.

With no new inputs, the old projection and its hash remain identical (verified
against CP008 for task-only and dossier-bearing fixtures).

## Files / commits

- CP009 audit-only commit: c4604f21d1a7b0e1d8e0973c2073538614a7b5bf.
- Code/test commit: 4ffb8809fdc0faac5d70c319309e0e17b8f30ac8.
- Modified existing edge projection and its existing test file only.
- This checkpoint and `BUILDER_CP_010_LOCAL_VALIDATION_20261020.json` persist evidence.
- No Site, runtime task, source registry, adapter activation, policy, epoch,
  autonomous branch, workflow, dependency declaration or lockfile modified.

## Executed verification

Python 3.12.14, from the existing `/workspace/Quant-Trade` checkout:

1. Focused edge/bridge unittest modules: 27 tests PASS (includes existing tests).
2. All six shell steps from `.github/workflows/oracle-v2-core.yml` executed locally
   on exact clean code SHA `4ffb8809fdc0faac5d70c319309e0e17b8f30ac8`:
   compile PASS; 77/77 tests PASS, zero skipped; policy fail-closed PASS; claim
   ceiling PASS; exact-head fixture qualification PASS; real GitHub dry-run PASS.
3. Exact-head fixture qualification:
   `AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED`, receipt hash
   `82295fa29ef43cdf22508008738b06e767d7de149692836164b8fb908e6920a4`.
   This is the existing pipeline qualification, not proof of production wiring
   of the new optional projection.
4. Real GitHub-state dry-run additionally emitted under explicit
   `LOCAL_GITHUB_READ_ONLY` scope: observed autonomous state
   `c564699c8876bf1cf99ee5dd2387874b96a5baef`, two real fetches, zero GitHub writes,
   zero push attempts, zero hosted-model calls. No model inference was requested.
5. Legacy projection/hash comparison PASS; `git diff --check` PASS.

Durable JSON contains the qualification receipt, explicit local dry-run receipt,
workflow step outcomes, test counts and workflow/test-log hashes. Local logs
remain in `/workspace/.setup/cp010-validation/`.

## Adversarial cases

Twelve added tests cover composition without maturity promotion; no declared
route; absent adapter; actual firewall rejection of unsupported documentary
content; naive PIT cutoff; UNKNOWN version policy; forbidden content;
ambiguous exact routes; forbidden future-price requirement; mixed ready,
unresolved and blocked counts; no explicit gap; exact hash binding and tampered
readiness; conflicting hypothesis identity; outcome/open-authority input;
input immutability and forbidden file/network/process I/O; absent catalog
semantics; legacy optionality. Several tests cover multiple subcases.

## Hosted CI limitation

The existing Builder workflow is push-triggered and both audit and implementation
commits were pushed normally to the existing Builder branch. An attempt to read
its hosted result using `gh run list` failed with `Forbidden` for
`https://api.github.com/repos/fahimahmedb/Quant-Trade/actions/workflows/oracle-v2-core.yml`.
The environment's observed policy allows package-manager/Git hosts but does not
allow `api.github.com`. No token was requested and no policy bypass attempted.

Local execution of the workflow is **not** independent hosted Actions evidence.
No hosted success, run ID or artifact ID is claimed. The workflow's dry-run
command uses a CI scope label; the separate durable receipt explicitly uses
LOCAL scope to avoid confusing that label with hosted execution.

## Authority / scientific limits

ECONOMIC_EXPERIMENT_AUTHORIZED: FALSE
PROSPECTIVE_OBSERVATION_AUTHORIZED: FALSE
REAL_CAPITAL_AUTHORIZED: FALSE
LIVE_TRADING_AUTHORIZED: FALSE
OUTCOME_ACCESSED: FALSE
ECONOMIC_RESULT: NOT_OBSERVED

No missing evidence was acquired, no source was made usable, no candidate was
modified, no economic result was measured, and no Site/VM/reboot integration
was performed. Git pushes here persist Builder code/checkpoints only; the
dry-run's zero-write claim applies to the autonomous-state proof operation.

## Remaining work / exact resume action

1. Read CP009/CP010 and reacquire fresh Builder/Oracle heads without overwriting
   autonomous commits.
2. Confirm hosted Oracle V2 Core CI for the exact implementation SHA once Actions
   is accessible (the required API hostname is `api.github.com`). Hosted status
   remains an integration gate; do not silently treat local checks as its proof.
3. Final Integrator may import this optional pure projection after qualification.
   It must supply actual artifact identities and explicit route/adapter catalogs.
4. Actual Site collection/rendering and runtime wiring remain separate bounded
   integration work. Do not mutate Oracle, activate acquisition, fabricate
   missing routes or declare deployed owner observability closed from CP010.

The Builder capability is at a stable handoff boundary. Further operational
closure belongs to the Final Integrator under CP16, not an automatic continuation
into runtime/source activation by this workstream.
