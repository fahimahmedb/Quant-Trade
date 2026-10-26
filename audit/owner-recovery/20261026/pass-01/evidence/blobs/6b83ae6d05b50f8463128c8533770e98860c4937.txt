# WEATHER V3 — CAPTURE-ALL ARCHITECTURE (S2, DESIGN ONLY) — 2026-10-02

Status: DESIGN. Nothing here is deployed, scheduled or authorised.
Branch: `claude/weather-v3-s2-capture-architecture-2026-10-02`
Companion schema: `V3_CAPTURE_ALL_SCHEMA_2026-10-02.json`

```text
REAL_CAPITAL_AUTHORIZED = FALSE    LIVE_TRADING_AUTHORIZED = FALSE
t0 = NOT_DECLARED                  BUILDER_AUTHORIZED = FALSE
DATA_T0 = NOT_DECLARED             EXPERIMENT_T0 = NOT_DECLARED     CAPITAL_T0 = NOT_DECLARED
OUTCOME_INFORMATION_USED = FALSE   ORDERS_PLACED = 0                P0_HOST_TOUCHED = FALSE
```

Evidence labels: **SPEC** = stated in the V2 spec (`claude/charming-allen-948kd8`, read via `git show`); **DESIGN** = decision made here; **OPERATIONAL** = a tunable engineering parameter with no scientific meaning; **UNVERIFIED** = external API behaviour not checked by this session (no network capture was performed; the Builder must verify before relying on it).

---

## 0. Purpose and non-goals

Purpose: stop losing irreplaceable point-in-time (PIT) data. A Polymarket book, a forecast vintage, or a market's pre-resolution metadata that is not recorded when it exists cannot be reconstructed later. A passive collector costs no capital and places no orders.

Non-goals (hard):
- no orders, no wallet, no signing keys, no authenticated endpoints (public read-only only);
- no signal evaluation, P&L, fills, or bias computation inside the collector;
- no scientific threshold is decided here. Validity rules are copied from the V2 spec as *flags* computed on top of raw data; the raw record is always kept, valid or not;
- no edit of V2, Astra evidence, or the P0 SEC capture service / target host.

## 1. Three governance events (different events, different authorities)

None is declared by this document.

| Event | Meaning | Required before declaration | Declared by | Consequence |
|---|---|---|---|---|
| `DATA_T0` | First instant of passive, order-free capture under a frozen collector manifest | (a) owner decision on host (section 12); (b) collector manifest frozen (section 11) with hash; (c) Builder authorisation for *collector code only*; (d) a recorded DATA_T0 ledger entry (UTC, manifest hash, host id) | Owner / Blue (project governance). Not this session | Starts the clock on *data accumulation only*. Counts nothing toward any experiment. Capture may start/stop; gaps are flagged, never repaired |
| `EXPERIMENT_T0` | Start of a frozen experiment's counted window (V2: "t0 declared by Blue in governance", spec §11) | A frozen experiment spec + hashes, independent re-audit pass, Builder authorised for that experiment, readiness gates of that spec. DATA_T0 must already exist and the data must satisfy the experiment's own completeness rule | Blue in governance, per experiment | Opens a counted window under pre-registered rules. Post-t0 mutation policy (V2 §22) applies |
| `CAPITAL_T0` | Any real-capital exposure | Everything above plus separate explicit owner authority for real capital (currently FALSE) | Project owner only | Out of scope; this design has no code path that can reach it |

Rules:
1. `DATA_T0` does not imply `EXPERIMENT_T0`. Data captured between them is *eligible evidence* for a later experiment only if a frozen spec says so; it can inform bias-history readiness (V2 §11.1 BIAS_HISTORY_READY needs only archived PRIMARY vintages and observed FINAL states) but never counts as an experiment window date.
2. The collector writes `phase_label = DATA_CAPTURE` on every record. It never writes PRE_T0/FORWARD (those are experiment-layer labels, SPEC §25 PHASE_LOG) — an experiment's PHASE_LOG is a *derived* table built later from this archive.
3. A collector start/stop is an operational event, not a governance event. Only the DATA_T0 ledger entry is governance.

## 2. Architecture overview

