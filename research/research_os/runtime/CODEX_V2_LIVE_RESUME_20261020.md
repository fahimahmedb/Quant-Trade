# Resume here — Oracle V2 active, Site connection pending

Latest Owner steering: finish Oracle H24 and connect its real wakes to the
existing Site; use very few tokens. Owner then reported only 3% token budget.
Preserve this checkpoint and complete pending verification; never invent PASS.

## Actual Oracle core

- Repository `fahimahmedb/Quant-Trade`, mandatory active branch
  `builder/oracle-v2-core-20261020`. Always fetch fresh HEAD, preserve autonomous
  commits, never force/rewind/reset. GitHub is the only scientific authority.
- Native qualified core SHA `a67ffec48fff895d5edc42171855e2213e49cf0d`.
- Exact core CI PASS: V2 `39360664488`, SEC P0 `39360664487`.
- Owner successfully prepared this release; V1 rollback executable remains
  `f3943830e20b05d926d3013501573b8b21fdace7`.
- Owner repaired ONLY the fixed root wrapper PATH via exact script
  `d7ce4bc7d79e5f219660973c79d47859dc7f42e1`; native release bytes unchanged.
  Root controls now resolve `/usr/sbin/runuser`.
- Real eleven-gate V2 canary PASS, including local GPT-OSS reasoning, fresh
  GitHub reads, actual process exit75 after claim, durable ideation intent,
  90-second lease expiry/recovery, blocked structural duplicate, two receipts,
  terminal replay with no HEAD change, all four authorities false.
- Durable report already on GitHub:
  `artifacts/AAA-V2-CANARY-a67ffec48fff895d/live-qualification.json`
  under `research/research_os/`. Qualification commit `243019cf9dc76d8a6c2862a2bf65cf18bab90003`.
- Fixed root activation succeeded. V1 timer disabled/inactive; V2 timer and
  local model enabled/active. Fresh V1->V2 migration source
  `0837f419c4e3a9e17a39269994f27d97fcf79757`.
- Automatic V2 wake proved by systemd invocation
  `42bae378bebf4580a13f3ee0fe6df65d`, commit
  `1147c244643bac7a6ce2d3b1d581a6b824f6a7c5`, DERIVED_ONE_READY_TASK.
  Another natural wake then claimed/completed Legacy at `d4fe00c...`.
- Full preboot status is `v2_evidence/ORACLE_V2_PREBOOT_STATUS_20261020.json`.
  Read-only root status gate reports PASS for local model and scientific/V2
  preflight, no hosted model calls. Legacy/corpus are loaded fresh each wake.

## Reboot gate — DO NOT SEND A SECOND REBOOT

One graceful OCI SOFTRESET requested at `2026-10-20T11:13:12Z`, HTTP200.
Preboot ID `79a29c0f-c7cd-4cd2-885c-9e4c18e123b6`.
`v2_evidence/ORACLE_V2_REBOOT_REQUEST_20261020.json` preserves the request.
Need a different boot ID + enabled/active V2/model + real natural postboot wake,
durable GitHub commit/receipt, no duplicate science, all authorities false.
Only then issue the final V2 operational receipt; no economic qualification.

## Site — current truth

Owner explicitly authorizes completing the existing other-agent integration.
Existing project `appgprj_6aca43cb86bc81918e067097356a37de`, public URL
`https://quant-trade-lab.sassylime.chatgpt.site`. Do not recreate/edit/publish
the Site unnecessarily; its v25 production ingress already exists.

- Current Site version25, source `7afac2cbfde65bd08bf64c0a4d6cf0ee6b62397a`.
- Environment revision10. Dedicated secret `QT_ORACLE_INGRESS_KEY` is set
  ONLY on Site and unreadable/masked by the API. Owner explicitly says its value
  is inaccessible and a synchronized NEW rotation is necessary.
- NO key generated/rotated/transferred by this agent yet. NO Oracle->Site wake
  claimed. Do not put credentials in Git, output, logs or event payloads.
- Required principal `oracle-research-live`; allowed worker prefix
  `oracle-research.`. Current V2 actor `oracle-research-v2` does not satisfy that
  prefix; the optional projection's explicit runtime actor is `oracle-research`.
