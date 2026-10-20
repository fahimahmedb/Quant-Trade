# CHECKPOINT 013 — Site v25 / Oracle V2 live-state reconciliation

Recorded 2026-10-20 after the Site Work branch and Codex V2 work advanced beyond CP12.

## Status

`CP13_RESUME_POINT = CURRENT`

This checkpoint does not replace CP12's repository-history reconciliation. It updates only the live V2 + Live Lab operating picture so work can resume without trusting stale handoffs.

All four hard authorities remain CLOSED:

- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`

---

## 1. Oracle V2 — current observed truth

Current branch:

`builder/oracle-v2-core-20261020`

Observed current HEAD during CP13:

`7b18783fc5e7aa83085e7226652f1b165ff56a83`

This is an autonomous Quant Research OS commit, not a Builder documentation commit:

`Research OS canonical queue refill c45424ba152150a97a728c88df27f14419ba52acad6799c5ec5403cbd6567f80 [skip ci]`

The event identifies:

- `worker_id = oracle-research-v2.integrator_portfolio`
- `research_contract_version = v2-core`
- `release_sha = a67ffec48fff895d5edc42171855e2213e49cf0d`
- a newly queued event-document frontier task
- all economic/prospective/capital/live authorities false
- hosted model calls = 0

### Actual Oracle V2 qualification

Commit:

`243019cf9dc76d8a6c2862a2bf65cf18bab90003`

Message:

`Research OS V2 actual Oracle qualification [skip ci]`

Its durable qualification evidence records all of the following live gates as true:

- authority closed;
- canonical migration;
- claim-expiry recovery;
- exact-release CI;
- local GPT-OSS reasoning;
- no duplicate replay;
- Oracle identity;
- real read-only entrypoint;
- trial before ideation;
- V1 quiesced during writes;
- V2 sidecars persisted.

It records:

- Oracle instance `VM.Standard.A1.Flex`, 2 OCPU / 12 GiB;
- hosted model calls = 0;
- local backend health PASS;
- model `gpt-oss-10.2b-q4-k-m`;
- runtime `openai_compatible`;
- model output classification remains `UNVERIFIED_MODEL_COMMENTARY`;
- outcome access false;
- all four authorities false.

### Writer transfer

Observed sequence:

- V1 branch still wrote at `2026-10-20T11:00:11Z`;
- V2 recorded `Research OS V2 bounded authority transfer` at `2026-10-20T11:02:47Z`;
- V2 then produced canonical queue refill at `11:03:54Z`;
- V2 subsequently claimed and executed `FRONTIER-QUANT-MECHANISM-DISTINCT-007`;
- that research stage failed closed on `MISSING_QUALIFIED_DOCUMENTARY_SOURCE_FOR_ENGINE:quant` with no outcome access and no model calls rather than fabricating source/evidence;
- V2 produced another canonical queue refill at `11:20:15Z`.

This is strong durable evidence that the V2 branch became the active durable Research OS writer after the bounded transfer.

### Active epoch

`V2_ACTIVE_EPOCH.json` currently records:

- state `OPEN`;
- epoch `ORACLE-V2-EPOCH-20261020-001`;
- knowledge cutoff `2026-10-20T01:00:00Z`;
- allowed models: deterministic engine + `gpt-oss-10.2b-q4-k-m`;
- contamination status `CLEAN`;
- Owner/Supervisor outcome blinding `BLINDED`;
- economic feedback not visible to the active epoch;
- first evaluation export accepted = false.

### Important stale-document warning

`ORACLE_V2_CORE_ROADMAP.md` and the older `CODEX_V2_HANDOFF_20261020.md` still contain statements that actual V2 activation/writes were pending. Those statements predate the 10:55–11:20 UTC live qualification and transfer sequence and MUST NOT be used as current runtime status without reconciliation.

### Reboot evidence

CP13 did not find a later explicit V2 `post-reboot`/`reboot` qualification commit. Therefore:

`V2_ACTIVE_WRITER = PROVEN`

`V2_ACTUAL_ORACLE_QUALIFICATION = PROVEN`

`V2_POST_REBOOT_AUTOMATIC_RECOVERY = NOT_YET_RECONCILED_BY_CP13`

Do not infer the last property from V1's reboot proof.

---

## 2. Existing Live Lab Site — recovered Work handoff

Exact existing Site:

- project id: `appgprj_6aca43cb86bc81918e067097356a37de`
- slug: `quant-trade-lab`
- public URL: `https://quant-trade-lab.sassylime.chatgpt.site/`

