# WTI producer hedging pressure — L0 source decision, 2026-10-12

**Decision: PARK_DATA for a spot-only implementation of the futures-premium
hypothesis.** The mechanism is not economically rejected. Public position data
are accessible, but a cash-price change alone omits the forward discount, roll
and basis through which hedging compensation can accrue. This pass qualified
one distinct L0 candidate; it did not execute or promote an economic expression.

## Required prospective odd-lot check, performed first

The existing `disc-us-issuer-oddlot-priority-prospective-l1-v1.md` was present at
remote HEAD `29f4ee22f72bbe11f0539c80cae868b6de5a384b`. Its SHA256 is
`a8efaae4f5d0865c2886ae644ce89ddc4efbffb98518a3652fb8250f7792689c`.
`PROSPECTIVE_T0=2026-10-12T20:00:00Z` had passed at the observed clock
`2026-10-12T20:20:43Z`.

One [SEC current-filings Atom query](https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%20TO-I&company=&dateb=&owner=include&start=0&count=100&output=atom)
at `2026-10-12T20:21:50.536135Z` returned HTTP 200, 2,816 bytes, four entries.
Their `updated` timestamps ranged from `2026-10-08T08:24:31-04:00` to
`2026-10-09T16:24:50-04:00`; none was after T0. Response SHA256:
`c0445e64cd21a37c863fa42ab9f5b7310b09364169664c3885bc7e9a0141eb88`.
Limit: 100 entries, 1 MiB, 25 seconds, no retry; observed wall time 0.622s.

**No post-T0 candidate was observed in this bounded feed; none was selected or
claimed.** Feed `updated` is not asserted to be EDGAR `accepted`, and this
snapshot does not prove complete SEC coverage or rule out a later arrival.
No filing exhibit, price payload, entry price or completion outcome was read
for the prospective case. Anebulo and all previously exposed issuers remain
ineligible. The future first chronological selection must still establish
coverage, exact `accepted` time and every frozen eligibility requirement before
claim/selection evidence is published. No historical substitute was used.

## New L0 question and mechanism

Family: `wti-producer-hedging-pressure`; cluster: commodity-producer-risk-transfer.
Question: can publicly observable producer/merchant net short pressure identify
compensation to investors bearing crude-oil price risk after publication and
costs? Physical producers wanting more certain future cash receipts are the
hypothesized payers; constrained risk-bearing capacity is the proposed reason
the compensation could persist. This is a prior economic explanation, not a
verified motive for each reported trade or a measured return premium.

This is distinct from crypto funding carry, VX volatility insurance, Treasury
auction inventory pressure, ETF B2/B4 and French fuel-price dissemination.
No closed expression is renamed. Broad hedging-pressure theory is already
public knowledge; no novelty or independent confirmation is claimed.

## Primary source evidence, scope and contradictions

- [CFTC COT documentation](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm),
  observed 2026-10-12, current report label October 6, 2026, FAQ 5 and 12–13:
  disaggregated histories and tokenless, reasonably bounded API use are
  documented. Tuesday positions generally become public Friday at 15:30 US
  Eastern; holidays alter the schedule. Only 13 months of release dates are
  listed. Trader categories reflect business classification, not each trade's
  motive. Thus producer-class positions mix hedging and speculation. Neither
  report date nor today's dataset update time authenticates historical
  first-public availability. These are material timing and causal limitations.
