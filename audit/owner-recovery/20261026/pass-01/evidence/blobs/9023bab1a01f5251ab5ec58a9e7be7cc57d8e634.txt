# Live Research Lab — Oracle Integration Continuation

Date: 2026-10-20
Branch: `builder/live-lab-oracle-integration-20261020`
Historical base: `builder/live-lab-owner-ux-rebuild-20261015` at `8583ea6e46b123e831e8af489ad1043b810a0cf4`
Status: ACTIVE

## Owner priority

Execute in this order:

1. Live Lab desktop / real Oracle integration.
2. Desktop factual and visual qualification.
3. Safari / iPhone / mobile qualification and repair.

Do not treat Safari/mobile as a substitute for fixing the core Live Lab first.

## Proven historical state

The 2026-10-16 production continuation records a successful public Site deployment with the native transport path preserved and a real benign canary traversing authenticated session/generation/lease -> D1 -> public SSE -> mapper/reducer -> visible worker state.

The same production record explicitly leaves genuine Oracle/scheduled emitter identity and real Safari hardware performance unverified/unsupported.

The 2026-10-17 Oracle route defines the intended integration:

`Oracle controller -> authenticated Site events -> D1 -> SSE -> LiveEventAdapter -> mapper -> reducer -> scene`

It also records that a dedicated Oracle production principal/ingress, an explicit hypothesis-generation activity, and an effective Owner command journal were still required at that point.

Since that audit, Oracle V1 has become a real autonomous runtime. The UI workstream must therefore consume real Oracle semantics rather than preserve the historical probe-only worldview.

## Truth invariants

- Site live state is a projection, never canonical scientific authority.
- Do not replace the native Site/D1/SSE path with GitHub polling.
- Heartbeat = presence only.
- Snapshot/reconnect = reconstruction only; never business motion authority.
- Duplicate/replayed events do not restart animation.
- Unknown progress remains UNKNOWN.
- No inferred Owner/Codex/research role identity.
- Oracle identity/activity must be explicit in the authenticated event contract, not guessed from worker IDs.
- Economic Look remains idle unless explicitly supported by the native contract.
- `REAL_CAPITAL_AUTHORIZED = FALSE`.
- `LIVE_TRADING_AUTHORIZED = FALSE`.

## Work package L1 — Oracle-native frontend contract — CLOSED PASS

- [x] Added explicit `hypothesis-generation` activity to the canonical UI model.
- [x] Bound it to a truthful existing non-economic comparison gesture family.
- [x] Explicit `ui_role` / `ui_label` metadata is accepted only when supplied and allowlisted; worker IDs never create identity.
- [x] Unsupported/malformed identity/activity values fail closed to generic worker/no activity.
- [x] Regression tests prove heartbeat/snapshot/reconnect cannot fabricate or replay Oracle work.
- [x] Representative Oracle event fixtures cover active, reconstructed, heartbeat and later-semantic-event behavior.
- [x] Added a bounded Oracle ingress-packet contract matching the proven historical native packet shape; it deliberately leaves the production ingress endpoint UNBOUND until a Site principal is actually deployed.
- [x] Completion packets require a durable output SHA-256 + exit code proof and forbid outcome-like UI fields.
- [x] Corrected the previous misleading `mobileSafari:true` capability to `UNVERIFIED_REAL_DEVICE`.

Exact-head client qualification before this checkpoint: `96b674fb23345a61cfad91438c1aebf4c147d761`.
Live Lab CI run `39357493478`: SUCCESS.
Earlier Oracle semantics CI run `39357269096`: SUCCESS.

L1 does **not** claim Oracle -> Site production ingress exists. It qualifies the frontend/native contract only.

## Work package L2 — Desktop Live Lab integration — ACTIVE

- [ ] Audit the current desktop composition against the locked UX3/UX4 constitution.
- [ ] Remove stale probe/demo framing from the live path where it can mislead the Owner.
- [ ] Make connection/idle/active/stale states legible without dashboard-first UI.
- [ ] Preserve center-of-world architectural composition and factual corner HUD.
- [ ] Keep fallback art direction coherent with WebGL.
- [ ] Re-run Node tests and browser QA.
- [ ] Produce integrated desktop review captures.

## Work package L3 — Real Oracle -> Site transport

This package may require the Site runtime/source and credentials that are not stored in this GitHub repository.

Required proof, not assumption:

- [ ] dedicated Oracle production principal;
- [ ] ingress accepts explicit Oracle semantic metadata;
- [ ] authenticated sequence/generation/lease behavior;
- [ ] heartbeat loop independent of long inference;
- [ ] start only after real work starts;
- [ ] completion only after durable verifiable result;
- [ ] D1 persistence;
- [ ] SSE visibility;
- [ ] mapper/reducer/animation receipt;
- [ ] no duplicate animation after replay/reconnect;
- [ ] no fabricated progress/economic result.

If the Site runtime cannot be mutated with available tools, stop only at that external boundary with one exact Owner/Work-mode action package; do not relabel frontend preparation as end-to-end integration.

## Work package L4 — Safari/iPhone/mobile (only after L1-L3 desktop truth path is qualified)

Historical browser evidence is Chromium touch/portrait emulation only and does not certify Safari.

Required Safari pass:

- [ ] real WebKit/Safari compatibility review;
- [ ] viewport and safe-area behavior;
- [ ] `100vh`/dynamic viewport handling;
- [ ] touch orbit/pan/pinch arbitration;
- [ ] scroll/overscroll prevention without trapping accessibility;
- [ ] bfcache restore/rebind;
- [ ] WebGL/WebGL2 capability/fallback behavior;
- [ ] memory/GPU pressure and context loss;
- [ ] device-pixel-ratio ceiling;
- [ ] reduced motion;
- [ ] portrait/landscape rotation;
- [ ] text/control hit targets;
- [ ] real iPhone/Safari proof when a physical/device-browser surface is available.

Do not mark real Safari hardware PASS from Chromium emulation.

## Definition of done

Phase 1 can be called `LIVE_LAB_ORACLE_DESKTOP_QUALIFIED` only when the desktop client is connected to an authenticated Oracle semantic path and representative live states are verified without inferred activity.

Phase 2 can be called `LIVE_LAB_SAFARI_MOBILE_QUALIFIED` only with Safari/WebKit evidence appropriate to the claim. Chromium portrait alone is insufficient.