```text
 schedule planner ──► slot ledger (planned, WAL) ──► fetcher ──► raw blob store (content-addressed, write-once)
        ▲                                               │                     │
   target registry                                      └─► capture envelope ─┴─► segment writer ─► sealed segments + manifest chain
 (stations, markets, tokens)                                                                          │
                                   clock monitor ──► clock records ──────────────────────────────────┤
                                   run lifecycle / gap records ───────────────────────────────────────┘
                                                                                                      ▼
                                                  derived layer (rebuildable, never authoritative): flags, tables, dedup views
```

Three layers:
1. **RAW (authoritative, immutable)** — exact response bytes + an envelope. Never rewritten.
2. **LEDGER (authoritative, append-only)** — planned slots, outcomes of each slot, collector runs, clock checks, gaps, config manifests.
3. **DERIVED (disposable)** — parsed tables, validity flags, quiet-book dedup views, coverage reports. Any derived table must be rebuildable byte-identically from RAW+LEDGER; if it cannot, it is a bug.

The collector process contains no research logic. Anything needing a threshold or judgement lives in the derived layer, outside the collector.

## 3. What is captured (streams)

All streams are public, unauthenticated, read-only. Endpoint names below follow the V2 spec (gamma listing; CLOB `GET /book`, `POST /books`; Open-Meteo Ensemble `ecmwf_ifs025`); exact URLs, parameters, rate limits and response shapes are **UNVERIFIED** and must be checked by the Builder against live documentation, with the verification result recorded in the collector manifest.

### 3.1 S-MKT — market metadata snapshots
- Source: Polymarket gamma listing of weather daily-temperature markets (SPEC §14.3: `closed=false` listing; NOAA-WRH template detection).
- Captured raw: full listing pages as returned (all pagination pages, each its own capture), including markets that are not in the V2 STATION_TABLE (the capture-all principle: record the universe, filter later).
- Content that must be recoverable from raw bytes: condition id, market/event slug, title, outcomes, CLOB token ids (YES/NO), `closed`, resolution/clarification state, resolution source/template text, `tick_size`/min order size if present, end/resolution dates.
- Cadence (OPERATIONAL): once per `META_PERIOD` (default 60 min) while any market is open; plus a snapshot at each daily universe compile; plus dense re-poll of a market from `FINAL_WATCH_START` until FINAL state is first observed (needed for `first_observed_final_at`, SPEC §25). `first_observed_final_at` = `captured_at` of the first capture showing the final state — a property of our own observation, never of the exchange's clock.
- **Outcome-bearing class**: resolution state and settlement values are outcome information. Stored in the same RAW format but under `class = OUTCOME_BEARING` (section 9.3).

### 3.2 S-BOOK — order books (best bid/ask and full depth)
- One capture = one token's book, from `GET /book` or one element of a `POST /books` response (SPEC §12.2 allows both). For a batch POST the *raw batch response body* is the blob; per-token envelopes reference the blob hash plus a JSON pointer/index to the element, so no byte is lost and per-token validity can be judged (SPEC §12.2: "validity is judged per token").
- **Depth**: store the entire response as received — every bid and ask level the API returns. There is no truncation, rounding or level cap in the collector ("desired depth" = all depth the endpoint offers). If the endpoint offers a depth parameter, the Builder records the parameter used in the envelope. Best bid/ask, spread, level counts and size sums are *derived* (section 8).
- Token universe: all CLOB tokens (YES and NO) of every open market in S-MKT, not only the 22-token V2 events (SPEC §12.4 "22 tokens" is an experiment-layer expectation).
- Cadence (OPERATIONAL, see section 7): a background grid for all tokens, plus window-aligned dense capture for V2-style entry windows when an event's `T_entry` is known.

