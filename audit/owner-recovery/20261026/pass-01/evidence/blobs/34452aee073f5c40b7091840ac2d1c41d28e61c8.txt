# EURUSD-RANGE-GRID-001 — exploratory intraday quote-proxy screen

Version 1, written 2026-10-10 before any Quant EUR/USD archive, price row,
return or reservation. This document and `manifest.json` define one candidate,
not an optimization space. Status: DESIGN_FROZEN_EXECUTION_GATES_OPEN.
No executable edge, confirmation, independent holdout or live authority is
claimed. Owner's latest autonomous continuation supersedes the older pauses.

## Decision and mechanism

Question: does one fixed RSI re-entry rule in a past-defined low-trend state
produce positive intraday mean return after observed quote spreads and assumed
additional costs? Do bounded additions and volatility adaptation contribute
anything over the same signal without them? The proposed mechanism is temporary
price pressure followed by a rebound. RSI/ADX do not identify who pays or prove
that constraint exists. A grid changes inventory and loss shape; it creates no
spread income here. All fills are marketable, not hypothetical passive fills.

A negative screen can park this exact rule/cost model. A positive screen can
justify authenticating quotes, delivery, broker access and real execution only.
It cannot reject all EUR/USD mean reversion, validate FXStabilizer or authorize
an unregistered RSI combination. Variance prediction is a risk input, not alpha.

## Source, rights, exposure and fixed window

Use only HistData Generic ASCII EURUSD ticks, joint DateTime/Bid/Ask/Volume.
The FAQ supports personal backtesting; commercial/live/raw redistribution rights
are unestablished. Raw bytes remain outside Git. No Dukascopy automation, FXCM
403 retry, mirror, paid service, account or substituted broker fees.
Source qualification is `../scouts/eurusd_grid_source_qualification_2026-10-10.json`.
Quote time is fixed EST UTC-05 without DST: add five hours. First delivery,
sampling, broker and attainable fills are unknown; the following causal clock
is an explicitly assumed proxy clock, not authenticated market availability.

Manifest: 21 source-local months 2025-01 through 2026-09. Warmup UTC
2025-01-01 05:00 through 2025-02-01 00:00 exclusive; outcome UTC 2025-02-01 00:00
through 2026-10-01 00:00 exclusive. Source-local January also covers the start
of the UTC outcome; never classify entire January as unread calibration.
No October archive or subsequent quote may repair an end-window open position.
Catalog labels do not establish downloadable archives or actual coverage.
Private predecessor UNKNOWN, NASDAQ/B4/F1 and prior literature selection remain
spent/exposed; vendor EUR Turbo 2013–2016 and HistData 2012-02-01 examples were
seen. These dates are not proclaimed virgin and no trial/error budget resets.

## Deterministic information and single daily opportunity

Combine every group sharing a millisecond into bid=min(bids), ask=max(asks),
mid=(bid+ask)/2. Count exact duplicate rows and multirow groups. The envelope
removes ordering discretion; it is synthetic and need not be a coexisting BBO.
Do not sort nonmonotone time, choose the last equal-time row or filter duplicates
by profit. Positive finite quotes and bid<=ask are mandatory for every row.

Build UTC 15-minute mid OHLC bars [t-15m,t). A valid bar has first/last quotes
within 60 seconds of its boundaries and no internal interquote gap >60 seconds.
Never forward-fill a missing bar. At boundary t use only timestamps strictly
less than t. A missing bar resets RSI/ADX warmup and prevents a crossing across
that gap. Calculations use a contiguous valid run, including quotes outside the
entry session. Weekend/missing-bar returns do not update the variance; its last
past state persists, while indicator warmup restarts.

