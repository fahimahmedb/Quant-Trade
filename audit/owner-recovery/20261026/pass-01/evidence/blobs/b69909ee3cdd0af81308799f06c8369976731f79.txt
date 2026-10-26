# Treasury auction inventory-pressure / ZF — frozen outcome-blind test

DATE_FROZEN = 2026-10-08
OUTCOME_EXPOSURE = NONE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE

## Treasury source contract

- Universe source: TreasuryDirect Auction Query plus the original Treasury offering-announcement PDF for every event.
- Frozen universe: every auction **announced as a nominal 5-Year Note** with auction date from **2015-01-01 through 2026-09-30 inclusive**. TIPS, FRNs and other terms are out. Announced reopenings remain in; no event may be excluded using auction-result information.
- Required fields before any price read: announcement date, auction date, security type, security term, reopening flag, CUSIP when available, original-announcement URL, and the original announcement's competitive-closing time.
- The competitive close is not inferred from a generic 13:00 convention. It is read from the original announcement and must explicitly be ET. `America/New_York` is converted to UTC using date-specific DST.
- Original announcement availability must predate PRE entry. The harness uses a conservative invariant: even announcement-date 23:59:59 ET must be earlier than T-180m.

TreasuryDirect confirms that Auction Query has non-TIPS announcement/results data from 1998 and supports CSV/JSON/XML downloads; the historical press-release archive exposes original announcements by auction year. Treasury also states that offering announcements include auction date and competitive/noncompetitive closing times. Historical announcements show 5-Year Note competitive close as 1:00 p.m. ET in ordinary and special/holiday schedules, but the event-level PDF remains authoritative.

## Frozen execution test

EVENT_TIME `T` = event-level competitive close from original Treasury announcement.

- PRE: **short ZF**. Entry = first valid BBO at/after `T-180m`, maximum +60s. Exit = last valid BBO **strictly before T**, maximum age 60s.
- POST: **long ZF**. Entry = first valid BBO at/after `T+10m`, maximum +60s. Exit = first valid BBO at/after `T+180m`, maximum +60s.
- No midpoint executions. Short sells at bid and buys back at ask. Long buys at ask and sells at bid.
- ZF point value = $1,000. Explicit fee assumption is frozen at **$3.00 per side per contract** in addition to the observed BBO spread. This is a conservative research cost assumption, not a claim about any specific broker tariff.
- Missing endpoint BBO makes that event unusable; no stale fill, interpolation, midpoint substitution or endpoint widening is allowed after outcome exposure.

### Contract selection / roll rule

Use an individual ZF March/June/September/December contract. Select the **earliest quarterly delivery month whose first calendar day is at least 14 calendar days after the auction date**. This is deterministic and uses no future price/volume/open-interest information. It approximates the documented Treasury-futures roll, where most open interest migrates during the final ~10 business days before the delivery month, while avoiding a hindsight volume-based roll.

### Exclusions

Only these predeclared exclusions are allowed:

1. Treasury source row fails required-field or original-announcement validation.
2. Auction lies outside the frozen universe/period.
3. Market data have a gap such that any frozen executable BBO endpoint is unavailable within 60 seconds.
4. Exchange data explicitly mark the selected contract unavailable/halted at a required endpoint.

Macro-news overlap, realized auction quality, result fields, volatility, return sign, liquidity observed after the fact, or any post-result instrument identity change are **not** exclusion reasons.

### Statistics and decision

Primary observation = one auction event with PRE, POST and COMBINED net USD per one-contract leg.

Report: event count, usable ratio, PRE mean net USD, POST mean net USD, COMBINED mean/median/sign-rate, and Newey-West t-statistic with frozen lag 3 on COMBINED net USD. Also report the frozen recent slice 2025-01-01 through 2026-09-30.

- `BLOCKED_DATA_QUALITY` if <90% of manifest events have all four executable BBO endpoints.
- `KILL` if PRE mean <=0, or POST mean <=0, or COMBINED mean <=0, or recent-slice COMBINED mean <=0.
- `KEEP_AS_RESERVE` if all those directional means are >0 but COMBINED Newey-West t <1.645.
- `PROMOTE_TO_EXPERIMENT_DESIGN` if all those directional means are >0 and COMBINED Newey-West t >=1.645.

These choices are frozen before historical ZF outcomes are read. No window, cost, roll, exclusion or statistical threshold tuning is permitted after outcome exposure.

## Market-data access gate

`MARKET_DATA_ACCESS = PAID_REQUIRED`

Current worker environment has no `DATABENTO_API_KEY`, no Databento client and no ZF history in the repository. Databento historical access requires an API key and is usage-billed; first-account promotional credits do not constitute already-authorized access. Other discovered ZF intraday/Level-1 vendors are also paid. No free source with 2015-2026 historical executable BBO coverage was identified.

Therefore the harness is prepared and synthetically testable, but **the historical test must not execute in this session**.

## Outcome-blind readiness verification (2026-10-08)

Treasury source checks completed before any ZF return read:

- Auction Query / historical press-release archive: nominal securities history and original announcements available for the frozen period.
- Announcement date, auction date, reopening flag and CUSIP are represented by Treasury metadata; event-level original announcement remains authoritative for competitive close.
- Original announcements/special schedules explicitly publish competitive closing time in ET; the harness refuses a timestamp without explicit `ET` and converts through `America/New_York` so EST/EDT differ correctly.
- No result-only auction field is required to build the event manifest or choose a contract.

Current market-data environment check:

- `DATABENTO_API_KEY`: absent.
- Databento Python client: absent.
- Repository ZF historical BBO dataset: absent.
- Free historical 2015-2026 ZF top-of-book/BBO source found: none.
- Access classification: `PAID_REQUIRED`.

Synthetic verification command (outcome-free):

`pytest -q tests/test_treasury_auction_zf_outcome_blind.py`

Result: `9 passed`. Covered: DST, reopening retention, malformed/ambiguous timestamp rejection, deterministic contract roll, missing BBO rejection, PRE no-look-ahead boundary, PRE-short/POST-long executable-side arithmetic with fees, announcement-before-entry invariant, deterministic manifest/digest.

`READY_TO_EXECUTE = FALSE` in the current worker only because authenticated/paid historical executable ZF BBO data are not already available. No historical return was read.