### 3.3 S-FCST — forecast vintages and metadata
- Source: Open-Meteo Ensemble `ecmwf_ifs025`, 51 members, daily max/min, station time zone, `forecast_days=3` (SPEC §3) — the V2 PRIMARY model. Additional sources may be added only via a new manifest version (section 11); each is its own `source_id`.
- One capture = one request for one station (ICAO) with the exact query parameters stored. Raw response bytes stored verbatim.
- Envelope must record, beyond the common fields: `station_icao`, `latitude_requested`, `longitude_requested`, `elevation_requested` (from the frozen STATION_TABLE source), `model_id`, `timezone_requested`, `unit_requested`, `forecast_days`, and — parsed from the response *only as extra metadata, never replacing raw bytes* — `grid_latitude_returned`, `grid_longitude_returned`, `grid_elevation_returned`, `generation_time_ms` if the API reports it, and any model-run/init-time field the API exposes. **UNVERIFIED**: whether Open-Meteo exposes the underlying model-run issue time. If it does not, the archive records `forecast_issue_time = UNKNOWN_NOT_PROVIDED` and the only provenance of vintage time is `captured_at`. It must never be imputed in the collector.
- Cadence (OPERATIONAL): `FCST_PERIOD` (default 60 min) per station — hourly capture over-samples the model-run cadence (runs update far less often) but guarantees that a vintage selection rule of the form "greatest `captured_at` in a window before `T_entry`" (SPEC §3) always has candidates; identical-body captures are kept in RAW (they prove availability) and collapsed only in the derived view.
- Station set: the union of the frozen STATION_TABLE (SPEC §14.3, compiled once and hashed) and every ICAO discovered later (tagged `EXPLORATORY_NEW_STATION`, SPEC §14.3). Station coordinates/time zone come from one OurAirports `airports.csv` snapshot committed as bytes with its sha256 (SPEC §14.3); that snapshot is itself an S-REF capture.

### 3.4 S-REF — static reference snapshots
OurAirports `airports.csv` snapshot(s), the compiled STATION_TABLE (+hash), the collector manifest, and any other reference file the collector depends on. Written once through the same RAW path; re-snapshotted on schedule (default daily) so changes are observable rather than overwritten.

### 3.5 Explicitly *not* captured
Account/wallet data, order submission endpoints, trades/positions of any wallet, realised P&L, any computed signal. (Public trade tape is deferred: see section 14 open items.)

## 4. Common envelope (every capture)

Every capture, successful or failed, gets exactly one envelope record. Full field list is in the JSON schema; the normative semantics are:

| Field | Semantics |
|---|---|
| `capture_id` | deterministic, section 6.1 |
| `stream` | `S-MKT` \| `S-BOOK` \| `S-FCST` \| `S-REF` |
| `source_id`, `request_url`, `request_method`, `request_params` (canonical JSON), `request_body_sha256` (POST) | exactly what was sent |
| `slot_id`, `attempt_no` | link to ledger (section 6.2) |
| `request_sent_at` | host wall clock UTC, ns resolution, immediately before the request is written to the socket (SPEC §12.1) |
| `captured_at` | host wall clock UTC when the **complete response body** has been received (SPEC §12.1; = `information_available_at`) |
| `request_sent_mono_ns`, `captured_mono_ns` | `CLOCK_MONOTONIC` readings, for durations immune to wall-clock steps |
| `http_status`, `response_headers_sha256`, `response_headers_blob` | status and full headers (headers may include server `Date`; stored as received) |
| `body_sha256`, `body_bytes`, `body_blob_path` | content address of the raw bytes after transport decoding only (gzip/deflate removed; no JSON re-serialisation). Also store `content_encoding_received` |
| `transport_error` | null or a classified code (`TIMEOUT`, `DNS`, `TLS`, `CONN_RESET`, `OTHER`) with free text; a failed attempt has `http_status = null` and no blob |
| `clock_offset_ms`, `clock_check_at`, `clock_check_id` | most recent clock-monitor result (section 10); null if none exists |
| `collector_run_id`, `manifest_sha256`, `engine_version`, `host_id` | provenance (section 11) |
| `phase_label` | constant `DATA_CAPTURE` |
| `class` | `MARKET_STATE` \| `FORECAST` \| `REFERENCE` \| `OUTCOME_BEARING` |

S-BOOK extension (SPEC §25 ORDER_BOOK_SNAPSHOT additions are all carried): `token_id`, `method` (`GET_BOOK`|`POST_BOOKS`), `batch_index`, `exchange_book_timestamp` (raw field value, as received, plus parsed ms), `tick_size_recorded` (as reported in the response), `book_age_ms = captured_at − exchange_book_timestamp` (diagnostic only, never gating — SPEC §12.1), `valid_capture` (bool), `invalid_reason` (enum), `asset_id_returned`, `book_hash_returned` (if the API supplies one; stored as received, **not** verified by us — UNVERIFIED semantics).

**Timestamp semantics, restated**: the exchange `timestamp` is the book's *last change*, not an observation time (SPEC D3-BOOK / §12.1). Therefore a book with an old timestamp is a perfectly valid, quiet book. Observation time is `captured_at`. The collector never uses `exchange_book_timestamp` to decide whether to keep, retry or discard a capture, except for the single SPEC rule below (flag, not delete).

