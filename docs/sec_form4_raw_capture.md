# SEC / Form-4 P0 Durable Raw Capture

This is a Data Plane acquisition capability. It preserves irreconstructible SEC/EDGAR
evidence before any Form-4 scientific interpretation exists. It does not parse
transactions, produce insider statistics, unblock research by itself, or grant data
confirmation authority.

## Current SEC access contract

The live collector uses the SEC Latest Filings Atom feed filtered to Form 4 for
discovery, then retrieves the SEC-hosted complete submission text. The endpoint classes
are recorded separately:

- `sec_latest_filings_atom_form4`: discovery/liveness response.
- `sec_complete_submission_text`: complete disseminated filing response.

The policy was rechecked on 2026-09-18 against SEC Developer Resources and Accessing
EDGAR Data. The SEC states that scripted access should be efficient/moderate, requests
must identify the requester through User-Agent, and total traffic must remain at or
below 10 requests/second. Quant deliberately freezes a stricter first-live policy:
60-second discovery polling, global concurrency 1, steady no-burst 2 requests/second,
and sequential backlog draining.

Live access fails closed unless both `SEC_REQUESTER_NAME` and a valid
`SEC_CONTACT_EMAIL` are present. All retries pass through the same rate limiter.
The bounded retry schedule is 5s, 15s, 60s, 5m, 15m. HTTP 429 and plausible automated
access HTTP 403 enter a 15-minute blocked state rather than hot-looping.

Official policy sources:

- https://www.sec.gov/about/developer-resources
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

## Durable evidence model

Runtime state is under `var/sec_form4/` and is intentionally ignored by Git:

- `raw/sha256/<prefix>/<hash>.bin`: immutable exact HTTP response body bytes.
- `attempts.jsonl`: append-only poll/request STARTED and COMPLETED envelopes.
- `manifest.jsonl`: derived raw-object index.
- `source_versions.jsonl`: observed byte versions per opaque filing source identity.
- `reconciliation.jsonl`: restart gaps, conflicts and integrity faults.
- `collector_state.json`: scheduling/backoff cursor.
- `pending/`: fsynced response transactions not yet fully published.

Every captured response records request-attempt time, local receipt time, HTTP/result
state, exact SHA-256, byte length, collector version, Git commit and endpoint class.
SEC publication time is not substituted for local receipt time.

A response transaction first fsyncs exact bytes plus its receipt envelope into a
committed pending stage. Publishing the content-addressed raw object and append-only
envelopes is replayable. A process death after stage commit is recovered on boot.
Existing content-addressed objects are verified, never replaced. The same source
identity observed with different bytes creates an explicit conflict/version record.

`manifest.jsonl` is only an index. It can be rebuilt from immutable raw bytes and
completed receipt envelopes. A checkpoint saying that evidence exists is never the
sole source of truth.

## Visibility firewall

Production status exposes only operational telemetry: RUN/IDLE/BLOCKED, timestamps,
HTTP/error state, opaque SHA-256, byte length, endpoint class, storage health,
scheduling/backoff and access-policy settings.

It does not expose raw Form-4 bodies, source/accession identities, issuer/owner fields,
transaction codes, filing counts or scientific aggregates. Capture is explicitly
tagged:

- `CAPTURED`
- `NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL`
- `NOT_ADMISSIBLE_FOR_CONFIRMATION`

Therefore `SCAN-INSIDER-FILINGS-001` remains scientifically blocked until a later,
separately reviewed parser/identity/PIT/admissibility path exists.

## Control Plane ownership

`QuantSystem` owns the collector lifecycle. On boot it reconciles staged responses
and raw-store integrity. On tick, a due SEC poll is handled before ordinary research
or desk work. The existing persistent serve loop therefore supplies the clock rather
than running a throwaway sidecar collector.

The smallest proof commands are:

```bash
python3 -m unittest tests.test_sec_form4_capture -v
python3 scripts/demo_sec_form4_capture.py
```

Live proof additionally requires explicit compliant identity and enablement:

```bash
QUANT_SEC_FORM4_CAPTURE=1 \
SEC_REQUESTER_NAME="..." \
SEC_CONTACT_EMAIL="..." \
python3 scripts/demo_sec_form4_capture.py --root . --live --proof-out /tmp/sec-live.json
```

The live proof JSON and generated status surfaces are intentionally opaque; raw response
content is never printed.
