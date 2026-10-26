# Work handoff — existing Quant-Trade Live Lab Site

Date: 2026-10-20

## Exact target

Modify the EXISTING ChatGPT Site only:

- project_id: `appgprj_6aca43cb86bc81918e067097356a37de`
- slug: `quant-trade-lab`
- live URL: `https://quant-trade-lab.sassylime.chatgpt.site`

Do NOT create a replacement project, change the slug, change hosting provider, wipe D1, or discard existing native SSE/history.

Before editing, capture the current Site source version, deployment/environment revision, access mode, worker source files and D1 bindings so rollback is possible.

## GitHub source of truth for this integration

Repository: `fahimahmedb/Quant-Trade`
Branch: `builder/live-lab-oracle-canonical-20261020`

Always fetch the fresh branch HEAD before acting. The minimum known integration HEAD when this handoff was written is:

`362b773690728b5881ced1d4b240510f333db675`

The branch is based on the qualified Oracle Research OS and contains the transplanted/validated Live Lab UX plus the truth-preserving Oracle UI contract.

Key files:

- `research/research_os/live_lab_contract.py`
- `research/research_os/oracle_live_worker.py`
- `research/live_lab_ux/adapters/platform-native.js`
- `research/live_lab_ux/adapters/platform-native-sse.js`
- `research/live_lab_ux/core/state-machine.js`
- `research/live_lab_ux/ui/motion-authority.js`
- `research/live_lab_ux/tests/oracle-live-contract.test.js`
- `research/live_lab_ux/ORACLE_INTEGRATION_CHECKPOINT_20261020.md`

## Existing production facts to preserve

Historical production repair already proved:

- canonical public SSE route: `GET /api/work/events`
- canonical snapshot route: `GET /api/work/snapshot`
- D1-backed session/event history
- duplicate events are ignored idempotently
- heartbeat is presence only
- reconnect/snapshot cannot restart business animation
- accepted ACTION_STARTED can drive the real reducer/DOM

Historical probe routes under `__platform_probe` are diagnostic surfaces only. They MUST NOT become the permanent Oracle integration by renaming or silently reusing them.

## Mission

Add a dedicated authenticated ingress for the real Oracle Research OS while preserving the existing canonical outbound stream:

`Oracle VM -> dedicated authenticated Site ingress -> D1 accepted event -> /api/work/events SSE -> LiveEventAdapter -> platform-native mapper -> reducer -> factual UI`

There must be NO GitHub polling loop in the Site and NO browser-side inference from GitHub task files.

GitHub remains canonical scientific state; Live Lab is only a projection of accepted runtime events.

## Dedicated Oracle principal

Create a dedicated Site-side worker principal/secret for Oracle. Do not reuse a temporary canary/probe key.

Preferred logical identity:

- principal: `oracle-research-live`
- allowed worker prefix: `oracle-research.`

The secret must remain in Site/VM secret storage only. Never write credentials to GitHub, Site source, screenshots, receipts, chat output, logs or D1 event payloads.

If the Site platform requires a different secret/principal mechanism, preserve the same security properties and report the exact mechanism used.

## Native Oracle ingress contract

Use a dedicated production route namespace such as:

- `POST /api/oracle/session`
- `POST /api/oracle/event`

Equivalent names are acceptable if the existing Site architecture has a clearly canonical location. Do not overload `__platform_probe`.

Ingress must accept only authenticated, bounded canonical Oracle event fields. Preserve these source fields when present:

- `event_id`
- `session_id`
- `worker_id`
- `action_id`
- `event_type`
- `event_seq`
- `generation`
- `emitted_at`
- `payload`

Site acceptance may add server facts such as:

- `accepted_at`
- monotonic/native `cursor`
- delivery token / server receipt metadata

Do not allow the client to forge server acceptance time/cursor.

## Truth rules

No Site code may infer business truth from worker naming, timing or appearance.

Explicit UI metadata may be propagated only when supplied by the Oracle contract and allowlisted by the existing mapper:

- `payload.ui_activity`
- `payload.ui_role`
- `payload.ui_label`

Unknown/invalid values fail closed to generic worker/no business gesture.

In particular:

- heartbeat NEVER authorizes business motion
- snapshot/reconnect NEVER authorizes business motion
- `hypothesis-generation` is a non-economic activity
- no event may infer or activate Economic Look unless an explicitly authorized economic event exists
- no percentage/progress may be fabricated
- role `owner` must not be inferred from worker id or label
- duplicate/out-of-order events must not replay animation

## Frozen authority invariants

These remain FALSE and Site work must not alter or visually contradict them:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

The Site is not allowed to grant or imply scientific/economic authority.

## Front-end source

Bring the deployed Live Lab runtime assets into alignment with the fresh GitHub integration branch rather than with the historical October 15 branch.

Do not blindly replace the backend worker source with GitHub files: the Site backend contains platform-specific D1/auth/runtime code that may not exist in the repo. Inspect and merge deliberately.

## Required tests before deployment

At minimum prove on the Site source/runtime:

1. unauthenticated Oracle ingress -> 401/403
2. wrong principal / wrong worker prefix -> rejected
3. valid session -> accepted with server-side generation/lease binding or equivalent bounded session binding
4. valid `ACTION_STARTED` with explicit Oracle UI metadata -> one D1 transition
5. exact duplicate `event_id` -> `DUPLICATE_IGNORED` (or equivalent), same canonical cursor/no second transition
6. heartbeat -> accepted presence only, no worker materialization or business animation
7. completion -> worker stops gesture
8. snapshot after reload -> reconstructs facts but does not replay motion
9. invalid `ui_role=owner` -> does not create Owner role
10. invalid/unsupported activity -> no business gesture
11. hypothesis-generation -> visible non-economic gesture only after genuine semantic start
12. public/native `/api/work/events` SSE continues to work
13. `/api/work/snapshot` remains factual
14. no credentials in source/receipts/logs
15. four authority invariants remain false

## Deployment gate

Do not claim completion from unit tests alone.

After deploying to the SAME existing Site, run a benign authenticated Site canary using the new dedicated Oracle ingress. It may use a synthetic non-economic worker identity for transport proof, but must use the production route and canonical mapper/reducer.

Required production proof chain:

`authenticated ingress accepted -> D1 row/event -> public/native SSE delivery -> mapper -> reducer -> factual active worker -> completion -> gesture stops -> reload snapshot does not replay`

Do not claim a REAL Oracle wake has been shown until a later event emitted by the actual Oracle VM is correlated end-to-end.

## Return to ChatGPT

Return a compact machine-checkable handoff containing:

- project_id / slug
- pre-change Site version + deployment/environment revision
- post-change Site version + deployment/environment revision
- changed backend files
- changed frontend files
- exact ingress routes
- exact auth/principal mechanism, WITHOUT secret value
- D1 schema/migration changes, if any
- test counts/results
- production canary event_id/session_id/generation/cursor
- proof that `/api/work/events` delivered it
- proof that completion stopped animation and reload did not replay it
- remaining blockers
- whether Safari/iPhone has actually been tested (do not infer this)

Stop and report a blocker instead of creating a new Site/project or weakening authentication/truth guards.