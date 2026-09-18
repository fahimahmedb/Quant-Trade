# Next Build Mission — P0 SEC / Form-4 Durable Raw Capture

This is the next Builder milestone.

Before acting, read `QUANT_NORTH_STAR.md`, `STATE.md`, and:
- `governance/P0_RAW_CAPTURE_CRITICAL_PATH_RECLASSIFICATION_2026-09-18.md`
- `governance/BLUE_P0_RAW_CAPTURE_CHECKPOINT_ADDENDUM_2026-09-18.md`

Do not reopen Route-B scientific specification as part of this mission. The current decision is:

`P0_RAW_CAPTURE_BLOCKER_STATE = NO_SCIENTIFIC_BLOCKER_IDENTIFIED`

`P0_IMPLEMENTATION_GAP = TRUE`.

## Mission

Build and start the smallest durable SEC/EDGAR Form-4 raw-capture slice that preserves the evidence that cannot be reconstructed later.

The mission is acquisition, not scientific analysis.

The first successful live run must not wait for:
- liquidity thresholds;
- ADV window selection;
- lambda / breach UCB;
- K_forward / M_economic / BEEE / MEUE;
- final D05/D07/D19 mechanics;
- Form-4 parsing / qualification / event construction.

## Day-1 non-negotiable properties

### 1. Exact immutable raw bytes

For every captured SEC response:
- preserve the exact response body bytes received;
- hash the exact bytes with SHA-256;
- record byte length;
- store append-only / content-addressed or otherwise prove no overwrite;
- never normalize, parse, or rewrite the raw object in place;
- preserve transport metadata needed to establish whether the stored body is complete, including Content-Encoding / Content-Length / transfer outcome where available;
- never silently hash a transparently decompressed representation when the mission requires the exact received body bytes.

Derived files may be added later. They must reference the raw object, not replace it.

A truncated/incomplete transfer must be recorded as incomplete/error evidence, never promoted to a valid raw capture.

### 2. Local acquisition envelope

For every request attempt, append a durable record containing at least:
- source/request locator;
- `request_attempted_at_utc`;
- `response_received_at_utc` when applicable;
- HTTP/result state;
- raw-object SHA-256 when bytes were received;
- byte length;
- collector version / git commit;
- attempt id.

SEC publication/acceptance time is a distinct source field. Never substitute it for local receipt time.

Historical backfill acquired today must retain today's local receipt time.

### 3. Attempt / heartbeat journal

Every scheduled poll must leave an append-only liveness record even when:
- no new filing exists;
- the request fails;
- the source rate-limits;
- parsing/discovery fails after the poll.

A later reviewer must be able to distinguish:
- no new source item;
- collector alive but request failed;
- collector did not run.

The complete gap-reconciliation engine may follow later, but the raw attempt history begins on the first live run.

## SEC access policy — freeze before first live request

Before the first live run, re-check the current authoritative SEC fair-access documentation.

As verified by Blue on 2026-09-18, current SEC guidance states:
- automated access is allowed subject to fair-access/security policy;
- total traffic must remain at or below 10 requests/second;
- scripted requests should declare a User-Agent identifying the requester and a contact email;
- efficient/moderate scripting is expected;
- SEC may throttle/block excessive automated access.

Builder must fail closed if the required User-Agent/contact configuration is absent.

### Initial collector traffic policy

Use a deliberately conservative policy, not the SEC maximum:

- discovery poll cadence: **60 seconds** while the collector is enabled;
- global SEC request concurrency: **1**;
- steady-state request rate cap: **2 requests/second** across all SEC endpoints used by this collector;
- no burst above the configured cap;
- queue newly discovered filings and drain sequentially under the same limiter;
- no retry loop may bypass the global limiter.

These are implementation defaults for safe acquisition, not scientific parameters.

The limiter must be designed as a **global SEC traffic budget**, not merely a local P0 loop limit, so future/parallel SEC consumers cannot collectively exceed the frozen policy.

If SEC guidance changes before first live run, update the implementation policy to comply **before** making requests and record the authoritative source/version consulted.

### Retry / backoff policy

Freeze before first live run:

- network timeout / transient network failure / HTTP 5xx:
  retry with bounded exponential backoff and jitter;
- HTTP 429 or an SEC rate-control response:
  stop ordinary draining immediately and enter rate-limit backoff;
- HTTP 403 plausibly caused by automated-access controls:
  stop aggressive retry; record the event and enter extended backoff / BLOCKED state;
- permanent 4xx other than rate-control cases:
  record and do not hot-loop.

