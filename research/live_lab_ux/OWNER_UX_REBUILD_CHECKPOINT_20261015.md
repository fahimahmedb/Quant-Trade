# OWNER UX REBUILD CHECKPOINT — 2026-10-15

Status: isolated visual rebuild checkpoint for Codex handoff.

Branch: `builder/live-lab-owner-ux-rebuild-20261015`
Base: `builder/live-lab-3d-full-build-20261015` at `6076774f52ca2e619caaab57fb6a278f47608349`

## Owner calibration locked

UX3 code: `UX3-LUEKkkChgA`
UX4 code: `UX4-DkkiQkhZhkA`

Canonical visual target:
- living architectural diorama, not a dashboard with 3D in it;
- large hybrid monumental operations floor;
- deep cinematic opening camera;
- night blue + controlled amber lighting;
- adult premium humanoid research agents;
- discreet futuristic workstations;
- vertical scientific/energy column as central core;
- floating-corner HUD, center of viewport reserved for the world;
- mobile-first immersive scene;
- real semantic event -> authorized business animation only;
- subtle ambient physical motion may continue when idle, but no fake research/business activity;
- important real worker transitions may receive cinematic camera follow;
- fallback must preserve the same art direction;
- production replacement requires Owner visual approval first.

## Work already executed in this checkpoint

A standalone WebGL visual prototype was built and exercised locally under `/mnt/data/quanttrade-rebuild/ux2/` with:
- `preview.html`
- `preview.css`
- `preview.js`

Representative captures were produced locally:
- `A_idle.png` — connected idle laboratory
- `B_active.png` — one worker active
- `C_selected.png` — selected worker / camera focus
- `D_economic.png` — Economic Look active
- `E_iphone.png` — iPhone portrait composition

The prototype intentionally focuses on the canonical new visual language and does not replace the production Site yet.

## Truth / platform invariants to preserve

Do NOT replace the working native live path:

`native worker event -> authenticated ingress -> store -> SSE -> LiveEventAdapter -> canonical mapper -> reducer -> factual state -> animation authority`

Do NOT replace it with GitHub polling.

Do NOT infer:
- Codex/Owner/Researcher/Builder/Auditor/Manager role identity;
- progress percentages;
- economic results;
- research decisions;
- Economic Look ownership;
- business activity from heartbeat, reconnect, snapshot, or elapsed time.

Heartbeat = presence only.
CONNECTED/SNAPSHOT = factual state reconstruction only.
Duplicate/replayed events must not restart animation.
Unknown progress remains UNKNOWN.
KILL/PARK/PROMOTE only from explicit reducer-backed decisions.

Governance invariants:
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- `paid_usd_total = 0`

## Codex next mission

Continue from this branch and this checkpoint. Do not restart UX discovery and do not reopen the Owner calibration questionnaires.

1. Read the current `research/live_lab_ux` implementation and native event/reducer contracts.
2. Port the new visual prototype into the real Live Lab, replacing the poor current visual scene while preserving transport/reducer truth semantics.
3. Keep the production Site untouched until visual approval.
4. Preserve or strengthen tests proving heartbeat/reconnect/snapshot cannot fabricate work.
5. Build the five canonical review states:
   - idle
   - one worker active
   - worker selected / camera focus
   - Economic Look active
   - iPhone portrait
6. Produce fresh visual captures from the integrated build.
7. Stop for Owner visual review before production deployment.

## Quality gate

Do not declare success merely because CI passes or WebGL initializes. The integrated build must visually read as:

> A living architectural diorama where real research work becomes visible.

Failure modes to reject:
- empty/cheap room;
- generic WebGL primitives;
- crypto/hacker aesthetic;
- dashboard-first composition;
- toy-like workers;
- giant permanent cards/title/paragraphs;
- visually flat architecture;
- fake activity.

## Current publication decision

`PRODUCTION_REPLACEMENT_AUTHORIZED = FALSE`

Reason: Owner visual approval is required after integrated representative captures.