`valid_capture` computation (copies SPEC §12.3 verbatim; computed in the collector for convenience *and* recomputable in the derived layer; the stored raw record is never altered):
```text
valid_capture = http_status == 200
            and body parses as the expected JSON shape
            and asset_id_returned == token_id requested
            and exchange_book_timestamp <= captured_at + 2000 ms     (else invalid_reason = FUTURE_TIMESTAMP)
            and clock_offset_ms <= 250 and clock_check age <= 60 min (else invalid_reason = CLOCK_UNVERIFIED)
            and provenance complete (all envelope fields above non-null)
invalid_reason ∈ {NONE, HTTP_NOT_200, PARSE_ERROR, ASSET_ID_MISMATCH, FUTURE_TIMESTAMP, CLOCK_UNVERIFIED, PROVENANCE_INCOMPLETE, TRANSPORT_ERROR}   (first failing in this order)
```
The 2,000 ms / 250 ms / 60 min constants are copied from V2 SPEC §12.3 as *inherited* values. A different experiment may recompute validity with its own frozen constants from the same raw data; the collector's flag is a convenience, not an authority. The Builder must not tune them.

## 5. Raw immutable format

### 5.1 Layout (root `CAPTURE_ROOT`, one per DATA_T0 manifest lineage)

```text
CAPTURE_ROOT/
  blobs/ab/cd/<sha256>.zst            # content-addressed raw bodies; write-once
  segments/<stream>/<yyyy>/<mm>/<dd>/seg-<utc_start>-<seq>.jsonl.zst   # envelope records
  segments/<...>/seg-...<seq>.seal    # seal file once closed (section 5.3)
  ledger/slots-<yyyymmdd>.jsonl       # planned/closed slots (append-only)
  ledger/runs.jsonl                   # collector_run lifecycle
  ledger/clock.jsonl                  # clock-monitor records
  ledger/gaps.jsonl                   # gap records (section 10)
  ledger/manifests/<manifest_sha256>.json
  ledger/data_t0.jsonl                # governance ledger; collector can NOT write it (see 1)
  chain/chain.jsonl                   # hash chain of seals
  quarantine/                         # corrupt/unparseable files moved here, never deleted
```

### 5.2 Rules
1. **Blobs are write-once and content-addressed.** Compression is zstd (or gzip) of the exact bytes; the address is the sha256 of the *uncompressed* body, so compression settings never change identity. Writing an existing address is a verified no-op (re-hash the existing blob; mismatch → `ALERT_BLOB_COLLISION`, quarantine, stop that stream).
2. Blob write protocol: write to `tmp/<uuid>`, `fsync` file, `rename` (atomic) to final path, `fsync` directory (reuse the P0 `_fsync_dir` pattern, reference only), set read-only (0444).
3. **Envelope segments are JSON Lines**, one record per line, canonical JSON (sorted keys, UTF-8, no insignificant whitespace, integers for ns timestamps, ISO-8601 UTC with `Z` for display fields). Each line ends with its own `record_sha256` (hash of the canonical line without that field).
4. Segments roll over by size or time (`SEGMENT_MAX_BYTES`, `SEGMENT_MAX_SECONDS`, OPERATIONAL). A segment is *open* (appendable) until sealed; after sealing it is never modified.
5. Nothing is ever deleted or edited. Corrections are new records with `supersedes = <capture_id>` and a reason; they are never retroactive.
6. No parsed value ever replaces raw bytes. Parsed copies in the envelope are convenience and must equal a re-parse of the blob (verified by a periodic audit job, section 13).

### 5.3 Seal and chain
On closing a segment: write `seg.seal` = `{segment_path, record_count, first/last capture_id, first/last captured_at, segment_sha256, prev_seal_sha256, sealed_at, manifest_sha256}`. Append the seal hash to `chain/chain.jsonl`. `prev_seal_sha256` links seals into a hash chain, so deletion or reordering of any sealed segment is detectable. Periodically (default daily, OPERATIONAL) the chain head hash — **hashes only, no market data** — may be committed to Git as a tamper-evidence anchor; that is optional and requires no authority beyond ordinary commits to the data-ledger location chosen by the owner.

## 6. Restart-safe, idempotent writes

Requirement: crash + replay must not duplicate or lose records, and a replay must not fabricate a capture.

