# AGENT 3 — EVENT-DRIVEN EQUITIES SCOUT

DATE = 2026-10-08
MISSION_CLASS = ONE_SHOT_FOLLOWUP_DATA_ACCESS_GATE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
OUTCOME_WINDOW_CONSUMED = NONE
SEC_COLLECTOR_CHANGE = NONE

## F3 / FORM4 RELATION

F3_REFERENCE_BRANCH = builder/sec-form4-census-v2a
F3_REFERENCE_SHA = 08dcfc39b4b22e0b25e54edde7b6accbb2bc4502
F3_REFERENCE_ARTIFACT = SEC_FORM4_CENSUS_MISSION.md
CANDIDATE_1_RELATION = SAME_FAMILY_NEW_EXPRESSION
FAMILY_NOVELTY = FALSE
RELATION_REASON = Existing F3/Form4 already defines the same economic family and upstream SEC substrate: original Form 4, non-derivative code P/acquired A, officer/director qualification, issuer CIK as stable identity, EDGAR public acceptance timing, and downstream-only security/price coverage. F3's registered expression forms an event when the trailing 10-session window crosses from fewer than 2 to at least 2 distinct qualified reporting-owner CIKs. The scout's Candidate 1 instead proposed a single qualifying purchase/issuer-day expression. That is an expression change inside F3, not a new causal family.
ACTION_ON_CANDIDATE_1 = DO_NOT_CREATE_NEW_FAMILY; DO_NOT_REWRITE_SEC_COLLECTOR; keep only as a possible future F3 expression if separately authorized.

## CANDIDATE_1

MECHANISM = Insider-purchase disclosure underreaction after public Form 4 acceptance.
EVENT = Original qualifying Form 4 purchase; expression differs from F3 because it does not require the registered 2-distinct-insider / 10-session crossing.
WHY_EDGE_CAN_EXIST = Same insider-information / costly-conviction mechanism already represented by F3.
WHY_NOT_ARBITRAGED = Sparse heterogeneous events and security-identity friction can delay full incorporation, but this is not causal novelty relative to F3.
POINT_IN_TIME_DATA = REUSE_EXISTING_F3_SEC_CENSUS_ONLY. No new SEC collector is justified.
PRICE_DATA = Requires point-in-time security identity, active+delisted daily prices, ticker-history and corporate-action history.
DELISTING_HANDLING = Must retain securities later delisted; no current-survivor filter or silent drop is permitted.
TIMESTAMP_INTEGRITY = Reuse existing F3 EDGAR acceptance-time semantics; no outcome work performed.
MINIMUM_DISCRIMINATING_TEST = NONE in this scout. Candidate is absorbed into F3 family and is blocked from outcome testing until the downstream market-data gate passes.
EXPECTED_INFORMATION_GAIN = LOW as an independent family because it materially overlaps F3.
ENGINEERING_COST = LOW upstream because F3 collector exists; market-data reconciliation remains non-trivial.
MAIN_BIAS_RISK = Treating the single-purchase expression as a new family, plus survivorship/ticker/corporate-action leakage.
MAIN_FALSIFICATION = N/A for this follow-up; no returns consumed.
DATA_BLOCKER = Downstream survivorship-safe market data unavailable in the current environment.
PRIOR_RANK = DEPRIORITIZED_AS_F3_EXPRESSION

## CANDIDATE_2

MECHANISM = Initial Schedule 13D post-disclosure underreaction.
EVENT = Initial Schedule 13D acceptance, excluding amendments.
WHY_EDGE_CAN_EXIST = Public revelation of a >5% beneficial owner with influence/control intent can update intervention, governance and takeover probabilities.
WHY_NOT_ARBITRAGED = EDGAR is heavily monitored and the five-business-day filing regime compresses informational lag; any residual edge may be small.
POINT_IN_TIME_DATA = SEC filing timestamp is public, but this candidate also requires deterministic historical subject-CIK-to-security mapping downstream.
PRICE_DATA = Same point-in-time active+delisted price and corporate-action requirement as Candidate 1.
DELISTING_HANDLING = Later-delisted/acquired targets must remain in universe with explicit terminal-action treatment when available.
TIMESTAMP_INTEGRITY = EDGAR acceptance datetime; no pre-acceptance execution.
MINIMUM_DISCRIMINATING_TEST = NONE until the common security/price data gate is passed. 2026 remains unconsumed.
EXPECTED_INFORMATION_GAIN = MEDIUM if clean data become available.
ENGINEERING_COST = MEDIUM because legacy/structured 13D parsing plus identity reconciliation is required.
MAIN_BIAS_RISK = Current-ticker mapping, survivor filtering, and ex-post activist outcome selection.
MAIN_FALSIFICATION = Tradable post-open residual is zero after the disclosure reaction and costs.
DATA_BLOCKER = Same current market-data access blocker; no clean full-sample CIK/security/delisting/corporate-action path is accessible now.
PRIOR_RANK = 1_AMONG_CAUSALLY_DISTINCT_REMAINING_CANDIDATES

