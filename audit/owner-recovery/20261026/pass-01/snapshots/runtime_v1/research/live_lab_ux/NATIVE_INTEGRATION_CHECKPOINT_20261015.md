# Native Live Lab integration checkpoint — 2026-10-15

## Provenance

- repository: `fahimahmedb/Quant-Trade`
- integration branch: `builder/live-lab-native-integration-20261015`
- platform-probe base: `809ec7e3d088a4ba4c5857771e6422ab91a139f4`
- isolated UX source tree: `901b06cbbccc1945bd50233eca7b6ec84934e586`
- UX import commit: `92244418f07f95a77379e31a83125f223a00b56a`
- implementation parent before this checkpoint: `3b9a6e129f22fe59e6d5d22445cef8fd41dfbece`

The UX branch was not merged wholesale. Only `research/live_lab_ux/` was grafted onto the proven platform checkpoint.

## Integrated path

```text
/api/work/events (proved native Site SSE)
  -> browser EventSource
  -> named snapshot / worker_event frames
  -> LiveEventAdapter
  -> platform-native mapper
  -> generation-scoped normalized UI events
  -> reduceScene factual state + replay guard
  -> deterministic DOM/CSS scene
```

Live entry point: `research/live_lab_ux/live.html`.
Replay entry point: `research/live_lab_ux/index.html`.

## Native facts accepted by the UI

Only the already-proved worker event types are mapped:

- `ACTION_STARTED`
- `ACTION_COMPLETED`
- `WORKER_HEARTBEAT`
- `SESSION_ENDED`

The mapper preserves worker/session/generation ordering. Progress is `UNKNOWN` unless a future proved contract explicitly supplies supported progress semantics. Heartbeat is presence-only.

## Falsification guard added

The Site SSE snapshot may already contain active events that are subsequently emitted again as SSE worker frames. Snapshot mapping now supplies:

- accepted event IDs already represented;
- max sequence watermark per `worker + session + generation` stream.

The reducer seeds those guards before subsequent frames. Replayed historical events therefore cannot masquerade as new live activity or restart animation. A genuinely later accepted sequence can resume animation.

## Validation performed in this integration session

Exact native mapper/reducer/SSE subset executed with Node built-in tests:

```text
11 tests
11 pass
0 fail
```

Covered:

- real probe-shaped `ACTION_STARTED`;
- no Codex/Owner inference;
- no progress/economic inference;
- explicit activity only;
- heartbeat presence only;
- generation reset ordering;
- duplicate suppression;
- unsupported event rejection;
- factual non-animating snapshot;
- snapshot replay suppression followed by genuine later event;
- thin EventSource framing and clean shutdown.

A full repository clone/CI run could not be executed from the local validation container because that container could not resolve `github.com`. This checkpoint does not mislabel the subset test as full CI.

## Safety / authority

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
LIVE_E2E_PASS = NOT_CLAIMED
DEPLOYMENT = NOT_PERFORMED
```

## Still not proved / not claimed

- authenticated Codex principal == Owner;
- fully remote Builder identity/authority;
- native APNs delivery guarantee;
- app-specific mobile reliability;
- exact third-party model route;
- production publication of this UX surface;
- richer semantic role mapping beyond protocol-backed `Worker`;
- live KILL/PARK/PROMOTE or Economic Look events from the current native worker contract.

Do not solve these unknowns by reviving GitHub polling as the primary live protocol or by fabricating UI activity. Continue from the native event architecture and add semantics only when the platform contract proves them.
