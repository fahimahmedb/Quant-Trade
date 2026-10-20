# Oracle V2 -> Live Lab bridge reconciliation — 2026-10-20

Status: `BRIDGE_RECONCILED_WITH_LIVE_V2 / SITE_PREFIX_AND_SECRET_ACTIVATION_PENDING`

## Reconciliation result

The previously CI-qualified Oracle V2 -> Live Lab bridge was reconciled non-destructively onto the then-current autonomous Oracle V2 state.

Reconciliation merge commit:

`d4afbdce65795a712dd9b7a15944aa34099088b3`

First parent — live Oracle V2 state at reconciliation:

`777d1a726a0dfa21008dfb63078ccc8d00a2507d`

Second parent — previously qualified bridge checkpoint:

`de9f1c2de0e278e0a3cb9b9c63ca2912fe88f936`

The merge tree used the exact live V2 tree as the base and overlaid only the audited bridge surfaces:

- `research/research_os/live_lab_contract.py`
- `research/research_os/live_lab_bridge.py`
- `research/research_os/live_lab_emitter.py`
- `research/research_os/oracle_worker_v2_live.py`
- `deploy/systemd/quant-live-lab-emitter-v2.service`
- `deploy/systemd/quant-research-worker-v2.service`
- `deploy/oracle_live_lab_bridge_install.py`
- `tests/test_oracle_v2_live_lab_bridge.py`
- `.github/workflows/oracle-v2-live-lab-bridge-ci.yml`
- prior bridge checkpoint documentation

No autonomous V2 durable task/event/receipt state was rewritten or dropped.

## Scientific/runtime invariant

The bridge remains observational and subordinate to GitHub durable scientific state.

Architecture:

`Oracle V2 scientific commit -> local outbox -> separate authenticated emitter -> existing Site ingress -> D1 -> SSE -> factual UI`

The Site cannot grant scientific/economic authority and Site delivery failure cannot invalidate a successful Research OS commit.

## Current exact production blocker

The factual V2 worker identity is:

`oracle-research-v2.<lane>`

The existing Site ingress was previously reported/configured to allow:

`oracle-research.`

The bridge intentionally refuses to rewrite the V2 identity.

Therefore production activation remains blocked until the EXISTING Site explicitly accepts:

`oracle-research-v2.`

for the dedicated principal:

`oracle-research-live`

No replacement Site/project is allowed.

## Existing Site target

- URL: `https://quant-trade-lab.sassylime.chatgpt.site`
- project id: `appgprj_6aca43cb86bc81918e067097356a37de`
- plugin id: `plugin_asdk_app_sites_e8d68311a5ec81919956b109c24876dd`
- reported Site state from Work handoff: v25 / environment rev.10 / authenticated ingress + D1->SSE canary / 97 tests

The current Chat connector can inspect the Sites-backed plugin envelope/read-only app tools but does NOT expose the Site source/admin/secret MCP surface. Consequently this checkpoint does not claim the prefix or secret has been changed.

## Secret boundary

Never put the ingress key in GitHub or chat.

Only the separate emitter service may read the secret from:

`/etc/quant-research/worker.env`

Required values:

- `QT_ORACLE_SITE_BASE_URL=https://quant-trade-lab.sassylime.chatgpt.site`
- `QT_ORACLE_PRINCIPAL=oracle-research-live`
- `QT_ORACLE_SITE_WORKER_PREFIX=oracle-research-v2.`
- `QT_ORACLE_INGRESS_KEY=<out-of-band secret>`

The installer requires root ownership, group `quant-research`, and mode `0640`.

## Next legitimate production sequence

1. In the existing Site admin/source, extend the authenticated Oracle allowlist to exact prefix `oracle-research-v2.` without weakening authentication.
2. Keep/rotate the ingress key only in Site secret storage; do not expose it in chat or Git.
3. Provision the same key out-of-band into `/etc/quant-research/worker.env` with the exact four values and permissions.
4. Qualify/build the exact reconciled bridge release according to Oracle V2 exact-release discipline.
5. Run `deploy/oracle_live_lab_bridge_install.py --release-sha <exact-sha> --enable` as root.
6. Observe a natural V2 wake.
7. Prove end-to-end: authoritative Research OS commit -> local outbox -> authenticated Site acceptance -> D1 -> `/api/work/events` SSE -> factual UI -> completion -> reload without replay.
8. Only then set `REAL_ORACLE_V2_SITE_CONNECTION = PASS`.

## Authority

Remain FALSE:

- `ECONOMIC_EXPERIMENT_AUTHORIZED`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED`
- `REAL_CAPITAL_AUTHORIZED`
- `LIVE_TRADING_AUTHORIZED`

This reconciliation changes none of them.
