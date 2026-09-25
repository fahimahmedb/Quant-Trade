# BLUE GOVERNANCE REFERENCE REPAIR — 2026-09-20

Authority: Blue / Mission Control.

## Finding

`REAL_GOVERNANCE_REFERENCE_DEFECT`

At parent Blue HEAD `23eb190babb5b2ffb5b54fea08633b3a55444e6c`, current target-host authorities required:

`governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`

but that path was absent from `blue/master-v2-2026-09-20` and returned 404.

The canonical source existed at:

`astra/p0-deep-adversarial-pre-t0@643deacdf5bbbdb1d2410c762eb20f72aff16bbf`

with Git blob:

`3ffe40107b7710c58de3b5a01b2e1574d611c5cb`

This made the Blue target-host handoff non-self-contained: an operator following the mandated read order from Blue could not resolve one of its required authorities without manually switching branches.

## Decision and repair

Import the exact source bytes, without semantic editing, into:

`governance/P0_QUALIFYING_DEPLOYMENT_CONTRACT_2026-09-20.md`

on the current Blue authority branch.

The imported blob must remain byte-identical to source blob `3ffe40107b7710c58de3b5a01b2e1574d611c5cb`.

## Scope

This is governance-reference repair only.

It does not:
- modify `blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`;
- reopen or strengthen Gate A;
- execute target-host qualification;
- declare t0;
- amend P14D;
- start Gate B or Product integration;
- authorize real capital.

## State retained

`GATE_A_V3_REPOSITORY_DISPOSITION = PASS`

`TARGET_HOST_ENTRANCE = PREPARED_ONLY / NOT_EXECUTED`

`READY_FOR_FINAL_RODAGE = FALSE`

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`PRODUCT_INTEGRATION = PAUSED`

`REAL_CAPITAL_AUTHORIZED = FALSE`

## Required post-commit verification

Resolve the live Blue HEAD, fetch the restored path from that exact HEAD, and require its Git blob SHA to equal:

`3ffe40107b7710c58de3b5a01b2e1574d611c5cb`

Also recheck:
- repository default branch;
- current branch count;
- open PR count;
- frozen candidate ref;
- final Astra audit ref.

No proof transfers to the new Blue governance commit; runtime proof remains pinned to the frozen candidate and independent audit SHAs.