Wilder RSI(14): seed average gain/loss with 14 consecutive close differences,
then alpha=1/14. If both zero RSI=50; loss=0 with gain>0 gives 100. Wilder ADX(14):
TR=max(H-L,abs(H-Cprev),abs(L-Cprev)); +DM=H-Hprev only if positive and greater
than Lprev-L, otherwise zero; -DM analogously (ties both zero). Seed mean TR/DM
from 14 bars, smooth alpha=1/14; DI=100*DM/TR, DX=100*abs(DI+-DI-)/(DI++DI-),
zero denominator gives zero. First ADX is the mean of 14 defined DX values,
then smooth alpha=1/14. No indicator-library default may change these seeds.

The first eligible boundary each UTC weekday with 07:00<=t<14:00 is that day's
only opportunity, shared by all expressions and cost cases. Eligibility:
defined RSI at t and previous contiguous bar, ADX(t)<20; long if RSIprev<=30
and RSI(t)>30, short if RSIprev>=70 and RSI(t)<70. No opposite/trend module,
news exclusion or retry of a cancelled opportunity. Basket maximum age two
hours, mandatory cutoff 16:00 UTC. One basket/expression, no overlapping basket,
no new entry after that day's shared opportunity, even if another expression
closed earlier. Weekdays with no opportunity contribute zero, not missing N.

## Causal volatility, frozen expressions and risk

Log mid close returns from consecutive valid bars, in decimal M15 units.
Warmup requires >=1,000 such returns. Reference sigma=sqrt(mean(r*r)) over only
the fixed warmup. Seed EWMA with mean(r*r) of its first 96 valid returns; then
recur over later warmup returns. EWMA mean=0, lambda=0.94 **per M15 return**;
this choice is a fixed design convention, not FX-calibrated optimal memory.
For each future closed bar update s2=.94*s2+.06*r*r; its next-bar forecast is
available at t. Explicit mean/variance state only, never the legacy defaults in
`src/volatility.py`, full-outcome variance, refitting, demeaning or future seed.
Reference sigma and outcome initial state are persisted before simulation.

Exactly three expressions, all reported, no replacement winner:

1. MAIN: RSI entry, three equal-quantity adverse rungs, d=A*sigma_t,
   R=.0025*E_day*min(1,sigma_ref/sigma_t).
2. NO_ADDS: same entry, d, R, stop, target, duration and caps; one rung only.
3. STATIC_GRID: same entry and three rungs, d=A*sigma_ref, R=.0025*E_day.

A is the last closed-bar mid, fixed through the basket. Direction s=+1 long,
-1 short. Entry levels A-s*k*d, k=0,1,2; stop A-s*3*d; target A+s*d/2.
No anchor/target/stop widening or shifting, no growing rung quantity, no loss
carried into a replacement basket. Additional buys trigger on source ask<=level;
additional shorts on source bid>=level. Stops/targets use the liquidation side
(long bid, short ask). Skip the shared opportunity if source spread exceeds
min(0.0001,0.2*d), sigma/d are nonpositive, or planned quantity <1 EUR.

Initial equity USD100,000 independently for each expression/cost path. E_day is
equity at UTC day start; no basket resizing after entry. All quantities are EUR,
rounded down to whole EUR (model units, no authenticated broker lot size).
For K=3 or 1 and h_stress=0.00015 USD/EUR per side, planned loss denominator
per unit is sum_{k=0..K-1}((3-k)*d+0.0001+2*h_stress).
q=floor(min(R/denominator, E_day/(K*(A+3*d+0.0002)))). Equal q per rung.
Sizing includes a full one-pip half-spread in the stress model and costs on
every rung and exit; a delayed/gapped fill can exceed this planned risk.
At each fill reject that addition if actual cumulative entry-to-fixed-stop
loss plus already-paid costs and assumed stress exit costs would exceed R,
or marked gross notional exceeds current equity. Never resize q opportunistically.
An initial rejected fill cancels the basket. A rejected add is permanently
skipped. Gross cap 1x equity; assumed margin 1/30 of gross, free equity >=95% of
equity at an opening fill; margin and broker minimums remain model assumptions.