### 6.1 Deterministic identity
```text
capture_id = sha256( "v1" | collector_lineage_id | slot_id | token_or_target_key | attempt_no )
slot_id    = sha256( "v1" | stream | source_id | target_key | slot_time_utc_s )
```
`collector_lineage_id` identifies the DATA_T0 lineage (not the process), so a restarted process regenerates the same ids for the same planned work. `attempt_no` is persisted in the slot ledger, so a retry gets the next number and a replay after crash cannot reuse an attempt that actually reached the network.

### 6.2 Write-ahead sequence per attempt
1. `SLOT_PLANNED` appended to the slot ledger (planner is deterministic from schedule + manifest; re-planning an existing slot is a no-op by unique `slot_id`).
2. `ATTEMPT_STARTED{capture_id, request_sent_at}` appended + fsync **before** the request is sent.
3. Request; on completion write blob (idempotent by hash) → append envelope line (unique `capture_id`) → fsync → `ATTEMPT_COMPLETED{capture_id, outcome}`.
4. **Recovery on restart** scans the ledger: any `ATTEMPT_STARTED` without `ATTEMPT_COMPLETED` is closed as `ATTEMPT_ABORTED_BY_CRASH`, with no envelope fabricated (we do not know whether the server answered); the slot proceeds to its next `attempt_no` if still inside its retry allowance, otherwise it is closed `MISSED_CRASH`. An envelope with no matching `ATTEMPT_COMPLETED` (crash between 3b and 3c) is *adopted*: append the missing completion; never re-fetch to "fix" it.
5. **Uniqueness**: the segment writer keeps an in-memory + on-disk index of `capture_id`s of the open segment and the previous N sealed segments' last-id sets (or a sqlite index `capture_id PRIMARY KEY` rebuilt from segments on start). A duplicate `capture_id` is dropped and counted `DUPLICATE_SUPPRESSED`, never written twice.
6. A torn last line in an open segment (crash mid-write) is detected by its missing/invalid `record_sha256` or missing newline; it is truncated to the last good line **after being copied** to `quarantine/` (so the byte evidence persists), then the writer continues.

### 6.3 Why a replay cannot duplicate or alter data
Identity is a pure function of planned work; blobs are addressed by content; ledger writes are keyed; and nothing in the collector reads market content to decide what to write. Replaying the same ledger from any point converges to the same set of `capture_id`s.

### 6.4 Deduplication policy
- RAW: **no observation dedup.** Two captures with identical `body_sha256` at different `captured_at` are two observations (evidence that the state persisted). Only blob *storage* is deduplicated (one blob, many envelopes).
- DERIVED: a "state-change view" collapses consecutive identical `(token_id, body_sha256)` into intervals `[first_captured_at, last_captured_at]` with counts. Rebuildable; never replaces RAW.
- A short-circuit that skips the network call because "nothing changed" is forbidden (it would destroy availability evidence).

## 7. Schedule and rate policy (all OPERATIONAL, none scientific)

The collector's job is to observe often enough that later experiments *can choose* their own windows. Parameters live in the manifest; changing one is a new manifest version (section 11), recorded and effective from a stated instant, with the old schedule's gap/coverage semantics preserved.

| Parameter | Default (OPERATIONAL, owner may change) | Notes |
|---|---|---|
| `BOOK_GRID_PERIOD` | 15 min, all tokens of all open weather markets | Background grid; not a statistical requirement |
| `BOOK_ENTRY_WINDOW_MODE` | when `T_entry(e)` is supplied by a frozen experiment calendar: replicate SPEC §12.2 (first attempt at `T_entry − 240 s`, retry every 20 s inside `[T_entry − 300 s, T_entry]`; plus `[T_entry + 300 s, T_entry + 360 s]`) | Mirrors V2 verbatim; the *calendar of `T_entry` values* is an input, never computed by the collector |
| `META_PERIOD` | 60 min | + daily universe compile |
| `FINAL_WATCH` | poll each non-final market every 10 min from market end time until first FINAL observation, then every 60 min for 3 further observations, then stop | Supports `first_observed_final_at` and detects later clarification/dispute changes |
| `FCST_PERIOD` | 60 min per station | |
| `MAX_RPS_GLOBAL`, `MAX_CONCURRENCY`, `BACKOFF` | owner/Builder set from published rate limits (UNVERIFIED); exponential backoff with jitter on 429/5xx; `Retry-After` honoured | The collector must be a polite public-API client |
| `RETRY_ALLOWANCE` | per slot: 3 attempts, 20 s spacing, never extending beyond the slot's own closing instant | |

