# Registered Stage B capture (sealed)

Preregistration R14 allows downloading and checksum-verifying the compressed
Stage B archives before the Stage A result. The dedicated workflow runs on
`builder/f1-sealed-stage-b-capture-2026-10-09`, with a separate directory and
artifact prefix `f1-stage-b-sealed-capture-<run-id>-<attempt>`.

It freezes the 2023-11..2026-09 key inventory against the original candidate
SHA256 before any download. November/December 2023 are marked warm-up only;
2026-10 is excluded. A complete certificate requires every planned archive.
Only a names-only listing and compressed-byte checksums are read. The job
uses the existing sequential transport at <=5 requests/s, and retains partial
captures for recovery. No monthly ZIP is decompressed and no statistic is
computed. Do not launch another copy while it is active.

The capture CLI keeps Stage A as its default for compatibility. Stage B is
explicit:

```sh
python3 -I research/crypto_carry_f1/capture_stage_a.py /private/f1-stage-b-sealed research/crypto_carry_f1/candidates_2026-10-08.txt f586b666d8950f9f98983a869eea012ef5e3ac7ac0c96f5d39a4dbbf0b65c9e4 --stage STAGE_B
```

Add `--verify-only` for an offline checksum/coverage check. A Stage A verifier
cannot use or relabel a Stage B plan. The script now encodes Unicode object
keys in HTTP URLs and reads the matching UTF-8 checksum filenames, preserving
the exact frozen symbol strings and bytes. These are transport fixes, not
changes to the hypothesis, fees, cells, selection rule or economic harness.

The analysis harness remains SHA256
`5a773f45c630c559532ccfbf6888bf506adf6e8a3c31b9fbe09f65ef33ec239c`.
Stage B analysis still requires the published Stage A result, authenticated
result SHA256, matching harness identity and the registered single test. A
compressed capture is not an economic look. Derived work credits Binance
Vision / Binance Public Data under CC BY-NC-SA 4.0; raw files stay outside git.

## Autonomous documented evaluation

`F1 Stage B single documented evaluation` waits for existing capture run
37901109334; it starts no additional Binance acquisition. Before reading a
monthly ZIP it authenticates the published A result SHA256
`554988d5c136caf43387d5338e0db226516e4a8b9e9a7ddf42c290aac6dbab03`,
theta 0.20, the unchanged harness and the published A review report. It checks
the completed artifact's GitHub digest, producer source hashes, frozen B plan,
every archive/checksum, manifest and warm-up flags. An incomplete or failed
capture aborts before reserving a look.

Only then it atomically claims `f1/crypto-carry-001-stage-b-look` and executes
the fixed CLI once. An existing claim blocks automatic reruns. Verification,
any result, attribution and a report survive on a separate evidence branch
and as an artifact, including after interrupted publication. No raw dataset
is put into git. The exact execution decision is in
`verification/stage_b_execution.json`.

### Recovery after the capture timeout (2026-10-09)

Capture 37901109334 attempt 1 reached the 300-minute acquisition-step limit.
Its last progress record was 33,100/35,789 archives; the successfully persisted
partial artifact is 11616937050 (73,560,519 bytes), SHA256
`71c1d8a7dde06ed47367952b29598c89ef3e39225c1634588c4865d050810ae5`.
This progress count is not a complete certificate. Controller 37918595118
aborted while waiting; verification, look reservation and economic execution
were all skipped. The B look reference was absent before recovery.

Only the failed capture job is rerun, as attempt 2 of the same run and producer
commit. It restores the existing compressed artifact, checksum-verifies saved
files and fetches missing keys. The controller now requires attempt 2 at the
original producer and authenticates the original plan SHA256
`4a6671472feb27817d816252a5d5b8302cac4a26ce6c997632ffc5df0e586f6a`,
observed in attempt 1's acquisition log. The old artifact is never accepted as
complete. This is an R7 infrastructure recovery before any B statistic;
economic selection, harness, costs and reporting policy remain unchanged.

The outcome also overwrites the existing research checkpoint with its final
status and next decision. After persistence, the nine-field result delta is
published to PR #22 with a run/attempt marker to avoid duplicate publication.
Existing negative Polymarket scouting and blocked F2 access are retained in
the checkpoint rather than automatically retested.

The Owner-directed takeover preserves UNKNOWN private predecessor history.
The result metadata and report authorize no confirmatory claim. The reporting
policy, published before B is read, rejects an excluded Sharpe-1.5 expression,
degenerate exposure, or a statistically confirmed expression below the assumed
cash hurdle. A positive screen above cash remains `INVALID_EXPERIMENT` for
registered confirmation until legacy lineage is resolved; other failures to
confirm are `INCONCLUSIVE_UNDERPOWERED`. No alternative cell replaces theta
0.20, and no threshold or cost assumption changes after observation.