If any path reaches intraday marked drawdown 5% from its own running equity
peak, close adversely and disable that path for the rest of the window. Include
its remaining zero days. A gap can breach the cap: report actual excess and
reject risk feasibility; never cap reported loss at budget or margin.

## Execution, ambiguity, gaps and failed exits

Order eligibility is signal/trigger time+1,000ms. Use the first subsequent group
at or after that time, never its best quote. Entry/add deadline is eligibility
time+5,000ms; later arrivals cancel/skip. Targets are marketable closes with the
same delay, not guaranteed limit profits. Stop/time/cutoff/risk closes have no
expiry: they remain pending until an observable group, including after rollover.
If stop/invalidation occurs before a pending add is executed, cancel the add.
Only one next rung can be triggered by a group; never retrospectively execute
multiple rungs crossed inside a gap. Stop, stale-gap, margin/risk, time/cutoff,
target, then addition is the fixed priority. A pending close forbids any add.
If adverse and favorable triggers are compatible with an equal-time envelope,
the adverse close wins. Mark open losses on the liquidation side after costs.

For opening long fills use max(trigger source ask, delayed source ask); short
use min(trigger source bid, delayed source bid). Apply the cost-case spread
envelope and additional adverse slippage. Closing long sells at min(trigger bid,
delayed bid), short buys at max(trigger ask,delayed ask), then costs. Stop closes
also include the stop level in that adverse extremum. A source interquote gap
>5 seconds while exposed causes a forced stale close at last time+5 seconds,
filled no earlier than its one-second delay. Include the fixed stop in that
close's adverse price bound. It is an assumed severe feed-risk policy, not proof
of a broker fill or of an unseen market path.

At the entry boundary t, retain the last strictly earlier source group; if
t-source_time>5 seconds cancel that day's opportunity. Its price sides are
known at t, but the order intent is stamped t, not that earlier source time.
Persist both clocks. Clock-triggered time/cutoff/stale orders similarly retain
the last-known source sides and their original source timestamp separately.

Apply financing to any still-open units at every 17:00 America/New_York rollover
(DST is used **only here**, not for HistData conversion): adverse 1 pip/EUR
central, 2 pips/EUR stress, Wednesday triple, no positive swap credit. This is
assumed, not a historical broker swap schedule. Include rollover crossings,
gap length and capital exposure even though the intended cutoff is 16:00 UTC.
Crossing any rollover fails the registered intraday risk gate; it does not
erase that day's realized/marked loss. If no allowed later quote permits final
closure, preserve open units, mark adverse max(stop loss,last quote loss) plus
accrued fees/financing, label UNRESOLVED_EXIT_SOURCE_FAILURE; no eligible economic
verdict, no optimistic final close or imported October price. Neither observed
gap endpoints nor this penalty prove the true worst intra-gap loss is bounded.

## Costs: two fixed paths, both disclosed

Central: observed bid/ask envelope; extra commission 0.5 pip/EUR/side and
adverse slippage 0.25 pip/EUR/side. Stress: twice that source spread around the
same envelope mid; commission 1 pip/EUR/side, adverse slippage 0.5 pip/EUR/side.
One pip=0.0001 USD per EUR. Closing every rung pays its side costs; no netting
fees away. Marking uses prospective exit costs. Cash yield=0; no net capital
borrow beyond the assumed FX margin structure; an assumed 4% annual cash hurdle
on full equity is also reported using 365 calendar days, including weekends.
Unknown conversion/platform/holiday-swap/size-dependent fees are omitted and
disclosed. These invented design scenarios are not authenticated attainable
costs, minimum conservative broker fees or Dukascopy/FXCM historical charges.

## Source QA, statistics and frozen decisions

