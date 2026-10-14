# CFE VX term-premium — prospective OOS v1

Status: FROZEN_PROSPECTIVE_OBSERVATION
Parent expression: `disc-cfe-vix-term-premium-l1-v2-reader`
Parent contract SHA256: `6ceab04d5f8ddbc0c5c1d7e7fa2314ff9ef60015579165b3e3d4fc1b79891d01`
Parent result verdict: `PROMOTE_EXPRESSION`
PROSPECTIVE_T0: `2026-10-15T00:00:00Z`
REAL_CAPITAL_AUTHORIZED: `false`
LIVE_TRADING_AUTHORIZED: `false`
PAID_USD_TOTAL: `0`

## Purpose

Freeze the already-promoted fixed VX settlement expression before collecting any new prospective economic observations. This is passive forward OOS evidence only. It does not validate alpha, execution, capacity, live readiness, or residual return after compensation for volatility/crash/liquidity risk.

The parent L1 already passed its one predeclared concentration adversary. No additional historical parameter search, sibling-window search, threshold search, or retrospective 2022–2026 backfill is authorized by this protocol.

## Frozen expression

The expression is exactly the parent `disc-cfe-vix-term-premium-l1-v2-reader`; this protocol creates no new economic variant.

- Instrument family: standard CFE VX futures.
- Direction: short one VX futures contract for expression accounting only; no real trade.
- Contract set: standard quarterly VX contracts only, preserving the H/M/U/Z cadence used by the parent sample.
- Entry target: 45 calendar days before the contract's final settlement.
- Exit target: 15 calendar days before the contract's final settlement.
- Endpoint tolerance: nearest otherwise-valid settlement within ±4 calendar days, exactly as in the parent contract.
- Central round-trip friction: 0.10 VX point.
- Stress round-trip friction: 0.25 VX point.
- Multiplier for descriptive unit conversion: USD 1,000 per VX point.
- Source/reader semantics: unchanged from the parent contract. Unknown/repeated notices, duplicate/non-monotone dates, malformed records, or ambiguous settlement schema are rejected rather than repaired ad hoc.

If any wording here can be interpreted differently from the parent contract, the parent contract and its frozen reader semantics control. No reinterpretation of `45→15`, endpoint selection, costs, contract cadence, or source QA is allowed.

## Prospective eligibility

A contract is eligible only if its frozen 45-day entry endpoint is on or after `PROSPECTIVE_T0`.

No contract with an entry endpoint before T0 may ever be inserted as prospective evidence, including 2022–2026 contracts whose outcomes are presently unknown to this protocol. Historical gaps remain historical gaps.

Every eligible quarterly contract is part of the OOS population. There is no outcome-based inclusion, exclusion, replacement, retry, or skipping. A missing/invalid official source is recorded as a missing observation, not replaced by another contract or data vendor.

The first eligible contract is determined mechanically from the official CFE settlement calendar and the frozen endpoint-selection rule; it is not selected using price behavior.

## Information discipline

Before T0, do not access or calculate any new signal→future-payoff observation for this protocol.

For each eligible contract:

1. determine identity/final-settlement date using non-outcome contract/calendar information;
2. apply the frozen 45-day endpoint rule without looking ahead to the exit payoff;
3. after the frozen exit endpoint has occurred and official settlement data are public, record entry/exit settlements and the derived gross/central/stress result;
4. append the observation; never overwrite a prior observation except to correct a demonstrable transcription/source-integrity error, which must preserve an audit trail.

No intraperiod discretionary stop, volatility filter, term-structure filter, macro filter, VIX-level filter, roll change, contract substitution, or exposure sizing rule may be introduced.

## OOS outputs

For completed prospective observations report only frozen-expression diagnostics:

- number of eligible contracts;
- number observed / missing and exact missing reason;
- gross mean/median VX points;
- central-net mean/median VX points;
- stress-net mean/median VX points;
- cumulative central/stress points;
- worst completed trade;
- endpoint-to-endpoint drawdown over the prospective sequence;
- chronological per-contract record and source hashes privately where rights require it.

No Sharpe/CAGR/annualized alpha or capacity claim is authorized from a small quarterly OOS sample.

## Interpretation

Prospective observations can strengthen or weaken confidence that the fixed expression persists. They cannot by themselves establish that the return is mispricing rather than compensation for crash/convexity/liquidity risk.

Allowed state labels:

- `OOS_ACCUMULATING`
- `OOS_WEAKENS_EXPRESSION`
- `OOS_SUPPORTS_FURTHER_VALIDATION`
- `PARK_DATA`

Forbidden labels from this protocol alone:

- `ALPHA`
- `EDGE_VALIDATED`
- `V3_PASS`
- `LIVE_READY`
- `REAL_CAPITAL_AUTHORIZED`

There is no automatic promotion threshold invented here. Any future transition to strict V3/capturability work requires a separate predeclared protocol and an actually available execution-quality data route.

## Existing execution-data blocker remains binding

The zero-paid-cost L2 qualification remains `PARK_DATA`: public CFE settlement/history data are adequate for this settlement-level prospective record, but they do not provide the complete historical bid/ask/trade/margin package needed to identify executable residual alpha. This OOS freeze does not reopen that blocker and does not authorize purchase, subscription, account creation, or a replay of the completed 2013–2021 L1.

## Scientific invariants

- one economic look globally remains in force;
- this protocol is passive and must not pre-empt an already active economic look;
- no post-outcome retuning;
- no 2022–2026 retrospective backfill presented as OOS;
- no real/live capital;
- `paid_usd_total = 0`.

## Next valid action

Wait until the first mechanically eligible quarterly contract reaches its frozen exit endpoint. Only then append its first prospective observation. Until that date, further VX economic work on this expression would be redundant search or look-ahead and is not authorized.
