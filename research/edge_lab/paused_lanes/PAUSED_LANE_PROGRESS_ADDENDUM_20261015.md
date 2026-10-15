# Paused Lane Progress Addendum — 2026-10-15

Status: RESEARCH-ONLY QUALIFICATION
Authority: Owner-authorized continuation of existing PARK/PAUSE lanes only.

Invariants:
- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- `PROSPECTIVE_OBSERVATION_AUTHORIZED = FALSE`
- `ECONOMIC_EXPERIMENT_AUTHORIZED = FALSE`
- no new signal→future-return/PnL look was performed.

## 1. Treasury auction / ZF — timing semantics tightened

New verified source semantics:
- TreasuryDirect states its auction-results page is updated on a real-time basis as soon as results are made available.
- TreasuryDirect account FAQ states public-auction result details are available after 2 p.m. ET.
- FiscalData Treasury Securities Auctions exposes `record_date` as the date data was published, but it is date-granular rather than a historical intraday timestamp.

Implication:
- a future coarse DAILY protocol is source-feasible;
- an intraday event-study must not be inferred from FiscalData `record_date` or DGS5;
- exact historical intraday release time remains a separate requirement if the hypothesis depends on minutes/hours.

Status:
- `CHEAP_PUBLIC_PROXY_IDENTIFIED = TRUE`
- `DAILY_COARSE_PROTOCOL_FEASIBLE = TRUE`
- `HISTORICAL_INTRADAY_TIMESTAMP_CHAIN = NOT_PROVEN`
- `ECONOMIC_LOOK_PERFORMED = FALSE`

## 2. France OAT/Bund — daily proxy chain confirmed

New verified source semantics:
- Banque de France publishes daily TEC-n rates and explicitly provides historical files; TEC10 is a constant-maturity synthetic French Treasury yield.
- Deutsche Bundesbank publishes downloadable daily 10-year Federal-bond yield time series.

Implication:
- a future DAILY France-vs-Germany relative-yield protocol is source-feasible;
- this is not an executable FOAT/FGBL chain;
- historical intraday fiscal-surprise timing remains unproven.

Status:
- `FRANCE_DAILY_PROXY = PASS`
- `GERMANY_DAILY_PROXY = PASS`
- `DAILY_RELATIVE_YIELD_CHAIN = PASS_L0`
- `INTRADAY_EVENT_CHAIN = BLOCKED`
- `FUTURES_EXECUTION_CHAIN = BLOCKED`
- `ECONOMIC_LOOK_PERFORMED = FALSE`

## 3. SEC Form 4 — recovery and delisting route advanced

### CI recovery
Repository-level Actions enumeration recovered the historical SEC Form-4 census workflow runs on `builder/sec-form4-census-v2a`:
- 66 historical runs are visible;
- 3 runs completed successfully;
- successful run `34880954696` has no retained artifact today;
- successful run `34878811352` has no retained artifact today;
- the latest run `35416321420` failed and has no artifact.

This materially narrows the recovery question: old successful CI existed, but the checked successful runs no longer expose the expected raw-cache artifact. This is consistent with expiry/non-upload, not proof that no temporary files ever existed.

### Survivorship / delisting return chain
A scientifically adequate canonical route is now identified:
- CRSP explicitly provides post-delisting return fields, including delisting return (`DLRET`), delisting amount (`DLAMT`) and delisting payment date (`DLPDT`).
- Nasdaq Security Status / Daily List can identify issue deletions and symbol/corporate-action history, but this does not substitute for a full delisting-return series. Historical Daily List access is fee-based.

Implication:
- the prior vague blocker `SURVIVORSHIP_DELIST_CHAIN = BLOCKED` can be refined to `CANONICAL_PAID_ROUTE_IDENTIFIED`;
- a rigorous free replacement has not been established;
- no data purchase or reacquisition is authorized by this memo.

Status:
- `HISTORICAL_CI_RUNS_RECOVERED = TRUE`
- `SUCCESSFUL_CI_RUNS_EXIST = TRUE`
- `RETAINED_RAW_CACHE_ARTIFACT_FOUND = FALSE_ON_CHECKED_RUNS`
- `CANONICAL_DELIST_RETURN_ROUTE = CRSP`
- `CRSP_ACCESS_COST_RIGHTS = UNRESOLVED`
- `FREE_EQUIVALENT_DELIST_RETURN_CHAIN = NOT_ESTABLISHED`
- `REBUILD_AUTHORIZED = FALSE`
- `ECONOMIC_LOOK_PERFORMED = FALSE`

Recommended next action if Owner later authorizes data acquisition/rebuild:
1. Decide whether CRSP/WRDS access is available/acceptable.
2. If yes, bind SEC issuer/security mapping to a survivorship-safe CRSP identifier path before outcome testing.
3. If no, evaluate a bounded commercial alternative that explicitly includes inactive securities and post-delisting economics; do not silently substitute current-ticker data.
4. Reacquire/rebuild the deterministic SEC census only after the data-chain decision, using the existing branch/scripts rather than starting over.

## 4. Current lane decisions

| Lane | New state after this addendum | Remaining blocker |
|---|---|---|
| Treasury / ZF | `L0_DAILY_SOURCE_GATE_PASS` | intraday timestamp/executable futures chain if required |
| France OAT/Bund | `L0_DAILY_SOURCE_GATE_PASS` | fiscal-event timing + futures execution chain |
| SEC Form 4 | `RECOVERY_COMPLETE_ENOUGH_FOR_DATA_DECISION` | census rebuild authority + survivorship/delist source access |
| Hyperliquid | `PARK_DATA_CONFIRMED` | paid/global history requirement |
| F2 | `PARK_PERMISSION_CONFIRMED` | explicit permission/access |
| Policy announcement | `PARK_UNTIL_AUTHORITY` | prospective observation authority |
| CFE VIX | `NO_NEW_ECONOMIC_ACTION` | stronger economic/prospective proof |

## Research integrity

This addendum advances source/timing/recovery/data-chain knowledge only. It does not change any canonical economic verdict, does not validate an edge, and does not authorize economic testing, prospective observation, live trading or capital use.
