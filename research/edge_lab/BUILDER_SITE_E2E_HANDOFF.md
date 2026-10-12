# BUILDER HANDOFF — SITE_E2E

## Mission

Repair and prove the public research Site **end to end**. This is a deployment/product repair, not a frontend redesign and not a research-method change.

Canonical research method: `research/edge_lab/EDGE_DISCOVERY_METHOD.md`.

Public Site expected by the Owner:

`https://quant-trade-lab.sassylime.chatgpt.site`

Known Site metadata from the project context:

- project id: `appgprj_6aca43cb86bc81918e067097356a37de`
- slug: `quant-trade-lab`

Current Owner observation: public URL returns **Not Found**.

Target acceptance state:

`SITE_E2E = PASS`

Do **not** claim success from a fresh `LIVE.json`, a GitHub Actions `SUCCESS`, a locally rendered page, or a correct frontend data adapter. The public URL itself must work.

---

## Known facts — do not rediscover from scratch

- Repository: `fahimahmedb/Quant-Trade`
- Research branch: `research/edge-lab-continuous`
- `research/edge_lab/LIVE.json` previously became stale while Discovery had already advanced.
- That telemetry problem was separately repaired.
- `scripts/edge_lab_live.py` exists as a derived-display overlay.
- `.github/workflows/edge-lab.yml` now refreshes Discovery telemetry and publishes derived `STATE.json`, `STATUS.md`, and `LIVE.json` with bounded race recovery.
- A GitHub Actions run for that telemetry path previously completed successfully.
- `LIVE.json` has shown fresh Discovery state including the Treasury 5Y L1 claim.
- Therefore `GitHub research state -> derived LIVE telemetry` works at least partially.
- None of this proves public Site deployment.
- The public Site is currently reported as `Not Found`.
- The Site must remain observability only. It must never become execution authority.
- `REAL_CAPITAL_AUTHORIZED = FALSE` and `LIVE_TRADING_AUTHORIZED = FALSE` remain invariant.

---

## Core diagnosis order

Do not start with React/UI changes.

Diagnose in this order:

1. **PUBLIC ROUTE** — does the expected URL resolve and return a real page?
2. **PROJECT/SLUG BINDING** — is `quant-trade-lab` still bound to an active published project/deployment?
3. **DEPLOYMENT** — is there an active successful deployment corresponding to the intended Site project?
4. **BUILD/ARTIFACT** — only if route and deployment binding exist.
5. **DATA ADAPTER** — only if a page is served but displays stale/wrong state.
6. **CANARY PROPAGATION** — prove fresh telemetry reaches the public page.

A `404`/`Not Found` means stop inspecting frontend data selection until route/binding/deployment are checked.

---

## Phase A — establish the external failure exactly

From an environment capable of reaching the public Site, record:

- requested URL;
- timestamp UTC;
- final URL after redirects;
- HTTP status if exposed;
- response title/body signature (`Not Found`, blank, app shell, etc.);
- whether DNS/host resolution succeeded;
- whether authentication is unexpectedly required.

Persist this as evidence, for example:

`research/edge_lab/e2e/site/public-probe-before.md`

Do not infer the cause from `Not Found` alone.

---

## Phase B — inspect deployment binding before frontend code

Using the actual Site/deployment controls available to you, inspect the exact project/slug:

- project id `appgprj_6aca43cb86bc81918e067097356a37de`;
- slug `quant-trade-lab`;
- expected public URL `https://quant-trade-lab.sassylime.chatgpt.site`.

Determine, with evidence:

- does the project still exist?
- is it published?
- is the slug still assigned to that project?
- is there an active deployment?
- what source/version does the deployment point to?
- did the last deployment succeed, fail, or disappear?

If the platform exposes no deployment or binding introspection to your environment, set:

`SITE_DEPLOYMENT_CONTROL = UNAVAILABLE`

and persist the exact missing capability. Do not fabricate a deployment from GitHub alone.

---

## Phase C — repair the first broken transition only

Examples:

### If route/binding is missing

Repair only publication/binding/slug/deployment configuration necessary to make the expected public URL serve the existing Site.

Do not redesign the UI.

### If deployment exists but build failed

Repair the narrowest build/deployment defect.

Do not touch research runtime.

### If page serves but stale/wrong data is shown

Only then inspect the Site data adapter / field selection.

Known subtlety: the lab plugin/status path has historically exposed both canonical Discovery state and fresh `validation_live` / `LIVE.json`-derived telemetry. The public room may have preferred stale canonical fields over the fresh live overlay. Verify before changing anything.

Prefer a narrow precedence rule that uses fresh display telemetry for display while keeping authoritative execution state separate. Never make `LIVE.json` execution authority.

---

## Phase D — canary propagation test

After the public page serves successfully, prove the data path.

Create a benign, display-only canary that cannot affect execution authority, for example:

`SITE_CANARY_20261012_<HHMM>_<8HEX>`

Requirements:

- canary must live only in derived display telemetry or an equivalent observability-only field;
- it must not alter Discovery/Validation authority, claims, outcomes, capital flags, or scheduling;
- record the source HEAD containing the canary;
- run the normal publication/deployment path;
- verify the exact canary becomes visible on the public Site;
- then either remove the canary via the normal display path or mark it explicitly as an E2E test artifact.

Persist evidence such as:

`research/edge_lab/e2e/site/canary-verification.md`

The evidence should include:

- canary;
- source HEAD;
- generated timestamp;
- public observation timestamp;
- public URL;
- what exact field/text proved propagation.

---

## Hard non-goals

Do not:

- create a new dashboard framework;
- redesign the room;
- replace the Site platform;
- touch scheduler/automation logic;
- change Discovery/V4.2/V3 methodology;
- edit research outcomes to make the Site look active;
- make `LIVE.json` authoritative;
- rebuild telemetry generation that is already working unless the canary proves it is the broken transition;
- claim E2E success because GitHub Actions passed.

---

## Acceptance test

`SITE_E2E = PASS` only when all of the following are demonstrated:

1. expected public URL serves successfully;
2. it is the intended Site/project/slug, not a replacement URL silently substituted;
3. page displays recognizable current lab state;
4. displayed HEAD and/or generated timestamp corresponds to fresh telemetry;
5. one benign display-only canary is published through the normal path and becomes visible on the public Site;
6. research execution authority remains unchanged.

If the platform itself cannot be controlled from your environment, return `BLOCKED` with exact evidence and the smallest human/platform action required. Do not substitute a local preview.

---

## Required final handoff

Return only the following concise block after work is complete:

`SITE_E2E = PASS | FAIL | BLOCKED`

`PUBLIC_URL =`

`PUBLIC_PROBE =`

`PROJECT_ID =`

`SLUG =`

`DEPLOYMENT_STATUS =`

`FIRST_BROKEN_TRANSITION =`

`ROOT_CAUSE =`

`FIX =`

`CANARY =`

`SOURCE_HEAD =`

`PUBLIC_CANARY_OBSERVED_AT =`

`AUTHORITY_UNCHANGED = true | false`

`FILES_CHANGED =`

`COMMIT =`

If public deployment tooling is unavailable, state that explicitly and persist the blocker; do not report PASS.