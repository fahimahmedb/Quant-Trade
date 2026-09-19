# CLAUDE FORWARD DATA — live checkpoint

**Branch:** `parallel/claude-forward-data-2026-09-20`
**Base:** `b17b381a8fa1f6a24e6cd6f92a090b40627bfe78` (Wave 1 CLAUDE handoff tip)
**Role:** Data Plane Builder, forward-data operability track. P0 SEC/Form-4 remains
exclusively `astra/p0-deep-adversarial-pre-t0`'s. This track does not read the P0
reservoir, does not modify `src/quant/dataplane/sec/**`, `deploy/quant_sec_supervisor.py`,
`deploy/quant-sec-capture.service`, `src/quant/clock.py` or `scripts/quant.py`.

This file is updated after each significant slice of work, before every checkpoint
commit. It is the running log; `handoff/CLAUDE_FORWARD_DATA_2026-09-20.md` is the
final deliverable written once the mission is complete.

---

## Mission (compressed)

Wave 1 built `src/quant/dataplane/forward_recorder.py` and left it recording zero
observations — the single highest-value-per-day item in the Wave 1 opportunity-cost
review. This mission's job is to make the forward lane *realistically operable*
without creating a second Control Plane / scheduler and without touching P0.

Concretely: audit the recorder adversarially, make time provenance honest and
explicit (no fake "trusted external timestamp"), inventory real non-P0 sources
already authorized in this repository, define an adapter contract, build a forward
coverage ledger with EXPECTED/ATTEMPTED/OBSERVED/VALID/CONFLICT/MISSING/UNKNOWN,
define a clean `ForwardCaptureTask`/`ForwardCaptureRequest` interface a future Clock
can call (or a manual runner using the identical contract today), and answer with
repository proof whether capture can actually start now.

## Starting state (read before any code)

Read in full: `QUANT_NORTH_STAR.md`, `STATE.md`, `SYSTEM_ARCHITECTURE.md`,
`NEXT_BUILD_MISSION.md`, `handoff/PARALLEL_WAVE1_CLAUDE_2026-09-19.md`, `SOURCE_BASIS.md`,
`research/opportunity_map.json`. Inspected: `src/quant/dataplane/**` (non-sec),
`src/quant/clock.py` (read-only — Control Plane contract, not modified),
`src/quant/dataplane/sec/timebase.py` (read-only, small interface file, to mirror the
injectable-clock convention already established for the SEC lane; no reservoir
content read), `src/quant/state.py`, `src/quant/paths.py`, `src/quant/events.py`,
`src/autonomous_research/runtime.py`.

Baseline before any change: `588 tests passed` (`PYTHONPATH=src python3 -m unittest
discover -s tests`).

Key facts established before writing code:

* `ForwardObservation`/`ForwardRecorder` are used only inside `forward_recorder.py`
  itself and `tests/test_dataplane_forward_lane.py` — no other module imports them,
  so they can be extended (additive, default-valued fields) without a large blast
  radius.
* The only two datasets ever registered are `us_sector_etf_daily` (Yahoo Finance
  public chart endpoint, credential-free, already fetched over the network by this
  repository's own `ingest.py`) and `nasdaq_composite_daily` (a static local export
  with no live update path — not forward-capturable).
* Live network egress to `https://query1.finance.yahoo.com` **is reachable from this
  execution environment** (`curl` returned HTTP 200 with real quote data during
  reconnaissance) — this is direct repository-adjacent proof that the already-used,
  already-authorized source is live-operable right now, without new credentials.
* `research/opportunity_map.json` names the *other* candidate lanes' exact blockers:
  `factor_residual` needs a survivorship-controlled security/factor panel (new
  provider), `volatility_surface` needs option chains/quotes/rates/corporate actions
  (new provider), `insider_filings` is the P0 SEC/Form-4 lane (out of scope here).
  None of these are invented as "available" — they stay named-blocked.
* A real defect found by falsification before writing any fix: `ForwardRecorder`'s
  read path (`accepted()`, and the count in `__init__`) does not enforce
  first-accepted-wins per key across *two independent recorder instances* racing on
  the same file — only the in-memory guard of a single already-running instance
  does. Two processes that both see an empty/older file and both accept the same new
  key with different values can both get journaled as `ACCEPTED`, and the naive
  reader returns both. This is being fixed and covered by an adversarial test (see
  progress log).

## Non-negotiable boundaries (restated for this file's own audit trail)

```
P0_RESERVOIR_ACCESSED   = FALSE  (kept true throughout; no var/sec/**, no handoff/SEC_FORM4_*.json read)
CLOCK_PY_MODIFIED       = FALSE
SEC_DIR_MODIFIED        = FALSE
SCRIPTS_QUANT_PY_MODIFIED = FALSE
SECOND_SCHEDULER_CREATED = FALSE
SCIENTIFIC_SELECTION_MADE = FALSE  (no D07/D05/D08/D19/MEUE/strategy choice)
NEW_BRANCH_CREATED      = FALSE (working on parallel/claude-forward-data-2026-09-20 as instructed)
```

## Progress log

- [in progress] Checkpoint file created. Baseline established. Beginning
  `ForwardObservation` time-authority hardening next.

(Further entries appended after each significant, committed slice.)