**Volume model** (ESTIMATE, formula only; no measured numbers): books/day ≈ `tokens_open × 86400 / BOOK_GRID_PERIOD`; with the V2 universe order of magnitude (48 stations × 2 kinds × 22 tokens ≈ 2,112 tokens) and a 15-minute grid that is ≈ 2.0×10⁵ books/day before entry-window densification. Book body sizes are unmeasured (UNVERIFIED). The Builder must measure bytes/book on a short *authorised* dry run and write the measured daily volume and compression ratio into the manifest; if projected storage is unaffordable, the owner is asked (section 12) — the Builder does not silently reduce depth or coverage.

## 8. Derived layer (all rebuildable; none authoritative)
- `book_levels`: one row per (capture_id, side, level_idx, price, size) parsed from the blob.
- `book_top`: best bid/ask price & size, spread, mid, level counts, total size per side — pure functions of `book_levels`; no thresholds.
- `book_state_intervals`: the dedup view of section 6.4.
- `validity`: recomputation of `valid_capture` under named, frozen rule sets (`RULESET_V2_SPEC_12_3` provided; others added only by frozen experiment specs).
- `coverage`: per (stream, target, day): planned slots, OK, FAILED, MISSED, DUPLICATE_SUPPRESSED, longest gap.
- `fcst_vintages`: parsed forecast vintages keyed (station, model, `captured_at`) with body hash; vintage *selection* (SPEC §3 greatest `captured_at` in `[T_entry − 3 h, T_entry)`) is an experiment-layer function applied to this table, not performed here.
- `station_table_compiled`: from S-REF + S-MKT.

Every derived table carries `derived_from_manifest_sha256`, `derivation_code_sha256` and a hash of its input segment set, so a result is traceable back to bytes.

## 9. Provenance, class firewall and PIT discipline

1. **Provenance** per record: source, URL+params, sent/captured times (wall + monotonic), HTTP status, body sha256, engine version, manifest hash, host id, run id, clock offset. This matches SPEC §12.3 "provenance complete".
2. **Point-in-time**: `captured_at` is the only time at which data is known to have been available to us. Later reprocessing may annotate but never rewrite it. Data with missing envelope fields are retained and flagged `PROVENANCE_INCOMPLETE`, not dropped.
3. **Outcome class firewall**: `OUTCOME_BEARING` records (resolution/settlement state) are written to separate segment directories (`segments/S-MKT-OUTCOME/...`). Derived-layer readers for experiments declare which classes they read; a pre-registered experiment's tooling reading `OUTCOME_BEARING` before its own analysis lock must be rejected by the consumer API. The collector never reads, parses for value, or joins outcome content (it needs only to store bytes, and to detect "state changed" for `FINAL_WATCH` via a *string/field equality on the market status field, not on any outcome value*). **UNVERIFIED**: whether the gamma status field cleanly separates "final" from outcome value; if not, the Builder stores the whole market object in the OUTCOME class.
4. **No survivorship**: markets are registered at first sight (S-MKT), including those later closed, and never removed from the target registry; the registry itself is derived from S-MKT.
5. **Never fabricate**: there is no interpolation, forward-fill, back-fill, or "typical value" anywhere. A missed slot is a `MISSED_*` ledger entry and a gap, nothing more.

## 10. Clock synchronisation, outages and gap flags

### 10.1 Clock monitor
- Dedicated task, period `CLOCK_CHECK_PERIOD` (default 10 min, OPERATIONAL — must be shorter than the SPEC §12.3 60-minute staleness limit with margin).
- Each check queries ≥ 3 independent time sources (NTP via chrony/ntpd status where available, plus ≥ 2 external NTP servers) and records offset estimate, round-trip, source ids, `chrony tracking` (if present) in `ledger/clock.jsonl` with its own `clock_check_id`. Public API `Date` response headers are *additionally* logged as a coarse cross-check (low resolution; not authoritative).
- `clock_offset_ms` in an envelope = the most recent check's absolute offset estimate; `clock_check_at` its time. Envelope validity per SPEC §12.3 (≤ 250 ms, check ≤ 60 min old) → else `CLOCK_UNVERIFIED` flag (record kept).
- Wall-clock step detection: if `CLOCK_REALTIME − CLOCK_MONOTONIC` drifts by > `STEP_ALERT_MS` (OPERATIONAL, default 100 ms) between consecutive checks, write a `CLOCK_STEP` clock record, and flag subsequent captures until a clean check.
- The collector never *sets* the system clock.

