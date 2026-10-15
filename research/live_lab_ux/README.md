# Live Research Lab — native integration

Integration branch: `builder/live-lab-native-integration-20261015`.

This branch starts from the proved platform-probe checkpoint `809ec7e3d088a4ba4c5857771e6422ab91a139f4` and imports only the isolated UX subtree from `builder/live-lab-ux-vision-20261014`; it does **not** merge that branch's unrelated research history.

## Safety state

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
LIVE_E2E_PASS = NOT_CLAIMED
DEPLOYMENT = NOT_PERFORMED
```

Nothing in this UI authorizes capital, trading, research conclusions, or economic decisions.

## Two surfaces

- `index.html` remains the deterministic `DEVELOPMENT/REPLAY` UX harness.
- `live.html` is the native live browser surface. It binds same-origin `/api/work/events` through browser `EventSource`, then through the canonical native mapper and the existing deterministic scene reducer.

The live surface adds no GitHub polling, retry scheduler, heartbeat timer, lease timer, progress timer, or fabricated worker activity. Browser `EventSource` owns the already-proved SSE reconnect/cursor behavior.

## Native event authority

The proved worker contract currently accepts only:

```text
ACTION_STARTED
ACTION_COMPLETED
WORKER_HEARTBEAT
SESSION_ENDED
```

`adapters/platform-native.js` maps only those accepted facts. It deliberately does **not** infer:

- Codex == Owner identity;
- Researcher / Builder / Auditor / Manager roles;
- progress values or percentages;
- KILL / PARK / PROMOTE;
- Economic Look ownership;
- economic results.

An accepted native worker is therefore represented as the protocol-backed `Worker` role unless stronger explicit semantics are supplied by a future proved contract. Missing progress remains `UNKNOWN`.

## Architecture

```text
native Site SSE frame
        |
        v
platform-native-sse.js
        |
        v
LiveEventAdapter
        |
        v
platform-native.js
        |
        v
normalized UI event
        |
        v
reduceScene() factual UI state
        |
        v
deterministic animation authorization
        |
        v
DOM/CSS rendered scene
```

Development replay substitutes `FixtureReplayAdapter` at the adapter boundary. Renderer and state machine stay shared.

## Snapshot / replay truth guard

The native SSE path can send a factual snapshot and then replay active events already represented by that snapshot. `mapNativeSnapshot()` now emits a replay guard containing accepted event IDs and generation-scoped stream watermarks. `reduceScene()` seeds those IDs/sequences during snapshot application.

Therefore:

- snapshot reconstruction never starts business animation;
- replayed SSE frames already represented by the snapshot are ignored;
- only a genuinely later accepted event can resume business animation;
- generation changes remain isolated by stream key `worker + session + generation`.

## Truth rules

- A heartbeat updates presence only; it cannot create or advance business animation.
- Disconnect freezes business animation.
- `CONNECTED` and `SNAPSHOT` restore transport/factual state but do not restart work animation.
- Duplicate IDs and out-of-order sequence numbers cannot replay animation.
- `UNKNOWN` progress renders `Progress unknown`; no percentage is synthesized.
- KILL/PARK/PROMOTE changes only on an exact supported `DECISION` UI event; the current native worker contract does not produce one.
- Only explicit event-backed roles are materialized.

## UX surface

Mobile Safari remains the primary layout. The shell uses ordinary DOM/CSS, safe-area insets, Pointer Events and a transform-only pan/pinch camera.

The replay fixtures continue to demonstrate richer future semantic roles and Economic Look states, but they remain visibly synthetic development fixtures and are not evidence.

## Tests

From this directory:

```bash
npm test
```

The suite uses Node's built-in test runner. `tests/platform-native.test.js` covers the real probe-shaped worker contract, generation-scoped ordering, duplicate suppression, heartbeat-only presence, unsupported-event rejection, factual snapshot reconstruction, snapshot replay suppression, forbidden identity/economic inferences, and the thin SSE subscription.

During the integration session the exact native adapter/state-machine subset was executed locally and passed 11/11 tests. A full repository clone/CI run was not available in that runtime because direct GitHub DNS access from the execution container was unavailable.

## Known platform boundary

This integration uses the platform capabilities already proved by the probe branch. It does not claim proof for the unresolved Codex/Owner principal, a fully remote Builder identity, native APNs delivery, app-specific mobile behavior, third-party model routing, or production publication of this UX surface.

Those are capability boundaries, not reasons to replace the working native event/SSE architecture with the older polling approach.
