# Quant — Live Research Lab · Owner revision 2026-10-16

[Integrated visual review](docs/VISUAL_REVIEW.md) · [Gallery A–F](review/index.html) · [Frozen constitution](docs/CANONICAL_UX_CONSTITUTION.md) · [Checkpoints](docs/REBUILD_20261016.md)

The Owner rejected the previous sparse candidate. This revision replaces it with a differentiated architectural research hall: double-height library, mezzanine, bridge, stepped terraces, glazed validation room, evidence pod, engineering alcove, archives, seminar tiers and integration table around the scientific column. Local PBR surfaces, beveled furniture/tools and a tailored adult humanoid replace the previous generic visual kit. Asset sources are credited in `assets/ASSET_CREDITS.md`.

## Local review

```sh
cd research/live_lab_ux
python3 -m http.server 4173
```

- `live.html`: existing same-origin native SSE → mapper → reducer → shared renderer.
- `index.html`: isolated, visibly synthetic review/replay; `?case=idle|active|selected|economic`. Original eight replay scenarios remain available.
- `review/index.html`: committed integrated captures and provenance.

Runtime dependencies/assets are local; no CDN, paid API or generated business data. To rebuild the MIT Three.js vendor bundle: `npm ci && npm run vendor`.

## Interaction and truth

Full-viewport world, maximum three normal corner facts. Drag/orbit, bounded navigation, wheel/pinch zoom, Shift/right-drag pan and canonical reset. Tap worker → actual station camera focus → short context after a focused frame paints → optional factual details.

Existing native adapters/mapper/SSE/reducer are unchanged by this revision. Heartbeat, connection, resync and duplicates never authorize work. Unknown progress stays unknown. Only explicit reducer-backed supported activity selects a gesture. Core motion requires the explicit Economic Look slot, an authorized worker and current transport. Structural zone names are not live role assignments. Screens show architectural schematics marked NON-DATA. No unsupported travel or inferred research roles.

Rendering batches static geometry, sleeps when idle and uses a nonblocking GPU fence to bound pending frames. Camera timing follows real elapsed time; gesture deltas stay bounded. Reduced motion suppresses repetitive motion/easing. The illustrated fallback uses a new empty capture of this exact hall and CPU projection of the same articulated adults. It supports pan/zoom/focus rather than perspective orbit or WebGL lighting, and skips building/loading the 3D environment.

```text
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
paid_usd_total = 0
PRODUCTION_REPLACEMENT_AUTHORIZED = FALSE
VISUAL_REVIEW_REQUIRED = TRUE
```

## Verification/reproduction

```sh
npm ci
npm test
npm run capture
python3 tools/prepare-review.py
npm run qa:browser
python3 tools/prepare-review.py
```

Capture/QA requires Chromium (`CHROMIUM_PATH`, default `/usr/bin/chromium`); packaging requires Python Pillow. `LAB_REVIEW_URL` defaults to `http://127.0.0.1:4173`. A/B/C/E use the real live entry and mapper with a browser-only EventSource mock. D uses an explicit normalized Economic Look fixture because native protocol does not supply it. Captures are synthetic, not evidence of real research.

41 Node tests cover native ordering/generation, snapshots, replay guards, progress, decisions, core/gesture authority and neck articulation. Browser results are stored with captures. Portrait is 393×852 Chromium touch emulation; real iPhone/Safari performance is unverified. The unrelated global SEC gate retains its existing STATE.md test-inventory freshness failure; no governance data is rewritten.

No Site is created, connected or deployed. Owner visual approval of the new integrated captures is required before production replacement.
