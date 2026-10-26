# Oracle V2 -> Live Lab bridge checkpoint — 2026-10-20

Status: `CODE_AND_CI_QUALIFIED / PRODUCTION_SITE_IDENTITY_ACCEPTANCE_PENDING`

This checkpoint records the isolated bridge built from the live Oracle V2 lineage without mutating the autonomous V2 writer.

## Source lineage

Integration branch:

`builder/oracle-v2-live-lab-bridge-20261020`

Base live V2 SHA at branch creation:

`4b44644845ff4ce56b08d808c2222fdac0202555`

Observed subsequent live V2 state-only commit:

`baa460a85efc9bae0cc1ef58e29557f86663f644`

The later commit is a canonical queue refill and changes durable Research OS state, not the bridge/code surfaces. The bridge branch is therefore intentionally isolated rather than force-updated over the autonomous writer.

## Existing Site identity

Existing Site only; no replacement project was created.

- Site: `https://quant-trade-lab.sassylime.chatgpt.site`
- Sites-backed private plugin id: `plugin_asdk_app_sites_e8d68311a5ec81919956b109c24876dd`
- plugin current release observed during this checkpoint: `PluginRelease_d007eb4422d081918efaaa1f3a08abb4`

The Site v25 / environment revision 10 / 97-test production-canary claims were supplied by the immediately preceding Work handoff. This checkpoint does not upgrade those reported facts into a fresh host-side Site-admin proof because the current Chat connector exposes only the Sites-backed plugin package/read-only app tools, not the Site source/admin/secret surface.

## Bridge architecture

`Oracle V2 scientific commit -> local non-authoritative outbox -> independent authenticated emitter -> existing Site ingress -> D1 -> SSE -> factual UI`

Scientific truth remains GitHub durable state.

The Site:

- cannot create research work;
- cannot grant economic/prospective/capital/live authority;
- cannot make a failed Site delivery invalidate a successful Research OS commit;
- receives no fabricated progress or business state.

## Implemented files

- `research/research_os/live_lab_contract.py`
- `research/research_os/live_lab_bridge.py`
- `research/research_os/live_lab_emitter.py`
- `research/research_os/oracle_worker_v2_live.py`
- `deploy/systemd/quant-live-lab-emitter-v2.service`
- updated `deploy/systemd/quant-research-worker-v2.service`
- `deploy/oracle_live_lab_bridge_install.py`
- `tests/test_oracle_v2_live_lab_bridge.py`
- `.github/workflows/oracle-v2-live-lab-bridge-ci.yml`

## Secret isolation

The scientific worker service does NOT load the Site secret.

Only the separate emitter service reads:

`/etc/quant-research/worker.env`

Required environment names:

- `QT_ORACLE_SITE_BASE_URL`
- `QT_ORACLE_INGRESS_KEY`
- `QT_ORACLE_PRINCIPAL`
- `QT_ORACLE_SITE_WORKER_PREFIX`

The secret value is neither stored in Git nor printed by the installer/emitter.

The installer requires the secret file to be:

- regular, not symlink;
- owner root;
- group `quant-research`;
- mode `0640`.

## Canonical destination

Pinned Site origin:

`https://quant-trade-lab.sassylime.chatgpt.site`

Pinned ingress routes:

- `POST /api/oracle/session`
- `POST /api/oracle/event`

Pinned principal:

`oracle-research-live`

## Critical identity finding

The actual live V2 worker identity is factual and must not be rewritten:

`oracle-research-v2.<lane>`

For example, current durable V2 artifacts contain:

`oracle-research-v2.fundamental_events`

The historical Site handoff expected worker prefix:

`oracle-research.`

Therefore production delivery MUST remain blocked until the existing Site ingress is explicitly proven to accept:

`oracle-research-v2.`

or an equivalent explicit allowlist that includes the exact V2 identity.

The bridge deliberately tests this mismatch and refuses to hide it by aliasing the worker id.

## CI proof

Workflow:

`Oracle V2 Live Lab Bridge`

Run:

`39418667831`

Head SHA:

`c74d7486ebcf0a3fdca1ebf904df1c14158d91d1`

Result:

`SUCCESS`

Passed stages include:

- compile bridge and V2 entrypoints;
- bridge invariants and V2 regression tests;
- secret isolation and Site pinning;
- no literal ingress secret committed;
- systemd unit verification.

This is code/CI qualification only. It is not a real Oracle->Site wake proof.

## Production state

`BRIDGE_CODE_QUALIFIED = TRUE`

`SITE_V25_REPORTED_READY = TRUE`

`SITE_V2_WORKER_PREFIX_ACCEPTANCE_PROVEN = FALSE`

`VM_ROTATED_SITE_SECRET_INSTALLED_PROVEN = FALSE`

`EMITTER_ENABLED_ON_ORACLE_VM = FALSE / NOT_PROVEN`

`REAL_ORACLE_V2_EVENT_ACCEPTED_BY_SITE = FALSE / NOT_PROVEN`

`D1_TO_SSE_REAL_V2_EVENT_PROVEN = FALSE`

## Hard authorities

Remain FALSE:

- `ECONOMIC_EXPERIMENT_AUTHORIZED`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED`
- `REAL_CAPITAL_AUTHORIZED`
- `LIVE_TRADING_AUTHORIZED`

The bridge cannot change these values.

## Exact next legitimate sequence

1. On the existing Site, expand/replace the Oracle worker allowlist so the authenticated `oracle-research-live` principal accepts exact worker prefix `oracle-research-v2.`. Do not create a new Site and do not weaken authentication.
2. Preserve/rotate the Site ingress key through Site secret storage; never copy it into Git or chat.
3. Provision the same key out-of-band into `/etc/quant-research/worker.env` with exact permissions and the four required env variables.
4. Rebase/reconcile this bridge code onto the freshest V2 code state without overwriting autonomous durable Research OS state.
5. Build/install an exact-SHA V2 release containing the bridge and re-run the existing V2 qualification gates required by the runtime release discipline.
6. Run `deploy/oracle_live_lab_bridge_install.py --release-sha <exact-sha> --enable` as root.
7. Observe one natural real V2 wake.
8. Prove the exact event chain: Research OS commit -> outbox -> authenticated Site ingress -> D1 accepted event -> `/api/work/events` SSE -> mapper/reducer -> factual UI -> completion -> reload without replay.
9. Only then classify `REAL_ORACLE_V2_SITE_CONNECTION = PASS`.

No step above authorizes economic outcome access or capital use.