- Session POST `/api/oracle/session`: JSON principal, worker_id,
  native_session_id (canonical scientific session), trace_id. Server returns
  visual session_id, generation, lease_id, heartbeat_interval_ms (10s).
- Event POST `/api/oracle/event`: principal, event_id, trace_id, worker_id,
  server session_id/generation/lease_id, increasing visual event_seq, event_type,
  action_id, emitted_at, bounded payload. Header Authorization Bearer key.
- ACTION_COMPLETED requires `effect_proof.stdout_sha256` and actual exit_code.
- Payload permits ONLY stage,label,detail,ui_activity,ui_role,ui_label.
  No Economic Look/owner role. Heartbeat is presence, never business motion.
- Visual session/generation/sequence are separate from scientific queue/lease;
  bind both namespaces explicitly in observer receipts. Never change science
  for display. Never replay historical starts to create current animation.
- Public outputs `/api/work/snapshot`, `/api/work/events`; health `/health`.
- Native secret path requested by Owner: `/etc/quant-research/worker.env`,
  root:quant-research 0640. Variables key, QT_ORACLE_PRINCIPAL and
  QT_ORACLE_SITE_BASE_URL. Check ACTUAL V2 unit; its installed a67 unit lacks
  this EnvironmentFile. V1 unit's optional EnvironmentFile does not prove V2.

## New isolated projection prototype — NOT DEPLOYMENT READY

`deploy/oracle_live_projection.py`: stdlib optional observer around unchanged
content-addressed qualified core, `--core-release`, `--config`, `--state-dir`.
Observes successful canonical CAS, then starts native Site visual session;
explicit lane/stage mapping, live-only heartbeat, printed stdout hash proof,
completion/end, idempotent exact-packet retries. Never replays stale starts.
UI failure cannot roll back scientific commit. Secret removed from environment
before Git/model subprocesses. ACK receipt Git write only AFTER scientific wake
ends, avoiding a HEAD change during reasoning. No alternate task authority.

Six local tests PASS (`tests/test_oracle_live_projection.py`), including real
Git claim/crash/recovery/new generation, failed CAS -> no phantom Site action,
Site failure isolation, exact uncertain-packet retry, heartbeat semantics,
actual stdout proof, completion idempotence and no economic/owner animation.
V2 CI now includes this module. Global discovery becomes608; regenerate STATE
using `scripts/status_artifacts.py --write`, never hand-edit the counter.

Still required: review/harden prototype (bounded local receipt retention,
secure synchronized key rotation, production installer/gated service override,
same core SHA pinned, explicit projection source SHA), CI, install on Oracle,
actual authenticated wake -> D1 -> SSE correlation and desktop UI proof.
Do NOT claim Safari/iPhone without a real device test.

## Access / private local helpers (never commit credentials)

OCI Run Command works as `ocarun` uid999, no general sudo. Owner SSH `ubuntu`
can install root files; do all code/tests/CI before requesting one concrete
Owner block. Existing fixed no-argument root controls are usable through OCI:
`/usr/local/libexec/quant-v2-{qualify,activate,status}`.

- Worktree `/workspace/Quant-Trade-v2`; old `/workspace/Quant-Trade` parked with
  stale V1 docs, do not push those.
- OCI SDK Python `/home/agent/.local/share/quant-oci/venv/bin/python`.
  Config `/home/agent/.oci/quant-trade-recovery.config` (private), never print.
- `/workspace/quant-oci-access.py --script-file ... --timeout ...` or
  `--command-id ...` to resume. Delivery takes3–5 minutes. Never duplicate an
  ACCEPTED mutation. Logs/requests in `/workspace/quant-oci-session`.
- `/workspace/quant-v2-status-live.sh` exports sanitized full native journal,
  copies it into ocarun cache, prints bounded summary/file hash.
- `/workspace/quant-fetch-inventory.py --filename ... --expected ... --stem ...`
  retrieves sanitized JSON through four hash-verified compressed chunks.
