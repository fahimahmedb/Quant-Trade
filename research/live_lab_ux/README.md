# Live Research Lab — native events + WebGL 3D floor

Build branch: `builder/live-lab-3d-full-build-20261015`  
Baseline: `fdfee2006869ff3770f752f32fb672da0b0fc4ac`

This build keeps the proved native Live Lab event architecture and replaces the primary spatial visualization with a real dependency-free WebGL research floor. The previous DOM/CSS Research Floor remains the automatic fallback when WebGL is unavailable.

## Safety state

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
```

Nothing in the renderer authorizes capital, trading, research conclusions, economic decisions, worker identity or progress.

## Canonical authority path

```text
native Site SSE / deterministic replay
              |
              v
        existing adapters
              |
              v
      normalized UI event
              |
              v
       reduceScene()
 factual state + animation authorization
              |
              v
       scene3d-policy.js
              |
              v
   WebGL 3D floor + DOM factual overlays
```

The 3D layer consumes the existing factual state. It does not poll GitHub, create timers for business progress, synthesize roles, or infer economic meaning.

## Two surfaces

- `index.html`: synthetic `DEVELOPMENT/REPLAY` harness. Richer roles and Economic Look cases are explicitly fixtures, never evidence.
- `live.html`: native browser surface using same-origin `/api/work/events` through `EventSource`, `LiveEventAdapter`, the canonical native mapper and `reduceScene()`.

Both surfaces now share `ui/scene3d.js` and `ui/scene3d-policy.js`.

## 3D floor

The renderer uses browser WebGL directly and adds no runtime dependency. It includes procedural floor geometry, stations, avatars, lighting/fog, camera orbit/pinch/zoom, touch selection, mobile DPR limits, reduced-motion behavior and activity-specific visual states.

Architecture nodes such as **Quant / Mechanisms**, **Fundamental / Events**, **Flows / Regulatory**, **Validator / Red Team**, **Economic Identity**, **Portfolio Map**, **Forward Farm** and **Decay Monitor** are structural room labels only. They are not displayed as active workers without event-backed state.

The old DOM/CSS scene remains available as fallback. HUD, result wall, detail sheet and safety strip remain DOM so factual text stays legible and accessible.

## Truth rules preserved

- heartbeat updates presence only;
- disconnect/stale freezes business animation;
- `CONNECTED` and `SNAPSHOT` do not restart business animation;
- snapshot replay guards still suppress duplicate/already-represented native events;
- unknown/completed-count-only progress never becomes a fabricated ratio;
- destinations require exact reducer state;
- native workers remain generic `Worker` unless a future proved contract supplies stronger semantics;
- Economic Look lights only when factual state has an explicit active worker.

Event-derived task/step strings are HTML-escaped in the 3D visual policy before overlay markup is rendered.

## Tests

```bash
cd research/live_lab_ux
node --test tests/*.test.js
```

`.github/workflows/live-lab-3d-ci.yml` runs the full isolated suite, syntax-checks JavaScript modules and verifies the replay/live 3D integration boundaries.

## Publication boundary

This branch is a build artifact, not a production deployment. The exact existing Site project remains `appgprj_6aca43cb86bc81918e067097356a37de`, slug `quant-trade-lab`. No replacement project or host is created by this branch. Public deployment and the native-ingress → SSE → `live.html` E2E canary require the Site project controls that were not exposed to the GitHub-only build runtime.
