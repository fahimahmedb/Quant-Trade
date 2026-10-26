# Pre-price implementation challenge — version 1

These notes resolve implementation details of the immutable preregistration at
df8ecb32c2a5a84b42f0609c223aefe2f1591c07. No market archive/row or result was used.
Windows, signal parameters, costs, thresholds, primary and comparisons are
unchanged. Original design-status fields in manifest.json/challenge.json are
historical snapshots; the complete code freeze is freeze.json plus
HARNESS_CHALLENGE.json. No new confirmatory alpha is allocated.

* ADX is the entry gate. Exits are the registered stop, target, elapsed time,
  cutoff, staleness and capital-risk rules. Price triggers use the source
  liquidation side; stress changes fill/mark costs. All triggered closes stay
  pending until executable under the assumed proxy clock. Stops override a
  pending add or optimistic target; earlier close eligibility is preserved.
* Basket age starts at first fill. A quote exactly five seconds after the
  previous group is fresh; a longer gap triggers the already-known timer at
  five seconds. Intent time and underlying source quote time are distinct.
  A closing order can remain open across calendar days/rollovers.
* Gross exposure is checked against equity after all prospective opening and
  liquidation costs, including the new rung. An opening cost can itself cross
  the 5% drawdown boundary and starts the adverse close immediately. Each path
  stops on its risk event; the family risk screen records failures in any of
  the six registered paths. Losses are never clipped to planned budget.
* Binary subtraction of decimal bid/ask can misclassify exactly one pip. Only
  the source spread comparison rounds to 12 decimal USD/EUR places. It does
  not change the one-pip economic threshold, costs or minimum risk budget.
* The 433 weekday return intervals retain intervening weekend P&L/financing in
  the next weekday return. The separate calendar NAV ledger and residual units
  retain failed exits. Cash hurdle is an assumed simple 4% times calendar years;
  its excess is reported, without adding a new success test.
* CSV is strict four-column ASCII. One exact optional DateTime,Bid,Ask,Volume
  header is accepted. Asset/month come from the pinned member/request; only
  DAT_ASCII_EURUSD_T_YYYYMM.csv or HISTDATA_COM_ASCII_EURUSD_T_YYYYMM.csv is
  accepted. Source time is validated before prices; post-window source-local
  September rows are counted but their prices cannot enter the calculation.
  No sorting/forward fill. All ZIP members receive CRC checks.

Runner procedure after public freeze and successful synthetic CI:

1. Preserve active Actions and local captures. Run capture.py only when clear.
   It follows the 21 declared free forms sequentially, stops on access errors,
   verifies any supported advertised checksums, saves compressed hash/origin
   proof before rename and reuses complete identical files. No ZIP member read.
2. Publish the complete capture certificate/raw hashes. Reconcile all local,
   artifact, public and run-log stores for prior FX exposure. Atomically CREATE
   the unique preregistered ref with the frozen commit; save the creation receipt
   in capture-v1/reservation.json (schema, ref, frozen_commit, freeze_sha256,
   atomic_create_receipt=true). Never use update_ref or a F1 reservation.
3. Run run.py once, fixed source/output roots. Its remote claim and local
   exclusive attempt/result gates precede price access. Past calibration state
   is persisted before the first outcome quote reaches simulation. Code,
   timezone dependency and captured bytes are checked before and after.
4. Publish exact result JSON/hash, six paths, paired diagnostics, source/risk
   failures, residual losses and all nine fields; update checkpoint once.
   A printed/saved/partial/source-failed outcome is retained and blocks replay.

An infrastructure resume needs a published PR22 no-outcome review certificate
bound to the original attempt hash/ref/commit, explicitly checking artifact,
log, local and public stores. It is never automatic. Existing calibration is
identity-checked and never overwritten. Synthetic JSON state restart is tested;
production does not checkpoint partial economic P&L as a replayable result.
Positivity remains a quote-proxy screen needing broker/delivery/execution
authentication, never confirmation, survival or live authority.
