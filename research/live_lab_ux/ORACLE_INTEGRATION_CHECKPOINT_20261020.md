# Oracle → Live Lab integration checkpoint — 2026-10-20

Status: isolated integration work on top of the qualified Oracle Research OS state.

Working branch: `builder/live-lab-oracle-canonical-20261020`
Canonical Oracle base captured for this work: `b425a5a9c84a73fe0b48c055af5ff960753b613f`
Live Lab transplant commit: `6f23233de2da1f17aebcc6e906ac1af09988fa05`
Historical UX branch remains archival: `builder/live-lab-owner-ux-rebuild-20261015`.

## Why the branch was rebuilt

The historical Live Lab line had the validated/published UX but had diverged far behind the current Oracle Research OS. The integration branch was therefore recreated from the fresh Oracle canonical head and the validated `research/live_lab_ux` subtree was transplanted onto it. No force-push, reset or rewrite of autonomous Oracle evidence was used.

## This checkpoint's scope

This package closes the **event-contract boundary only**:

1. Oracle's existing durable `ACTION_STARTED` / `ACTION_COMPLETED` lifecycle remains the factual source.
2. `live_lab_contract.py` maps a canonical lane/stage to explicit allowlisted UI metadata.
3. `oracle_live_worker.py` is an opt-in wrapper around the canonical worker. The qualified `oracle_worker.py` remains unchanged.
4. Live Lab accepts explicit `ui_role`, `ui_label` and `ui_activity` only; worker IDs are not parsed to invent role or identity.
5. `hypothesis-generation` is represented as a distinct non-economic semantic activity. Its physical pose reuses the comparison rig only; this does not convert it into audit or Economic Look semantics.
6. Heartbeat, reconnect and snapshot remain non-authorizing. Snapshots may reconstruct factual identity/state but cannot replay business motion.

## Explicit non-goals at this checkpoint

- No public Site deployment.
- No production Oracle credential or Site principal provisioned.
- No HTTP event emission from Oracle to the Site yet.
- No replacement of D1/SSE with GitHub polling.
- No Economic Look ingress.
- No Safari/iPhone certification yet.
- No claim that browser pixels show a real Oracle wake until an authenticated Site canary proves the full chain.

## Current integration gate

`ORACLE_EVENT_CONTRACT_READY / SITE_INGRESS_NOT_YET_CONNECTED`

The next desktop/live gate is:

`real Oracle stage -> dedicated authenticated Site principal -> accepted native event -> D1 -> SSE -> LiveEventAdapter -> canonical mapper -> reducer -> visible factual worker -> completion -> no replay`

Only after that desktop/live gate is closed should the dedicated Safari/mobile qualification begin.

## Frozen authorities

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

This Live Lab work does not alter those authorities or convert visual activity into scientific/economic evidence.
