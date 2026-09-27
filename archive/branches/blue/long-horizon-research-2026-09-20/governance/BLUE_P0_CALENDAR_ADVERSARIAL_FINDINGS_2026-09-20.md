# BLUE — P0 Calendar Adversarial Findings — 2026-09-20

## Authority

Research/adversarial record only. This file does not declare t0, continuity, or a governance amendment.

`t0 = NOT DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

## Finding CAL-001 — EDGAR daily-index settlement anchored to UTC calendar date

Status: **REPRODUCED RED / FIX CANDIDATE UNDER EXACT-HEAD CI**

Research branch:
`blue/p0-continuity-qualification-2026-09-20`

Red commit:
`a9dd68457397e7c392c3866ccefdef2b9bd22910`

Red CI:
`35479512122 = COMPLETED / FAILURE`

The failure was isolated to exactly two new discriminants:
- `test_settle_delay_is_measured_after_edgar_close_not_utc_date_start`
- `test_bootstrap_day_is_the_edgar_eastern_business_date`

384 tests ran; exactly 2 failed.

### Defect

Production `reconciliation_due()` previously did:

- `cutoff = now - timedelta(hours=DAILY_INDEX_SETTLE_HOURS)`
- `day = parse_ts(bootstrap_started_at_utc).date()`
- considered a day settled when its UTC calendar date was not later than `cutoff.date()`.

But the code's own contract says `DAILY_INDEX_SETTLE_HOURS = 30` is the wait **after a day closes**.

SEC authority says:
- EDGAR filing hours are 06:00–22:00 Eastern Time on business days;
- indexes incorporating the current business day's filings are updated nightly beginning about 22:00 ET and are usually completed within a few hours.

Therefore the settlement clock must be anchored to the EDGAR Eastern business-day close, not UTC midnight/date truncation.

The old implementation could make a Friday daily index due only a few elapsed hours after the 22:00 ET close while claiming the 30-hour policy had elapsed. A syntactically valid but not-yet-complete index could then become a false coverage proof.

### Candidate correction

Commit:
`5b5489edef620080df3410d93e9b213c7e6c66bf`

Changes:
- map bootstrap/source dates through `America/New_York`;
- define the business-day close as 22:00 ET;
- convert that close to UTC before adding the existing 30-hour elapsed-time policy, avoiding DST +/-1h errors;
- make a day eligible only when the exact settlement instant has elapsed;
- correct one pre-existing test whose comment said the next day was not settled while its assertion incorrectly required it to be due.

This is acquisition-critical because `collector.py` is in the P0 fingerprint closure.

At the time this record was written, exact-head CI for the candidate was still running. Do not claim green until refreshed.

## Finding CAL-002 — federal holiday can pin reconciliation forever

Status: **STRONG CODE/SOURCE HYPOTHESIS / RED TEST NOT YET RUN**

### External evidence

SEC's current 2026 EDGAR calendar explicitly lists federal holidays on which EDGAR will not receive/process/accept filings.

The SEC daily-index directory for Q3 2026 has files for Friday 2026-09-04 and Tuesday 2026-09-08 but no daily-index file for Labor Day Monday 2026-09-07.

Sources rechecked on 2026-09-20:
- https://www.sec.gov/submit-filings/filer-support-resources/edgar-calendar
- https://www.sec.gov/Archives/edgar/daily-index/2026/QTR3/
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

### Current code path

`reconciliation_due()` skips only `day.weekday() >= 5`.
It has no EDGAR holiday authority.

A weekday federal holiday therefore becomes a reconciliation target after the settle horizon.

`reconcile(day)` on a missing holiday daily index:
- opens `DAILY_INDEX_UNAVAILABLE`;
- appends the date to `unreconciled_days`;
- does not mark it reconciled.

`reconciliation_due()` does not skip `unreconciled_days`; it keeps returning the oldest date not in `reconciled_days`.

The Clock still prioritizes due discovery polls, so raw discovery is not permanently stopped. But daily-index reconciliation can remain pinned to the holiday and later days can never be reconciled, leaving the coverage proof unable to self-heal.

### Required next discriminant

Before calling this a confirmed defect, add a focused test proving:
1. a known SEC federal holiday is not a reconciliation obligation;
2. the next business day becomes eligible normally after its own settle threshold;
3. no business-day 404 is silently treated as a holiday;
4. holiday authority is prospective/versioned/fingerprinted, not inferred from the observed 404.

Do not fix by "404 means holiday"; that would turn a source outage into a false source-normal silence.

## Relation to the P14D challenge

These findings strengthen the case that a fixed passive 14-day soak is not equivalent to targeted calendar/fault testing:
- a 14-day window may not cross DST;
- it may not include a federal holiday;
- it does not force the exact settlement boundary;
- it does not distinguish a correct business calendar from a UTC-date approximation unless the chosen dates expose it.

The correct replacement is still hybrid:
accelerated discriminants + target-host proof + prospectively declared real-source calendar events.