## CONCRETE MARKET-DATA ACCESS CHECK

REQUIRED_CHAIN = CIK_AT_EVENT_DATE -> SECURITY_ID_AT_EVENT_DATE -> TICKER_HISTORY -> ACTIVE_OR_DELISTED_PRICE_PATH -> SPLITS/DIVIDENDS/TERMINAL_CORPORATE_ACTIONS
CURRENT_ENV_PROVIDER_CREDENTIALS = NONE_DETECTED_FOR_MASSIVE_POLYGON_EODHD_TIINGO_NASDAQ_QUANDL_CRSP_OR_EQUIVALENT

MASSIVE_POLYGON = PROVIDER_CAPABILITY_PLAUSIBLY_CLEAN_BUT_NOT_ACCESSIBLE_NOW. Reference endpoints expose as-of-date ticker reference, CIK, FIGI, active/delisted status, delisted timestamp and ticker events; price/split/dividend history sufficient for 2022-2024 requires a paid history tier rather than current free two-year history. No usable credential is mounted.
EODHD = PROVIDER_CAPABILITY_PLAUSIBLY_CLEAN_BUT_NOT_ACCESSIBLE_NOW. Public documentation exposes delisted-symbol workflows, EOD history, splits/dividends and Fundamentals identifiers including CIK/CUSIP/ISIN/OpenFIGI/PrimaryTicker. The demo token was sufficient only to confirm an active-name identifier response, not a complete delisted historical universe. Full use requires a paid token; none is mounted.
TIINGO = NOT_ACCEPTED_AS_CURRENT_CLEAN_PATH. It exposes active/delisted search, permanent tickers and adjusted EOD data behind a token, but no sufficiently verified deterministic CIK->security-as-of-date chain was established for this task, and no token is mounted.
YAHOO_REPO_FEED = REJECTED_FOR_THIS_USE. The repository itself records that adjusted closes are retroactively restated for corporate actions, the endpoint is undocumented, and the Data Plane lacks corporate-action history. It cannot establish a survivorship-safe issuer-CIK/security lifecycle for F3.

CIK_TO_SECURITY = BLOCKED_CURRENT_ACCESS
DELISTED_SECURITIES = BLOCKED_CURRENT_ACCESS
CORPORATE_ACTIONS = BLOCKED_CURRENT_ACCESS
SURVIVORSHIP_SAFE_PRICES_2022_2024 = BLOCKED_CURRENT_ACCESS
MARKET_DATA_ACCESS = PAID_REQUIRED

## SELECTION

TOP_CANDIDATE = CANDIDATE_2 — INITIAL_SCHEDULE_13D_POST_DISCLOSURE_UNDERREACTION
WHY_TOP = Candidate 1 is not a new family: it is SAME_FAMILY_NEW_EXPRESSION relative to existing F3/Form4. Candidate 2 remains causally distinct, but it is not ready for an outcome test because the same downstream market-data chain cannot currently be reconstructed cleanly.
MINIMUM_NEXT_TEST = NONE_UNTIL_DATA_GATE. Do not consume returns or sealed confirmation. The next admissible action is only to obtain/read a source that can simultaneously prove event-date CIK/security identity, later-delisted coverage, 2022-2024 daily executable prices, and corporate actions.
DATA_BLOCKER = No clean survivorship-safe market-data source satisfying all required downstream surfaces is accessible in the present environment. Suitable paid provider capabilities appear to exist, but credentials/entitlements are absent and free/demo access is insufficient. Do not substitute Yahoo/current-ticker data and do not build another SEC collector.
DECISION = KEEP_AS_RESERVE_DATA_BLOCKED

REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