Fail closed on corrupt ZIP/member CRC, unexpected schema/timezone/asset/month,
nonmonotone time, invalid quote, incomplete requested archive, inconsistent
manifest/code or raw-byte changes. Exact duplicates are counted and grouped;
they do not add N. Record raw/local and UTC bounds, rows, groups, duplicates,
per-day session coverage/gaps, invalid bars and cancelled opportunities. A
weekday with less than 90% valid M15 bars in 07:00–16:00 is source-unqualified.
More than 5% source-unqualified outcome weekdays fails the source gate; do not
delete those days and proclaim a result on the survivors. Any unresolved exit
fails the source gate. Ordinary gaps do not permit deleting losing baskets.
All outcomes including source failures consume the reserved outcome exposure.

Primary estimand MAIN central net mean daily return on equity, all scheduled
weekdays included. Report all six paths (3 expressions x 2 cost cases), daily
and basket ledgers, means/Sharpe (sqrt(252), no indicator/order N), costs and
financing separately, MTM drawdown, exposure, rollover/gap/stop events, half-window
returns (split 2025-12-01 00:00 UTC), and top-10 positive-day concentration.
For means use max(Newey-West SE lags 5,20), all weekdays in order. Provide nominal
95% normal intervals, explicitly exploratory: private selection and model bias
are not corrected by them. For MAIN minus NO_ADDS and MAIN minus STATIC_GRID
central, also report paired daily differences and the same SE. These are two
prespecified diagnostics, not extra replacement strategies or confirmation.
No alpha borrowed from F1/F2/F3, reallocation or relaxation of 3.227/other gates.

Source failure -> SOURCE_GATE_FAILED, not economic rejection.
If source passes: MAIN central or stress mean<=0 -> PROXY_COST_REJECT_THIS_RULE.
Rollover crossing, actual 5% drawdown breach or margin failure ->
PROXY_RISK_REJECT_THIS_RULE (co-report any cost rejection).
Otherwise only PROXY_POSITIVE_NEEDS_EXECUTION_VALIDATION if central/stress means
are positive, central nominal 95% lower bound>0, both fixed halves positive,
>=100 completed MAIN central baskets and >=252 qualified outcome weekdays.
All other nonnegative results -> PROXY_INCONCLUSIVE. Separately, either paired
central mean<=0 -> GRID_OR_ADAPTATION_INCREMENT_UNSUPPORTED; do not replace MAIN
with a comparator. No retest with new thresholds/windows/costs. Failure to reach
the screen is not proof that smaller effects or all mean reversion are absent.
~20 months is weak Sharpe evidence even under iid days (~0.78 SR standard error,
before serial dependence); many fills do not fix low independent N. No SR goal
is optimized and no post-result variant is authorized.

## Freeze, challenge, reservation and recovery gates

Before acquisition: publish this version and the immutable manifest in PR #28
and PR #22; record hashes/commit; finish the explicit Codex design challenge in
`challenge.json`. This is not independent replication. The historical EB2
deadline/independent F1 A/B review are scoped to F1, not a waiver or a new FX
deadline. Any new contradiction holds this protocol pending a public pre-look
resolution. No numerical market result is used for the challenge.

Before any price row or economic computation: publish, synthetic-test and freeze
the complete FX harness, result schema, dependencies and reservation procedure.
This batch's safety kernel is not that complete harness. Capture ZIPs sequentially
only after no run/capture is active, using the declared page/form route; verify
provider checksum if one exists, otherwise disclose its absence and pin our raw
hash before parsing. Do not claim a nonexistent expected provider checksum.
Use existing identical archived bytes after interruption, never silently refresh.

Atomically create `refs/heads/looks/eurusd-range-grid-001-exploratory-01` with the
frozen harness/prereg/manifest commit before opening any tick row. Creation must
fail if the ref already exists (no get-then-update, force, fallback or overwrite).
Also use local exclusive result/lock and durable attempt metadata. Never use
the F1 refs. An infrastructure resume is allowed only after checking all artifact,
job-log, local-result and public evidence stores and establishing that no outcome
was printed/saved, with the original reservation preserved and a published
reason. Printed, partial, source-failed or saved outcome is exposure: retain it,
never recompute as a new attempt. Write/publish exact result, hash, limitations,
falsification, lesson and nine verdict fields before any next-family action.
