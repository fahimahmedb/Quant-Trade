# F1 Stage A capture without an agent session

The dedicated `F1 Stage A compressed capture` workflow runs on branch
`builder/f1-persistent-stage-a-2026-10-08`. It does not merge PR #22 or run an
economic calculation. It uses the frozen candidate bytes (SHA256
`f586b666d8950f9f98983a869eea012ef5e3ac7ac0c96f5d39a4dbbf0b65c9e4`) and
the registered 2020-01..2023-12 window. No Stage B archive is downloaded.

`capture_stage_a.py` uses the existing `acquire_f1.py` transport: sequential
requests, at most 5/s, verified public checksums, stop on repeated 403/429.
Before downloading it publishes `plan_STAGE_A.json`: every selected archive
key, the candidate identity, window and complete listing coverage. A failed
listing prevents publication and downloading. A restart reuses this plan
instead of querying a changed archive inventory.

The capture directory contains the compressed archives, manifest, immutable
plan, source/run provenance, acquisition log and `capture_STAGE_A.json`.
`COMPLETE` requires every planned archive's bytes and SHA256 to match its
manifest/public checksum. HTTP failures, removed or corrupted files cannot
silently shrink the analysis universe. No CSV row is read by acquisition or
verification.

Every workflow attempt uploads artifact
`f1-stage-a-capture-<run-id>-<attempt>` (30-day retention), including an
interrupted capture when possible. A subsequent attempt restores the most
recent artifact and downloads only missing or damaged planned archives. The
workflow serializes its own attempts and limits this worker to 5 requests/s.
Claude's private detached-process status is unknown here; this workflow cannot
measure or assert the aggregate rate of those private workers. Do not launch
another copy of this capture while its job is active.
The full capture needs hours, not a live LLM session. A failed attempt can be
retried from Actions; its capture is not an economic look.

## Local recovery and verification

Download/unpack the Actions artifact into a private directory. This unpacks
the artifact container; leave the individual monthly ZIPs compressed. With
the exact source commit checked out:

```sh
python3 -I research/crypto_carry_f1/capture_stage_a.py /private/f1-stage-a research/crypto_carry_f1/candidates_2026-10-08.txt f586b666d8950f9f98983a869eea012ef5e3ac7ac0c96f5d39a4dbbf0b65c9e4 --verify-only
```

Verification makes no network call. Omitting `--verify-only` resumes capture.
Only a truncated final manifest record can be repaired; malformed interior
records abort. An intact final record missing its newline is preserved.
The original Claude manifest/archives can also be imported: absent a plan,
the script builds one from names before fetching and verifies the existing
files before resuming. Unexpected manifest keys abort for investigation.

## Boundary before the economic run

`COMPLETE` proves acquisition coverage, not an edge. Before Stage A analysis,
establish whether the earlier Claude execution exposed an outcome. If it
did, preserve that result and its original harness. If unexposed, adopt/pin
the reviewed PR #23 repair and execute the registered Stage A run once.
For the Owner-directed takeover on 2026-10-09, the separate PR #25 runner
can resume from the last published unexposed canonical state while preserving
`prior_outcome_exposed: null` for the inaccessible private history. Its
evidence, Owner instruction and first documented discovery scope are recorded
in `verification/stage_a_exposure.json` and copied into result metadata. This
does not establish the missing history or authorize a confirmatory claim. A
subsequently recovered earlier outcome must be preserved and reconciled;
decision-changing post-outcome repairs invalidate the registered lineage.
Publish the result, source SHA256 and result SHA256 before the Stage B review
and run. This workflow intentionally contains no `run_f1.py` invocation.

Source: Binance Vision / Binance Public Data, CC BY-NC-SA 4.0;
non-commercial research capture. See the preregistration and terms notes.
