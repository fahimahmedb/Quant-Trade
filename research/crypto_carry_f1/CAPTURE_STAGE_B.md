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
