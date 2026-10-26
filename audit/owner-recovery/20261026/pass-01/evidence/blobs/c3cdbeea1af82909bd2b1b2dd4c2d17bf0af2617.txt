# Live Research Lab UX Vision — isolated implementation

Branch target: `builder/live-lab-ux-vision-20261014`.

This directory is a **presentation/runtime shell only**. It is intentionally isolated from the production Site, worker ingress, authentication, lease semantics, scientific `CONTROL`/`STATE`, economic methods/results, and the parallel platform-capability probe branch.

## Safety state

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
LIVE_E2E_PASS = NOT_CLAIMED
DEPLOYMENT = NOT_PERFORMED
```

All supplied scenarios are visibly marked `DEVELOPMENT/REPLAY`. Their tasks, evidence references, metrics and decisions are synthetic UX fixtures and are **not research or economic evidence**.

## Architecture

The scene has one direction of authority:

```text
canonical worker event
        |
        v
LiveEventAdapter + protocol-owned mapper
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

Development substitutes `FixtureReplayAdapter` at the adapter boundary. The renderer and state machine are unchanged.

`LiveEventAdapter` deliberately implements no polling, SSE/WebSocket selection, authentication, cursor, retry, lease, heartbeat cadence or reconnect policy. The proven platform protocol must own those semantics and inject a single `mapCanonicalEvent(canonicalEvent)` function. This prevents this UX branch from becoming a second competing live protocol.

## Truth rules

- A heartbeat updates presence time only. It cannot create or advance business animation.
- A stale lease or disconnect freezes business animation and raises a technical warning.
- `CONNECTED` and `SNAPSHOT` can restore factual state, but cannot restart business animation.
- Animation resumes only when a subsequent accepted semantic business event authorizes it.
- Duplicate IDs and out-of-order sequence numbers are ignored and cannot replay animation.
- `UNKNOWN` progress renders `Progress unknown`; no percentage is synthesized.
- `COMPLETED_COUNT_ONLY` renders only the completed count.
- `KNOWN_TOTAL` renders the explicit completed/total relationship.
- Only one worker can visually own the Economic Look machine at once.
- KILL/PARK/PROMOTE changes only on an exact `DECISION` event carrying that destination.
- Roles are materialized only after an accepted event/snapshot provides backing for that role.

## UX surface

Mobile Safari is the primary layout. The shell uses ordinary DOM/CSS (no canvas/WebGL or external assets), safe-area insets, Pointer Events, touch-action control, and a lightweight transform-only camera.

Implemented surfaces:

- global research floor with pan / pinch zoom / camera reset;
- event-backed Worker, Researcher/Scout, Builder, Data, Auditor/Red Team, Manager/Orchestrator stations;
- current task, step, progress mode, next action and last real action;
- idle, working, blocked and stale/frozen presentation;
- semantic activity visuals for source research, document reading, data qualification, coding/testing, Economic Look calculation, audit/red-team, commit/persistence, handoff, result and blocker;
- KILL / PARK / PROMOTE destinations;
- global Economic Look FREE / ACTIVE indicator and one-owner visual lock;
- recent-result wall and synthetic economic-result cards;
- character tap bottom sheet with replay-day / last-hour history and evidence references;
- explicit stale/resync technical warnings.

## Deterministic fixture scenarios

1. Researcher source investigation → handoff.
2. Builder coding/testing → commit/result.
3. Auditor red-team → PARK.
4. Economic Look → PROMOTE.
5. Worker becomes BLOCKED.
6. Heartbeat/lease becomes stale and freezes activity.
7. Disconnect → reconnect → snapshot/resync without fake animation restart.
8. Two documentary agents concurrently while exactly one Economic Look is active.

The UI never advances these scenarios on a business timer. A user explicitly applies the next event or remaining fixture events.

## Tests

From this directory:

```bash
npm test
```

The suite uses only Node's built-in test runner and has no package dependencies. It covers the requested negative/failure invariants as well as the replay scenarios.

## Binding boundary

The implementation is **ready to bind structurally** to the proven live protocol without rewriting the scene. Production integration must stop at the adapter until the platform-probe owner supplies the canonical contract/mapper and live-stream authority.