- `/workspace/quant-v2-reboot.py` sent the single reset; its exclusive request
  file prevents duplication. Do not use old V1 reboot or root prepare scripts.
- Site source READ-ONLY checkout `/workspace/.quant-site-private/source` at
  exact v25 SHA above; native contract in `worker/oracle-ingress.mjs`, tests in
  `test/oracle-ingress.test.mjs`. No Site source was changed/pushed/published.
  A transient source Git credential was used in memory only and expires;
  it is NOT the Oracle ingress key. No credential was stored in Git config.
- Owner handoff branch `builder/live-lab-oracle-canonical-20261020`,
  `research/live_lab_ux/WORK_SITE_HANDOFF_20261020.md`; only UI metadata wrapper,
  explicitly NO HTTP emitter. Reuse selectively, never merge wholesale.

All four economic/prospective/capital/trading authorities remain FALSE.

## 15:40 UTC continuation — preserve, do not restart

Fresh Oracle inventory: boot `4aa3fb04-ff14-49fa-8f08-0171d41c6701`
(differs from preboot), V2 timer enabled/active, V1 disabled/inactive, model
active/enabled and `/health` status `ok`, model RAM 10,348,507,136 bytes.
The existing service still uses the native V2 entrypoint, without projection.
Evidence OCI command:
`ocid1.instanceagentcommand.oc1.eu-paris-1.amaaaaaatoradqaa6lhygr2hmaxpp3vozeouka26whfblsauhrznnhu45hpa`.
Owner then asked this agent to finish independently; no other-agent handoff arrived.

The optional observer now has bounded 256-file local retention, seven tests;
root installer `deploy/oracle_live_host_prepare.py` has three contract tests.
Installer pins the unchanged a67 scientific core, verifies exact observer CI,
installs only the observer + systemd drop-in + root:quant-research 0640 env,
drains the current wake without killing science, retains the canonical flock,
then resumes the existing timer and requests one actual wake.
It never modifies the scientific config, model, queue, tasks or authorities.
Secret rotation is explicitly Owner-authorized. Its only VM transport is
RSA3072 OAEP-SHA256 ciphertext; the ephemeral private key stays on Oracle.
Do not claim live Site delivery until the root installation and correlated
real Oracle event / GitHub observer receipt / public snapshot / SSE are proven.

Fresh native root status completed 2026-10-20T15:50:47Z: new boot ID as
above, model health PASS, V2 active/enabled, 29 postboot wakes with durable
output commits. Last invocation `38b12ebc10da443eb3f17dc908ce1abc`, commit
`1b80321eb81860586b5645661e34574ed40f968f`, DERIVED_ONE_READY_TASK.
Full root-owned evidence remains on Oracle as
`v2-status-20261020T155047.695158Z.json`, SHA256
`d6a7afc34c87c52fc3100a3b8bd008bb02fc860348a9749ef609815b056312c8`.
Local tests: 22 integration/deployment tests PASS before retention change;
final 10 observer/installer tests PASS; 21 readiness/portfolio tests PASS;
unchanged Site production-source native ingress tests 5/5 PASS.

Site secret rotation: production environment revision11, same v25 source,
deployment `appgdep_6ad78e0219288191a446d21fa7632ce1` requested.
Only sealed ciphertext is staged in ocarun's private `.cache/quant-live-link`;
its SHA256 is `5606aa4de1c944b2d515c863964d95c5ed24915e0414d5f1c472ffc4eeb574c4`.
Do not rotate again merely to inspect it: the matching key is now stored by
Sites, and the existing VM private transport key decrypts the staged payload.
Root installation has NOT yet happened. Installer must pass both exact-source
CI gates before Owner runs the final bounded command.

Same Site v25 redeployed successfully with environment revision11. Real HTTP
authorization checks: anonymous401, rotated credential + forbidden worker403;
no test worker/session created. Explicit `Quant-Trade-Oracle/1.0` User-Agent
is required by the public ingress edge (default Python agent returned403).
ASML/current-corpus preflight 15/15 PASS. Status test count612 obtained from
canonical `unit_test_count()`; unchanged replay inputs, no manual count.