Initial bounded backoff schedule:

`5s -> 15s -> 60s -> 5m -> 15m`

with jitter and a durable attempt record for every retry.

Honor `Retry-After` when supplied and never retry sooner than the authoritative cooldown.

Persist any active cooldown/backoff state across restart.

Use finite network connect/read deadlines so a hung request cannot silently stall liveness.

Never increase request rate automatically to catch up after downtime. Backlog drains under the same global limiter.

## Source discovery and raw capture

Use an authoritative SEC/EDGAR public discovery mechanism suitable for current Form-4 filings and then retrieve the associated filing/raw documents from SEC-hosted endpoints.

Builder may choose the exact SEC endpoint after verifying current official documentation and response semantics. Prefer the simplest source that:
- exposes current filings reliably;
- supplies stable accession/source identity;
- allows deterministic retrieval of the filing package/raw document;
- can be polled under the fair-access policy.

Do not introduce paid data or credentials.

Record the exact endpoint class and discovery semantics in implementation documentation and tests.

### P0 blocker: prove discovery semantics before accepting NO_NEW_DATA

A transport-level HTTP success is not sufficient evidence of a successful discovery poll.

Before production `NO_NEW_DATA` may be emitted, Builder must prove the discovery path end to end using a known Form-4 fixture/reference:

`discovery response -> Form-4 identification -> stable source/accession identity -> raw document locator -> raw document bytes`.

Tests must reject as ERROR/BLOCKED rather than `NO_NEW_DATA`:
- unexpected HTML/error pages returned with nominal HTTP success;
- structurally invalid discovery payloads;
- a discovery parser/filter configuration that cannot surface known Ownership/Form-4 filings;
- missing required continuation/pagination metadata;
- any source response whose semantics cannot establish that the query completed correctly.

Perform the first real SEC probe as soon as this functional slice exists, before optional hardening. Persist only opaque operational proof on Blue-visible surfaces.

### P0 blocker: coverage continuity must never be silently inferred

A healthy heartbeat proves collector liveness, not complete coverage of a bounded/paginated discovery source.

From Day-1:
- preserve exact raw discovery responses as immutable raw objects under the same visibility firewall;
- record the discovery coverage/window/pagination metadata supplied by the chosen endpoint;
- traverse all required pages/continuations available for that poll under the same global limiter;
- bind every discovered filing task to the discovery object/page that produced it;
- maintain a durable last-validated coverage/cursor state.

If the collector cannot establish continuity from the last validated poll through the current discovery result, record:

`COVERAGE_UNKNOWN`

with the affected interval/cursor/page range.

Never report complete coverage merely because the poll returned successfully.

The full backfill/reconciliation engine may remain later work. Day-1 only requires truthful detection and durable recording of unknown coverage.

Tests must include:
- discovery window overflow / more items than one page can hold;
- missing/interrupted intermediate page;
- restart during paginated discovery;
- a successful heartbeat with unresolved coverage, which must remain `COVERAGE_UNKNOWN`.

## Visibility firewall

P0 capture does **not** authorize scientific-content visibility.

Operational status surfaces may expose only opaque acquisition telemetry such as:
- collector RUN / IDLE / BLOCKED;
- last successful poll time;
- last attempt time;
- error/rate-limit state;
- opaque object id / SHA-256;
- byte length;
- storage health;
- outage duration;
- opaque coverage state such as COMPLETE / COVERAGE_UNKNOWN, without filing counts or identifying content.

Do not expose to protocol-mutating actors:
- raw Form-4 body/content;
- parsed transaction fields;
- filing title/issuer/owner identity;
- filing-specific URLs/accession strings when they reveal scientific content;
- filing counts by period/issuer/owner/form subtype;
- transaction-code distributions;
- qualification/event/crossing counts;
- any scientific aggregate;
- raw-response excerpts in exceptions/logs/CHIEF_BRIEF/status.

Tests may inspect fixtures needed to verify byte preservation and parser-independent plumbing, but the production status surface must not publish interpretable Form-4 content.

## Crash/restart commit discipline

Discovered work must be recoverable from durable state.

A filing/task may not be acknowledged/advanced beyond recoverable state before:
1. the raw bytes have been durably persisted when acquisition succeeded; and
2. the corresponding immutable acquisition envelope has been durably persisted.

Crashes between raw-object write, envelope write, task acknowledgement and cursor advance must be recoverable without silent loss or substitution.

Tests must include interruption/crash at those boundaries, plus disk-full/write-failure behavior.

