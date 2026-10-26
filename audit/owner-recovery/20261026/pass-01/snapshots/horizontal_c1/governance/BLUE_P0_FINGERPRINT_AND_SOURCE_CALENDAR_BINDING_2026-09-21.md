# BLUE — P0 FINGERPRINT + SOURCE-CALENDAR AUTHORITY BINDING — 2026-09-21

## 0. Status

`ACQUISITION_CRITICAL_FINGERPRINT_REPOSITORY_CLOSURE = CLOSED_FOR_FROZEN_V4_LINEAGE`

`SOURCE_CALENDAR_AUTHORITY_VERSION = BOUND_FOR_2026_FROZEN_V4_LINEAGE`

`TARGET_HOST_RUNTIME_BINDING = NOT_ESTABLISHED_BY_THIS_DOCUMENT`

This document closes two promotion-checklist lineage/binding items only. It does
not establish target-host readiness, Gate B, t0, Gate C, scientific validity,
economic readiness, or capital authority.

## 1. Frozen lineage

Frozen production candidate:

`4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072`

Git tree:

`4d15ef6f471213ee6ab56337b555d2906ef9bf16`

Exact V4 repository verification run:

`35536353538 = COMPLETED / SUCCESS`

Verified input-tree digest:

`sha256:ceaa2a1801e96a51dc8c86ea087a3a113d15aa757fbed0b7415129c157c231f2`

Independent V4 audit:

`astra/p0-gate-a-v4-independent-audit-2026-09-20@afe25984b0ddd261fda143d858106c3c71e45149`

Verdict:

`AUDIT_GATE_A_V4 = PASS_REPOSITORY_CORRECTION`

## 2. Acquisition-critical fingerprint authority

Contract:

`governance/P0_ACQUISITION_CRITICAL_FINGERPRINT_V1.md`

Frozen-V4 blob:

`4f8b6eda87507e170f8d9f0840926d79e318e140`

Implementation:

`src/quant/dataplane/sec/fingerprint.py`

Frozen-V4 blob:

`b3ea2aa9379e7354bf7d51590eebf5e66e2503f0`

Primary regression/mutation suite:

`tests/test_sec_form4_capture.py`

Frozen-V4 blob:

`2ce6e0d770329949b8811efadeb2e7c483fbb34a`

Independent/adversarial suite:

`tests/test_astra_pre_t0.py`

Frozen-V4 blob:

`01a15c32d846bd5aac34ed932e197d588ed0f32f`

Repository evidence covers, among other things:
- deterministic fingerprint generation;
- complete policy-field classification with generation-time fail closed;
- stable non-plaintext requester identity binding;
- timeout/backoff/retry/discovery/drain policy sensitivity;
- critical module mutation sensitivity;
- supervisor/restart-policy sensitivity;
- effective runtime configuration sensitivity;
- one budget reservation / one network request / one durable attempt discipline;
- no hidden retry bypass;
- lifecycle/service-start fingerprint recording;
- mid-window fingerprint-change detection;
- materialized-fingerprint mismatch blocking;
- effective-unit digest binding and V4 stability against mutable systemd runtime observations.

Conclusion:

`ACQUISITION_CRITICAL_FINGERPRINT_REPOSITORY_CLOSURE = CLOSED_FOR_FROZEN_V4_LINEAGE`

This means the repository-level fingerprint contract is bound to the exact
frozen V4 lineage. It does NOT mean the future target host has materialized the
same fingerprint or loaded the same effective systemd definition. Those remain
Gate-B evidence.

## 3. Source-calendar authority

Frozen calendar implementation:

`src/quant/dataplane/sec/calendar.py`

Frozen-V4 blob:

`b4fbd58b381e01ec882b60386cf73d4017e7db5c`

The file prospectively binds the 2026 EDGAR closed dates and fails closed for an
unbound calendar year.

The source metadata embedded in the frozen code identifies:

`https://www.sec.gov/submit-filings/filer-support-resources/edgar-calendar`

and the 2026 federal-holiday closure set.

Blue independently rechecked the official SEC EDGAR Calendar on 2026-09-21.
The official 2026 closed dates matched the frozen code's 2026 set:
- Jan 1;
- Jan 19;
- Feb 16;
- May 25;
- Jun 19;
- Jul 3;
- Sep 7;
- Oct 12;
- Nov 11;
- Nov 26;
- Dec 25.

The SEC's official EDGAR guidance also states filing availability is
06:00–22:00 ET Monday–Friday except federal holidays and that EDGAR is closed
outside those hours, on weekends and federal holidays.

## 4. Calendar semantics bound in V4

Collector implementation:

`src/quant/dataplane/sec/collector.py`

Frozen-V4 blob:

`dd301dab4de08719293ef35df02164e9d663248a`

Repository semantics include:
- timezone: `America/New_York`;
- EDGAR business-day close hour: `22`;
- daily-index settle delay: `30 elapsed hours` after source close;
- business-day authority from the prospectively bound calendar;
- no inference of a holiday from an HTTP failure.

Calendar-compression regression suite:

`tests/test_p0_continuity_compression.py`

Frozen-V4 blob:

`8586c7d7496f9f68ef39cf7547a197d3a3a5a684`

It discriminates:
- Friday/weekend/Monday boundary;
- 30h settlement from 22:00 ET rather than UTC-date start;
- Eastern-date bootstrap;
- known 2026 SEC holiday;
- fail-closed unbound future year;
- HTTP outcome cannot define holiday status;
- spring/fall DST elapsed-time behavior;
- direct/CLI reconcile cannot bypass settlement;
- virtual P14D horizon calendar behavior.

Conclusion:

`SOURCE_CALENDAR_AUTHORITY_VERSION = SEC_EDGAR_CALENDAR_2026 / FROZEN_V4_BLOB_b4fbd58b381e01ec882b60386cf73d4017e7db5c`

The authority is valid for the bound 2026 calendar encoded in frozen V4. A
future unbound year must fail closed and requires a new prospective calendar
binding before qualification can rely on it.

## 5. Promotion-checklist effect

The following repository-lineage items may now be treated as closed:

- acquisition-critical fingerprint closure;
- applicable source-calendar authority version.

They close only the repository/binding dimension.

Still required:
- restart-burst proof repair exact-head CI;
- targeted independent Astra recheck;
- Blue final fault-matrix disposition;
- final consistency/promotion decision;
- actual target-host Gate B after any promotion.

## 6. Safety

`P14D_GOVERNANCE_STATUS = STILL_FROZEN / NOT_YET_AMENDED`

`P14D_PROMOTION_READY = FALSE`

`TARGET_HOST_READY = FALSE`

`GATE_B_MUTATION_AUTHORIZED = FALSE`

`GATE_B = NOT_STARTED`

`t0 = NOT_DECLARED`

`REAL_CAPITAL_AUTHORIZED = FALSE`