Latest Work branch handoff reports:

- Site version **25** published;
- environment revision **10**;
- authenticated Oracle ingress operational;
- D1 -> SSE production canary validated;
- old diagnostic agents hidden from the Live Lab while historical data was preserved;
- reload does not replay business animation;
- **97 tests passed**;
- real capital and Economic Look remain disabled.

The canonical repository handoff remains:

`builder/live-lab-oracle-canonical-20261020`

and documents production routes/contracts including:

- `POST /api/oracle/session`
- `POST /api/oracle/event`
- canonical outbound SSE `GET /api/work/events`
- factual snapshot `GET /api/work/snapshot`
- dedicated principal `oracle-research-live`
- secret must remain in secret storage and never be persisted in GitHub/events/logs/screenshots/chat.

The Site is an observational projection, never scientific/economic authority.

### Verification scope caveat

CP13 can verify the GitHub-side contract and recover the exact Work handoff, but did not independently reopen/control the Site browser in this checkpoint. Therefore Site version/revision/test-count/canary claims remain the Work-produced production handoff, not a second independent browser audit by CP13.

---

## 3. The remaining real V2 -> Site integration gap

The Work handoff states that the rotated ingress secret was registered on the Site side but the matching value was not yet installed/established in the Oracle VM runtime.

Expected runtime variable:

`QT_ORACLE_INGRESS_KEY`

Expected VM env file:

`/etc/quant-research/worker.env`

Expected permissions:

- owner: `root:quant-research`
- mode: `0640`

Expected principal:

`oracle-research-live`

No secret value belongs in GitHub or this checkpoint.

### Current V2 code observation

At current V2 HEAD, these Live Lab source files are NOT present:

- `research/research_os/live_lab_contract.py`
- `research/research_os/oracle_live_worker.py`

They remain present on the canonical Live Lab branch, where the wrapper explicitly says it adds UI metadata only and does not add network transport or change scientific authority/queue/leases/receipts/results.

The active V2 branch already emits durable canonical Research OS event objects containing fields such as:

- event_id
- session_id
- worker_id
- action_id
- event_type
- event_seq
- generation
- emitted_at
- payload

Example current V2 workers include `oracle-research-v2.integrator_portfolio` and `oracle-research-v2.market_discovery`.

Therefore the correct final bridge is NOT GitHub polling and NOT a second business-state system. It is a bounded emitter/adapter from actual V2 runtime events to the already-qualified Site ingress.

---

## 4. Resume decision

### V2

Do NOT restart V2 implementation. It is already live as a pre-outcome autonomous writer.

Immediate V2 work should be limited to:

1. reconcile/update stale V2 roadmap/handoff with the actual qualification + writer transfer;
2. obtain/prove V2 post-reboot automatic recovery if still required by the V2 DoD;
3. do not disturb active epoch or live writer while adding Site observability;
4. after operational closure, resume CP12 historical-capability reconciliation before declaring a clean canonical V2 trunk.

### Site

Do NOT rebuild or republish a replacement Site. Preserve version 25/rev10 unless a bounded integration fix truly requires a new revision.

Immediate Site/Oracle integration work:

1. preserve the already-qualified Site ingress and D1/SSE path;
2. rotate/install one matching secret on Site + VM without exposing it;
3. add/use a bounded V2 runtime emitter/adapter that submits actual canonical V2 events to the Site ingress;
4. execute one genuine V2 wake through production ingress;
5. correlate exact event/session/generation/cursor through ingress -> D1 -> SSE -> reducer/UI;
6. prove completion stops motion and reload does not replay it;
7. preserve all four authorities false and never synthesize Economic Look/progress/Owner roles.

### Final CP13 target

`V2_ACTIVE_PRE_OUTCOME_WRITER + LIVE_LAB_REAL_ORACLE_E2E + CP12_RECONCILIATION_READY`

The only current missing bridge between the two live lines is the real authenticated V2 event emission into the already-qualified Site transport. The Site transport itself should not be redesigned.