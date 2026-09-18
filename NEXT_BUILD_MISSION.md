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
- never normalize, parse, or rewrite the raw object in place.

Derived files may be added later. They must reference the raw object, not replace it.

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
- outage duration.

Do not expose to protocol-mutating actors:
- raw Form-4 body/content;
- parsed transaction fields;
- filing counts by period/issuer/owner/form subtype;
- transaction-code distributions;
- qualification/event/crossing counts;
- any scientific aggregate.

Tests may inspect fixtures needed to verify byte preservation and parser-independent plumbing, but the production status surface must not publish interpretable Form-4 content.

## Progressive hardening after capture starts

Once the irreversible Day-1 path is running, continue without stopping capture to add:
- durable manifest schema;
- formal gap/reconciliation ledger;
- restart/resume cursor;
- backfill/reconciliation worker;
- source-package completeness checks;
- Data Plane registry integration;
- parser/normalizer kept downstream of raw storage;
- explicit `CAPTURED / VISIBLE / ADMISSIBLE` state separation.

Historical raw objects and original acquisition envelopes must never be rewritten during hardening.

## Integration with Quant

Reuse the existing persistent architecture:
- Control Plane clock / long-running `serve` mode;
- EventLog / heartbeat;
- Data Plane provenance/fingerprinting primitives;
- persistent state and status surfaces;
- capability-gap unblocking.

Do not create a separate one-off collector process if the existing Control Plane can own its lifecycle coherently.

The collector must survive restart without losing historical attempt/raw-object state or duplicating/mutating already-captured objects.

## Tests required before live enablement

At minimum prove:

1. exact byte identity survives store/reload;
2. duplicate identical response does not overwrite prior evidence;
3. same source identity with different bytes creates explicit version/conflict evidence rather than silent replacement;
4. request-attempt and receipt timestamps are distinct and durable;
5. no-new-data poll leaves a heartbeat/attempt record;
6. simulated timeout/5xx follows bounded backoff;
7. simulated 429 enters rate-limit backoff and never exceeds the limiter;
8. simulated 403 does not hot-loop;
9. restart preserves collector state and append-only history;
10. production status serialization cannot expose raw filing body or parsed scientific aggregates.

## First-live-run evidence required

After tests pass and current SEC policy has been rechecked:

- run the collector against SEC;
- preserve the first compliant raw capture if a new filing is observed;
- otherwise preserve successful poll/heartbeat evidence showing the collector is live;
- show immutable raw-store structure without rendering filing contents;
- show attempt/receipt timestamps and hash metadata;
- show current request limiter/backoff configuration;
- demonstrate restart/resume;
- update `STATE.md` and `CHIEF_BRIEF.md` from actual persistent state.

The first useful signal from this mission is a collector that is actually running, not another governance document.

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

This milestone is complete when Quant has a durable, policy-compliant SEC/Form-4 capture path that is actively accumulating or polling for irreversible point-in-time evidence, with immutable raw bytes, local receipt timing, liveness history, conservative request controls, restart safety, and no scientific-content exposure.

If the collector is blocked by SEC/network behavior, leave the system in an explicit persistent `BLOCKED` state with the attempt history intact rather than weakening request policy.