- [Official CFTC dataset catalog](https://publicreporting.cftc.gov/api/views/metadata/v1/72hh-3qpy),
  HTTP 200: `72hh-3qpy` = `Disaggregated - Futures Only`, provenance OFFICIAL,
  category Commitments of Traders. `dataUpdatedAt=2026-10-09T19:30:08+0000`;
  metadata updated 2022-09-21. Its description identifies producer/merchant,
  swap-dealer, managed-money and other-reportable categories. Catalog SHA256
  `4b29a31922771ae5acf77b3ef7264863bb6dc5585fcb5daadcac0b4e960d2795`,
  2,238 bytes. No positions were requested. The catalog's license field is null;
  public access is not a fabricated open-license identifier.
- [CFTC CSV route](https://publicreporting.cftc.gov/resource/72hh-3qpy.csv?$limit=0):
  HEAD HTTP 200, `text/csv`, last modified October 9 at 19:30:07 GMT; zero body
  bytes. This verifies route availability, not WTI coverage, contract mapping,
  row uniqueness, schema adequacy or a complete point-in-time history.
- [EIA RWTCd workbook route](https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls):
  HEAD HTTP 200, Excel content type, content length 471,040, last modified
  October 7, 2026 at 13:16:46 GMT; zero body bytes. The workbook was not opened.
- [EIA definitions and source notes](https://www.eia.gov/dnav/pet/TblDefs/pet_pri_spt_tbldef2.asp),
  read 2026-10-12: WTI Cushing is a physical spot marker; data source is
  Refinitiv, an LSEG business. EIA describes daily closing spot prices and
  unweighted aggregates. A cash marker is not a futures total return or an
  executable bid/ask series.
- [EIA reuse policy](https://www.eia.gov/about/copyrights_reuse.php), read
  2026-10-12: EIA permits use of its government information with acknowledgment
  while distinguishing protected third-party materials. Do not infer that the
  LSEG-sourced series has unrestricted redistribution rights. Dataset-specific
  terms remain a qualification item; no extraction restriction was bypassed.

The [CFTC explanatory notes](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm)
were also read, including illustrative positions and classifications, not a
WTI observation series. A PRE user-guide link and an alternate EIA notes URL
were unavailable in the browser and were not retried. No study performance,
WTI price history, position rows, returns, signal correlation or P&L was read or
calculated. Source examples and the public theory count as documentary/selection
exposure; PRIVATE_UNKNOWN and historical N/M remain unchanged.

## Decision consequence and next

Do not spend a look testing the full futures hedging-premium hypothesis against
cash returns alone. That could discard a premium paid through the curve or
mislabel ordinary oil beta as alpha. This is a proxy-adequacy decision before
outcomes, not evidence of zero economic compensation.

On the next pass, the owner's prospective odd-lot check still comes first.
If it yields no admissible event, the single useful follow-up is a bounded
documentary check of **one free WTI futures settlement/contract-calendar route**
that could supply a declared, dated long-futures holding/roll return. Use at
most three primary metadata requests and 15 minutes; zero retries, zero price
payloads, no account or purchase. Reuse the source evidence above instead of
repeating CFTC/EIA probes. If no distinct usable route is established, leave
this implementation PARK_DATA and choose another causal L0; do not substitute
spot, ETF or another commodity outcomes. If usable, the next action is a linked
L1 declaration with release clock, fixed exposure/holding rule, costs, adequate
sample, benchmark and one contradiction, followed by CAS claim before data.

## Receipt

- RESULT: PARK_DATA for the spot-only WTI hedging-premium implementation;
  source access established but proxy adequacy failed before outcomes.
- EFFECT_SIZE: Not estimated.
- UNCERTAINTY: Actual hedging motive, publication history, futures basis/roll,
  executable costs and dataset-specific licensing.
- POWER_LIMITATION: L0 documents/headers only; no statistical sample or test.
- ECONOMIC_SIGNIFICANCE: Potential risk-transfer compensation; neither positive
  net economics nor retail capturability established.
- FAILED_CRITERIA: Cash series does not identify futures total return;
  complete qualified futures/clock/cost package absent.
- LESSON: Access to two free series does not make their pairing a valid test of
  the proposed economic payoff.
- FAMILY_STATUS: New L0 reserve; spot implementation PARK_DATA, mechanism
  untested. No new active economic execution and no V3 admission.
- NEXT_DECISION: Mandatory odd-lot check, then one bounded futures-route
  qualification if no admissible event; no outcome access in that task.

Observed direct HTTP cost: four requests (one SEC feed GET, one catalog GET,
two HEADs), 5,054 response-body bytes total, no retries. Respective wall times:
0.622s, 0.989s, 0.643s and 0.797s. Browser: three calls, five opens, one failed
link click and two cached-document finds; origin bytes are not exposed.
Paid spend 0 USD; tokens/global bill/total CPU NOT MEASURED. Source caches remain
private; only this decision and metadata proof are published. No code, dashboard,
automation or governance changes.

Initial CONTROL digest:
`a9998e826eb4afa5b19578ed8da92cce52ab88a5f435e4c48629f299210cc342`.
paused=false, real_capital_authorized=false, live_trading_authorized=false.
Concurrent branch advances are reconciled before publication; no source probe
or calculation is repeated when refreshing the publication parent.

Publication parent (fresh HEAD + CONTROL rechecked): `06bee90a0d5822f710cad7c8140a6722f512f6cc`.
