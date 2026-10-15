# Paused Lane Source Qualification — 2026-10-15

Status: RESEARCH-ONLY QUALIFICATION
Branch: `research/paused-lanes-qualification-20261015`
Base HEAD: `93534d9c365b52f2aa80c4277da1cac4e7338d31`

## Authority and boundaries

Owner authorized a separate bounded effort on 2026-10-15 to advance currently PARK/PAUSE research lanes in parallel with the ratified DELTA research mandate.

This artifact is limited to source, rights, timing, data-chain and implementability qualification. It does **not** authorize or perform:

- Builder work;
- economic experiments;
- new signal→future-return or PnL looks;
- real prospective observation;
- live trading;
- real capital;
- automatic promotion of any lane;
- creation of a new research family.

`REAL_CAPITAL_AUTHORIZED = FALSE`
`LIVE_TRADING_AUTHORIZED = FALSE`
`PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
`ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`

The purpose is to determine whether an existing parked lane now has a materially better route to a future preregistered test.

## 1. Treasury auction / ZF

Existing lane: `disc-zf-auction-pressure-v0`
Existing blocker: full BBO / roll package was too costly before a first coarse effect; reactivate only if a cheap public proxy is identified.

### New source qualification

A cheap public coarse route now exists at L0:

1. U.S. Treasury FiscalData publishes Treasury Securities Auctions data with official auction-level fields and API access.
2. The Federal Reserve / FRED publishes the daily 5-Year Treasury Constant Maturity Rate (`DGS5`).

This pair is sufficient for a **coarse data-feasibility / event-response preregistration candidate** without buying ZF history or constructing a full executable futures chain.

### Qualification verdict

`SOURCE_GATE = PARTIAL_PASS`
`CHEAP_PUBLIC_PROXY_IDENTIFIED = TRUE`
`EXECUTABLE_ZF_PROXY = FALSE`
`ECONOMIC_LOOK_PERFORMED = FALSE`

This does **not** demonstrate a ZF edge, fills, futures execution, auction surprise measurement, or tradable PnL.

### Next safe action

Prepare a future frozen coarse-proxy protocol only after separate economic-experiment authority. Before that, qualify exact event fields, auction publication timestamps and whether the daily yield observation timing can support the intended event horizon without look-ahead.

Recommended lane disposition: `L0_SOURCE_GATE_ADVANCED`; do not mutate the canonical economic status automatically.

## 2. France sovereign repricing / OAT-Bund

Existing lane: `disc-france-oat-bund-l1-v0`
Existing blocker: previously declared ECB France series key returned 404; an accessible distinct proxy was required.

### New source qualification

A distinct coarse public route is identifiable:

1. Banque de France publishes daily French sovereign benchmark indices/rates including TEC10, with historical files.
2. Deutsche Bundesbank publishes a daily 10-year German federal bond yield series and downloadable time-series formats.

This is enough to replace the failed single-key dependency for **coarse relative-yield source feasibility**.

### Qualification verdict

`SOURCE_GATE = PARTIAL_PASS`
`COARSE_FRANCE_GERMANY_DAILY_PROXY = TRUE`
`FOAT_FGBL_EXECUTION_CHAIN = FALSE`
`EVENT_SURPRISE_TIMESTAMP_CHAIN = FALSE`
`ECONOMIC_LOOK_PERFORMED = FALSE`

The lane remains blocked from an economic claim because the current qualification does not establish earliest-publication timestamps for fiscal surprises, futures CTD/DV01/roll/carry, matched executable prices, fees, margin or fills.

### Next safe action

Qualify exact historical-download rights/coverage and publication semantics for TEC10/Bund daily data, then separately qualify one fixed official fiscal-event timestamp source. No event-return calculation before separate authority.

Recommended lane disposition: `L0_SOURCE_GATE_ADVANCED`; do not treat daily yield proxies as executable FOAT/FGBL.

## 3. SEC Form 4 events

Existing lane: `disc-sec-form4-eod-l1-v0`
Existing blocker: referenced census code exists but the saved event dataset was not found at the pinned source head; survivorship-safe mapping and delist prices remain unresolved.

### Primary-source qualification

SEC EDGAR is publicly accessible for the core filing/submission surfaces used by the prior capture implementation. Form 4 XML filings contain issuer/security identity and transaction fields that can support a point-in-time mapping chain if handled under the existing custody/visibility controls.

### Repository recovery findings

The prior SEC work was recovered far enough to distinguish **implementation history** from **published scientific dataset**:

1. Real raw-capture evidence exists. Commit `aa34939cd1d1995cc8a26cfc07d7c1aa7b95640c` records a live SEC probe that acquired 20 distinct Form-4 accessions as immutable raw objects, re-hashed 22 stored objects with no address mismatch, preserved the journal/raw bytes/cursor across restart, and explicitly classified the raw capture as not admissible for scientific confirmation.
2. The dedicated census branch still exists: `builder/sec-form4-census-v2a` at HEAD `08dcfc39b4b22e0b25e54edde7b6accbb2bc4502`.
3. That branch contains `scripts/sec_form4_census.py`, `scripts/sec_form4_proof.py`, dedicated SEC census/event schemas, tests, and `.github/workflows/sec-form4-census-proof.yml`.
4. The workflow was designed to generate `artifacts/sec_form4_census/`, exact-head prove it, commit it with message `data: publish deterministic SEC Form-4 V2-A1 census`, upload the pinned raw SEC cache as a GitHub Actions artifact, and then push the exact proven HEAD.
5. The current branch tree contains no `artifacts/sec_form4_census/` directory.
6. Repository commit search did not locate the expected deterministic-census publication commit.
7. Therefore the strongest supported conclusion is that the **census publication step never landed in Git history**. This is not evidence that no intermediate workflow run ever produced temporary files.
8. Actions-artifact recovery remains unverified because the currently available connector surface did not expose branch push/workflow-dispatch run enumeration sufficiently to prove presence or absence of a retained artifact. The raw-cache artifact was configured for 90-day retention when successfully uploaded.

### Qualification verdict

`SEC_PRIMARY_FILING_ACCESS = PASS`
`CIK_SECURITY_MAPPING_SUPPORT = PARTIAL_PASS`
`RAW_FORM4_CAPTURE_HISTORY_EXISTS = TRUE`
`PREVIOUS_CENSUS_IMPLEMENTATION_LOCATED = TRUE`
`DETERMINISTIC_CENSUS_PUBLISH_COMMIT_LOCATED = FALSE`
`CENSUS_ARTIFACT_IN_BRANCH_HEAD = FALSE`
`ACTIONS_ARTIFACT_RECOVERY_STATUS = UNKNOWN_CONNECTOR_LIMITATION`
`SURVIVORSHIP_DELIST_CHAIN = BLOCKED`
`REBUILD_AUTHORIZED = FALSE`
`ECONOMIC_LOOK_PERFORMED = FALSE`

### What this changes

The lane is no longer correctly described as “census work absent.” The implementation and real raw-capture history exist. The missing object is the **published deterministic scientific census** plus an admissible survivorship/delist return chain.

### Next safe action

1. If a surface capable of enumerating historical push/workflow-dispatch Actions artifacts becomes available, search for the configured `sec-form4-v2a1-raw-cache-*` artifact before reacquiring SEC data.
2. Do **not** rerun `sec_form4_census.py` against SEC until a separate historical-data acquisition/rebuild authority is granted.
3. Independently qualify a survivorship-safe/delist-capable price source and point-in-time security mapping path without inspecting the hypothesis outcome.
4. Only after those data-chain gates are resolved should a new frozen economic protocol be considered.

Recommended lane disposition: `DATA_CHAIN_PARTIAL_UNBLOCK`; canonical economic state remains unchanged.

## 4. Hyperliquid forced-flow

Existing lane: `disc-hyperliquid-forced-flow-v0`
Existing blocker: heavy node/global-fill infrastructure before first signal; reactivate only with cheap compliant data route.

### Source qualification

Official Hyperliquid historical archive documentation exposes L2/historical data through archive infrastructure, but archive transfer is requester-pays and the public info API's fill endpoints are limited/recent and do not substitute for a complete historical global-flow+BBO stream.

### Qualification verdict

`ZERO_PAID_FULL_HISTORY_ROUTE = NOT_FOUND`
`PUBLIC_RECENT_FILLS_SUBSTITUTE = INADEQUATE`
`PARK_DATA = CONFIRMED`

No reactivation is recommended from the evidence currently available.

## 5. F2 prediction access

Existing blocker is explicit permission/access.

`STATUS = PARK_PERMISSION_CONFIRMED`

No source workaround is authorized because the blocker is permission, not merely discoverability.

## 6. Policy announcement repricing

The lane is prospective by design and currently requires a frozen V4.2 contract / qualified timing source.

Because `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`, this work may qualify official metadata and timing semantics only. It may not begin collection of a prospective outcome sample.

`STATUS = PARK_UNTIL_AUTHORITY`

## 7. CFE VIX term premium

The existing `disc-cfe-vix-term-premium-l1-v2-reader` expression remains `PROMOTE_EXPRESSION`, not `EDGE_VALIDATED`. This paused-lane qualification does not reopen or extend the economic sample.

Known unresolved items remain material: current 2022–2026 behavior, capital denominator, margin/intratrade path, executable-fill semantics, attribution and effective-trial denominator.

`STATUS = NO_NEW_ECONOMIC_ACTION`

## Decision matrix

| Lane | Previous blocker | New qualification | Recommendation |
|---|---|---|---|
| Treasury / ZF | no cheap proxy before BBO/roll work | official auction + daily 5Y proxy identified | `L0_SOURCE_GATE_ADVANCED` |
| France OAT/Bund | failed ECB key / no distinct proxy | TEC10 + Bundesbank 10Y route identified | `L0_SOURCE_GATE_ADVANCED` |
| SEC Form 4 | missing census + mapping/delist chain | census implementation + raw capture history recovered; deterministic publish absent; delist chain still blocked | `DATA_CHAIN_PARTIAL_UNBLOCK` |
| Hyperliquid | expensive host/global history | official archive remains requester-pays; recent API insufficient | `PARK_DATA_CONFIRMED` |
| F2 prediction | permission/access | unchanged | `PARK_PERMISSION_CONFIRMED` |
| Policy announcement | prospective contract/timing | authority still absent | `PARK_UNTIL_AUTHORITY` |
| CFE VIX | promoted expression needs stronger proof | no new source action in this pass | `NO_NEW_ECONOMIC_ACTION` |

## Research integrity

No economic outcome was accessed or recomputed for the parked lanes in this qualification pass. No economic state transition is authorized by this memo. Any future L1 economic look requires its own frozen protocol and separate authority consistent with canonical governance.