### 10.2 Run lifecycle (reference patterns from P0, not code reuse)
`ledger/runs.jsonl` records `RUN_START{run_id, manifest_sha256, host_id, boot_id, pid, engine_version, previous_run_id, previous_exit}`, `RUN_HEARTBEAT` (every `HEARTBEAT_PERIOD`, default 60 s), `RUN_STOP{reason}`. The restart classification borrows the P0 idea (fingerprint the effective environment; classify the restart as `CLEAN_RESTART`, `CRASH_RECOVERY`, `MANIFEST_CHANGED`, `HOST_CHANGED`, `MANUAL`) but the code is independent. An unrecognised environment/manifest change **blocks capture start** (fail closed) until a new manifest is recorded.

### 10.3 Gap records
A *gap* is any interval where an expected stream/target observation did not occur. Derived deterministically from the slot ledger plus run lifecycle, written to `ledger/gaps.jsonl` by a separate `gap_auditor` pass (idempotent by `gap_id = sha256(stream|target|interval)`).

| `gap_reason` | Meaning |
|---|---|
| `COLLECTOR_DOWN` | no heartbeat across the interval |
| `HOST_CLOCK_UNVERIFIED` | interval where captures exist but clock check stale/over limit |
| `SOURCE_HTTP_ERROR` | non-200 / transport failures exhausted the slot's retries |
| `RATE_LIMITED` | 429s exhausted retries |
| `MISSED_CRASH` | slot closed by crash recovery |
| `SCHEDULE_OVERRUN` | slot not started in time (backlog) |
| `UNIVERSE_UNKNOWN` | S-MKT capture itself failing, so target registry may be stale |
| `OPERATOR_PAUSE` | owner/Blue paused capture (an explicit ledger entry) |
| `MANIFEST_TRANSITION` | schedule changed by new manifest |

Gaps are *flags*. Downstream experiments decide whether a gap matters under their own frozen completeness denominator (cf. SPEC §12.4, which counts MISSING and never drops it). The collector never "fills" a gap.

## 11. Collector manifest (versioned, hashed)

One JSON document, canonical form, `manifest_sha256`. Contents: `lineage_id`, schema version, stream list, source endpoints + verified parameters (incl. the UNVERIFIED-item verification results), every OPERATIONAL parameter above, the inherited SPEC §12.3 constants (named, with spec section reference), STATION_TABLE reference hash, OurAirports snapshot hash, engine version / code hash, storage config (compression, segment limits), host identity. Every envelope names its `manifest_sha256`. A material change → new manifest, new hash, ledger `MANIFEST_TRANSITION`; never edited in place. Schedule/threshold-type fields are labelled `OPERATIONAL` or `INHERITED_FROM_SPEC`; there is no field of type "scientific threshold".

## 12. Owner-facing hosting options (NOT chosen here)

The owner must choose; this design runs on any of them because all state is files + a single process.

| Option | For | Against / risks |
|---|---|---|
| A. Claude Code cloud session container | Zero setup; already has repo access and proxy-governed egress | Container is ephemeral and reclaimed after inactivity; heartbeats/routines are best-effort; repo clone is not durable storage; disk allowance is fixed; network policy may need allow-listing of gamma/CLOB/Open-Meteo/NTP hosts; high risk of long gaps and of clock-check infeasibility (cannot guarantee NTP access); data must be exported to durable external storage. Likely acceptable only as a short **dry run for measurement**, not as the archive of record |
| B. Separate always-on host (VM/VPS or owner machine) with systemd-style supervisor and off-host replication | Continuous operation, controllable clock (chrony), durable disk, no dependency on a session lifecycle | Paid resource and credentials/ops burden → needs owner approval; must be a **different host** from the P0 target host to avoid cross-contamination |
| C. P0 target host (`quant-p0-targer`) | — | **Excluded by this design**: it is a P0 asset under its own authority; using it needs a separate explicit authorisation and a P0 impact review. Not recommended |
| D. Split: B for collection + A only for audits/derived-layer builds | Keeps heavy storage off the session container | Two surfaces to govern |

