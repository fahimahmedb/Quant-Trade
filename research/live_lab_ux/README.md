# Quant — Live Research Lab · integrated owner rebuild

Branch: `builder/live-lab-owner-ux-rebuild-20261015`
Owner starting checkpoint: `d37c50b145ca7a97628e01078999b2a2b6e43841`
Calibration: UX3 `UX3-LUEKkkChgA`, UX4 `UX4-DkkiQkhZhkA`.

[Canonical constitution](docs/CANONICAL_UX_CONSTITUTION.md) · [Integration checkpoints](docs/INTEGRATION_CHECKPOINT.md)

## Run locally

```sh
cd research/live_lab_ux
python3 -m http.server 4173
```

- `live.html`: existing same-origin native EventSource transport, mapper, reducer and integrated architectural renderer.
- `index.html`: explicitly synthetic review/replay, no SSE or ingress. Review cases: `?case=idle`, `active`, `selected`, `economic`; original eight truth scenarios remain selectable.
- `review/index.html`: committed integrated A–E captures after capture packaging.

Runtime dependencies are vendored locally, including the Three.js MIT license. No runtime CDN, paid API or generated research data. To reproduce the vendor bundle: `npm ci && npm run vendor`.

## Integrated world

The owner's retained `owner_rebuild_preview/` is the visual starting point, preserved unchanged. Its operations ring, raised areas, back elevation, containment column, stations, low camera and corner HUD are refactored into the real renderer. The scene adds eleven physical functional zones, a curved terrace and mezzanine, access stairs, arched trusses, mixed mineral/metal/glass/timber/textile, practical warm lights and articulated seated adult humanoids.

The world fills the viewport. Three factual corner signals remain: transport, last business event (UTC), Economic Look. Worker selection approaches the station; context appears after focus settles; factual details are a separate optional dialog. Desktop orbit, wheel zoom, Shift/right-drag bounded pan, touch orbit/pinch and reset are supported. No travel is inferred from native events without a destination contract.

The fallback uses an empty architectural illustration captured from this exact 3D scene, with the same adult meshes projected/shaded on CPU. It supports pan/zoom and worker approach. Fallback cannot provide full perspective orbit or the WebGL material/lighting model. It does not substitute a dashboard or prepaint active workers.

## Truth architecture

```text
native worker event → authenticated ingress → store → SSE
→ LiveEventAdapter → platform-native mapper → reduceScene
→ factual visual policy → motion-authority → shared renderer
```

Ingress/store are outside this visual subtree and are untouched. Native adapters and SSE binding are unchanged. One reducer hardening freezes every prior worker animation before snapshot application, including workers omitted by an empty/partial snapshot. This prevents a later event on another worker reviving an old gesture.

Heartbeat is presence only. Connection, snapshots, reconnect and duplicates cannot authorize work. Unknown progress remains unknown. Unsupported activities, results, commits and blockers do not implicitly become reading/typing/calculation. Explicit supported activity chooses a gesture family. Economic core motion requires the explicit slot, an authorized worker and current transport; stale/resync stays dim. Reduced motion removes repetitive motion and camera easing. Idle rendering sleeps; static architecture is batched.

Structural zone names do not identify live roles or prove research work. Native workers remain generic `Worker` unless the proved mapper supplies another explicit contract. Screens show `SYSTEM GEOMETRY · NON-DATA` and station availability; there are no invented financial charts, outcomes or progress.

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
PRODUCTION_REPLACEMENT_AUTHORIZED = FALSE
VISUAL_REVIEW_REQUIRED = TRUE
```

## Validation and capture reproduction

```sh
npm ci
npm test
npm run capture
# Convert generated assets/*.png to same-name WebP before testing fallback.
npm run qa:browser
```

`CHROMIUM_PATH` can select a compatible Chromium installation. `LAB_REVIEW_URL` defaults to `http://127.0.0.1:4173`. Browser capture/QA mocks EventSource only inside isolated browser pages; it never sends an ingress event or alters a production store. A/B/C/E use `live.html` through the native mapper. D uses an explicit reducer fixture in `index.html`, because the current native protocol does not support Economic Look. Every capture is visibly synthetic, not evidence of live research.

The isolated Node suite covers native events, ordering/generation, snapshots, replay guards, progress, decisions and core/gesture authority. Browser QA additionally covers native view integration, focus/details and forced no-WebGL fallback. iPhone composition uses 393×852 Chromium touch emulation; real iPhone/Safari performance is not certified.

No Site is created, connected, deployed or replaced. Existing production remains untouched. Owner visual review of the integrated captures is the next gate; CI does not approve the art direction.