On restart:
- already persisted identical raw objects may be deduplicated by immutable identity;
- an uncommitted/incomplete acquisition must be retried safely;
- active SEC cooldown/backoff must remain in force.

## Progressive hardening after capture starts

Once the irreversible Day-1 path is running, continue without stopping capture to add:
- richer durable manifest schema;
- formal gap/reconciliation/backfill engine;
- broader source-package completeness checks;
- Data Plane registry integration;
- parser/normalizer kept downstream of raw storage;
- explicit `CAPTURED / VISIBLE / ADMISSIBLE` state separation.

The minimal durable discovery cursor/coverage state and crash-safe task recovery required above are **not** deferrable.

Historical raw objects and original acquisition envelopes must never be rewritten during hardening.

## Integration with Quant

Reuse the existing persistent architecture:
- Control Plane clock / long-running `serve` mode;
- EventLog / heartbeat;
- Data Plane provenance/fingerprinting primitives;
- persistent state and status surfaces;
- capability-gap unblocking.

Do not create a separate one-off collector process if the existing Control Plane can own its lifecycle coherently.

The collector must survive restart without losing historical attempt/raw-object/coverage state or duplicating/mutating already-captured objects.

## Tests required before live enablement

At minimum prove:

1. exact byte identity survives store/reload;
2. duplicate identical response does not overwrite prior evidence;
3. same source identity with different bytes creates explicit version/conflict evidence rather than silent replacement;
4. request-attempt and receipt timestamps are distinct and durable;
5. no-new-data poll leaves a heartbeat/attempt record;
6. known Form-4 fixture proves discovery -> raw-document path;
7. invalid/HTML/unexpected discovery response cannot become `NO_NEW_DATA`;
8. pagination/window overflow cannot silently become complete coverage;
9. missing page produces durable `COVERAGE_UNKNOWN`;
10. simulated timeout/5xx follows bounded backoff;
11. simulated 429 honors limiter and `Retry-After`;
12. simulated 403 does not hot-loop;
13. cooldown survives restart;
14. restart preserves collector, cursor, coverage state and append-only history;
15. crash between raw write / envelope / acknowledgement / cursor advance causes no silent loss;
16. disk-full/write failure cannot acknowledge uncaptured evidence;
17. compressed HTTP response preserves the intended exact-byte semantics and transport metadata;
18. truncated transfer is rejected/marked incomplete;
19. production status/log/exception/CHIEF_BRIEF serialization cannot expose raw filing body, filing-identifying scientific content, or parsed scientific aggregates;
20. blocked/hung request leaves a diagnosable liveness state rather than permanent silent stall.

## First-live-run evidence required

After the functional discovery slice passes its core offline tests and current SEC policy has been rechecked:

- perform the first real SEC discovery probe **before optional hardening**;
- persist its raw discovery response and attempt/receipt envelope under the visibility firewall;
- demonstrate that response validation distinguishes valid discovery from error/HTML/invalid payload;
- demonstrate coverage/pagination state for that probe;
- preserve the first compliant filing raw capture if a filing is discovered;
- otherwise preserve successful poll/heartbeat evidence showing the collector is live **and** discovery semantics/coverage are valid;
- show immutable raw-store structure without rendering filing contents;
- show attempt/receipt timestamps and hash metadata;
- show current request limiter/backoff/cooldown configuration;
- demonstrate restart/resume;
- update `STATE.md` and `CHIEF_BRIEF.md` from actual persistent state without exposing Form-4 scientific content.

A nominal HTTP-200 poll alone is not sufficient live proof.

The first useful signal from this mission is a collector that is actually running and whose discovery/coverage semantics are trustworthy, not another governance document.

## Scope boundary

Do not:
- analyze the Form-4 contents;
- compute Form-4 counts/statistics;
- select ADV windows;
- calibrate liquidity or execution economics;
- expose captured filing contents to Blue/protocol-mutating surfaces;
- claim scientific confirmation authority for captured data;
- add real-capital authority.

## Definition of done

This milestone is complete when Quant has a durable, policy-compliant SEC/Form-4 capture path that is actively accumulating or polling for irreversible point-in-time evidence, with immutable raw bytes, local receipt timing, liveness history, truthful discovery/coverage state, conservative request controls, crash/restart safety, and no scientific-content exposure.

If the collector is blocked by SEC/network/discovery behavior, leave the system in an explicit persistent `BLOCKED` or `COVERAGE_UNKNOWN` state with the attempt history intact rather than weakening request policy or reporting false completeness.