Common requirements regardless of choice: UTC system clock with NTP/chrony; ≥ 2 independent replicas of sealed segments (or one replica + hash anchoring); capacity for the measured volume; outbound HTTPS to the source hosts; no credentials of any kind; a `ledger/data_t0.jsonl` writable only by a governance step, not by the collector.

## 13. Builder acceptance tests (mechanical, no scientific judgement)

A future Builder implements and passes all of these before any DATA_T0 request:

1. **Crash/replay**: kill -9 at every write-protocol step (before ATTEMPT_STARTED, after it, after blob, after envelope, before completion, mid-line). After restart and replay: zero duplicate `capture_id`s, zero lost completed envelopes, torn line preserved in `quarantine/`, aborted attempts recorded, no fabricated envelope.
2. **Idempotent planner**: planning the same day twice yields identical `slot_id` sets and no duplicate ledger lines.
3. **Byte fidelity**: for each stream, a mocked HTTP server returns fixed bytes (with and without gzip, unicode, large numbers, duplicate keys, trailing whitespace); stored blob sha256 equals the sha256 of the transport-decoded bytes exactly.
4. **Timestamp semantics**: a book with `exchange_book_timestamp` = 6 h before `captured_at` is `valid_capture = true` (quiet book); one 2,001 ms after `captured_at` is `FUTURE_TIMESTAMP`; one exactly 2,000 ms after is valid (mirrors SPEC §12.3 verification list); `book_age_ms` is stored but never alters validity.
5. **Clock**: stale clock check (> 60 min) → `CLOCK_UNVERIFIED`, record retained; synthetic wall-clock step → `CLOCK_STEP` + flagged captures.
6. **Failure capture**: HTTP 429/500/timeout/DNS failure each yield an envelope with `http_status`/`transport_error` set, no blob, retries inside the allowance only, backoff observed, `Retry-After` honoured.
7. **Batch POST**: one `POST /books` response with N tokens → one blob, N envelopes referencing it, per-token validity independent (one `asset_id` mismatch invalidates only that token).
8. **No-dedup-of-observation**: 10 identical responses → 10 envelopes, 1 blob; the derived interval view shows one interval with count 10.
9. **Seal/chain**: flip one byte in a sealed segment / delete a segment / reorder seals → the verifier fails and names the segment.
10. **Derived rebuild**: delete derived layer, rebuild twice, outputs byte-identical.
11. **Gap auditor**: injected outage windows produce the expected `gap_reason`s, idempotently on re-run.
12. **Class firewall**: an experiment-mode reader refuses to open `OUTCOME_BEARING` segments before an externally supplied analysis-lock flag; the collector binary has no code path that reads outcome fields' values.
13. **Fail-closed start**: changed manifest hash / host id / missing clock source → collector refuses to start until a new manifest is ledgered.
14. **Governance guard**: the collector cannot write `data_t0.jsonl`, cannot import any trading/signing code, has no credentials in its environment, and issues only GET and `POST /books` to an allow-listed host set (static check + network-policy test).
15. **Measure-before-scale**: a time-boxed dry run on an authorised host records bytes/book, compression ratio, request latency distribution and rate-limit responses into the manifest (these are measurements to inform OPERATIONAL parameters; no scientific conclusion).

## 14. Open items and limitations (honest list)

- All API behaviours (endpoint URLs, pagination, rate limits, whether depth is parameterised, whether Open-Meteo exposes run/issue times, gamma status semantics, response `hash` fields) are **UNVERIFIED** here.
- Public trade tape / last-trade price / price-history endpoints are not in this V1 design: V2 uses book snapshots only; adding them is a manifest version change and an owner choice (data that exists only transiently should be considered if confirmed available).
- Historic data before DATA_T0 cannot be created by this design; recovery of earlier archives is S1's (data archaeology) task and must be merged by provenance label, never blended into this stream.
- A capture-all archive improves *information availability*, not edge. Existence of the archive supports no claim about Weather performance (North Star §7: alpha discipline).
- Owner/Blue decisions required (not decided here): host choice and storage budget (section 12); who declares `DATA_T0` and when; whether to include extra sources/streams; retention/replication target.

## 15. Authority statement

This document designs a passive, order-free, capital-free data path. It declares no t0 of any kind, authorises no Builder, places no orders, inspects no outcomes, and leaves V2, Astra evidence and P0 assets untouched. Implementing it requires the DATA_T0 prerequisites in section 1 to be satisfied by their own authorities.
