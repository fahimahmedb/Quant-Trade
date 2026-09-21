# BUILDER — GATE-B ROUTE-1 CONCRETE MUTATION PACK — 2026-09-21

## 0. Mission identity

Branch: `builder/gate-b-route1-concrete-mutation-pack-2026-09-21`
Verified starting HEAD (as dispatched to this session): `6e4f37d77d8ddb7cab4e53133e6c8570d3e9fc25`

This handoff supersedes the mission-dispatch commit alone; it is not satisfied by
mission-dispatch CI (35641260071) being green. The concrete artifacts and this handoff are
the actual deliverable.

## 1. Reserved run — unchanged, not re-reserved

```text
GATE_B_RUN_ID = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
GATE_B_ATTEMPT_NUMBER = 1
RUN_RESERVATION_DIGEST = sha256:97dac3e09e453dae189111c6f6d014aa2b426dea532bae6ae51de016c37ed8bc
REVOCATION_EPOCH = 1
REVOCATION_REFERENCE = gate-b-host-relay-preseal-2026-09-21-initial-epoch
```

No `Registry.reserve()`, `seal_activation()`, or `consume_activation()` call was made from
this session. No target host was touched.

## 2. Changed files

```text
A governance/gate_b_route1/quant-gate-b-egress.nft
A governance/gate_b_route1/quant-gate-b-egress-guard.service
A governance/gate_b_route1/var-lib-quant-p0.synthetic.mount.unit
A governance/gate_b_route1/GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json
A handoff/BUILDER_GATE_B_ROUTE1_CONCRETE_MUTATION_PACK_2026-09-21.md
```

No other file was modified. `git status --short` before this handoff commit showed only the
new `governance/gate_b_route1/` directory as untracked — no frozen V4 (`src/`), no
`quant-sec-capture.service`, no other production/config file touched.

## 3. Exact SHA-256 for every pack artifact

```text
quant-gate-b-egress.nft
  sha256:4cf0c4823f8a2c10c90102470ec73ca4f676a5ff30f62c458b0e5f7ea5f578d5

quant-gate-b-egress-guard.service
  sha256:c756fbc574fb4bdd5acbb5869ed733bc6dbfb6307c5e6da13c56831fe8363de3

var-lib-quant-p0.synthetic.mount.unit
  sha256:ef9e43e7674270ed3977a8e89c54c0e07c8ac6ec1e32566c3441d04438fd507e

GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json (full file, includes embedded manifest_digest field)
  sha256:472bb20eb85d21ffc6c4060e4939ce728a5767671455b3b3b803847f70bd4273
```

Canonical manifest self-digest (over the object with `manifest_digest` field removed,
`json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True)`):

```text
manifest_digest = sha256:e80e020fe2469bad6eb4bc79d4392e9123a8f136bdbe652a826a593849492f3e
```

These three artifact digests are embedded verbatim inside `pack_artifacts.*.sha256` in the
manifest and were verified to match by direct re-computation (section 5).

## 4. Pack contents summary

### A. `quant-gate-b-egress.nft`

Creates a dedicated `table inet quant_gate_b` with a single `chain output` (`type filter
hook output priority filter; policy accept;`) containing exactly one rule: `tcp dport 443
drop`. `inet` family covers both IPv4 and IPv6 with one rule set. No other table, chain, or
base policy is touched. No SEC allow exception, no second chain, no jump target that could
bypass the drop.

### B. `quant-gate-b-egress-guard.service`

One-shot unit (`Type=oneshot`, `RemainAfterExit=yes`). `ExecStart` loads only
`/etc/quant/gate-b/quant-gate-b-egress.nft` via `nft -f`; the unit becomes active only if
that load succeeds. `Before=var-lib-quant\x2dp0.mount quant-sec-capture.service` orders it
ahead of both the synthetic mount and the collector. `ExecStop` (`nft delete table inet
quant_gate_b`) is the rollback-only removal path, to be invoked exclusively by the Operator
rollback sequence after the collector is already stopped. Does not reference or modify
`quant-sec-capture.service`.

### C. `var-lib-quant-p0.synthetic.mount.unit`

Represents the exact future bytes for the run-scoped replacement of
`/etc/systemd/system/var-lib-quant\x2dp0.mount`. `Where=/var/lib/quant-p0` is unchanged;
`What=` is bound exactly to the fixed run-scoped synthetic reservoir path. `Requires=`/
`After=` include `quant-gate-b-egress-guard.service` and the conventional escaped unit for
the `/mnt/quant-data` backing (`mnt-quant\x2ddata.mount` — flagged TARGET_HOST_ONLY below,
since the exact live unit name is not repository-verifiable). `Before=quant-sec-capture.service`.
Original-unit expected digest (`fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875`)
is bound in the manifest for pre-mutation verification and post-rollback restoration proof.
No change to `opt-quant-var.mount` semantics.

### D. `GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json`

Canonical JSON binding: schema/version (`quant-gate-b-route1-mutation-pack/v1`); exact run
ID/attempt/reservation digest/revocation epoch; frozen candidate triple; target-host opaque
identity + boot binding; exact run-scoped paths (synthetic reservoir, evidence root, three
install paths); SHA-256 of A/B/C; expected original mount-unit digest; the five allowed
mutation phases (`PRE_MUTATION_VERIFICATION`, `EVIDENCE_BACKUP`, `INSTALL_NETWORK_GUARD`,
`SYNTHETIC_RESERVOIR_SWITCH`, `ROLLBACK_SANITIZATION`) each with an exact ordered
command/check list and explicit `on_mismatch: STOP` semantics; a `verification` object
split into `repository_side` (this mission) and `target_host_only` (deferred to Operator);
the full capability matrix with `ALLOW_REAL_SEC_NETWORK: false`; and an explicit
`activation_statement` that no activation is sealed or consumed by this artifact.

## 5. Exact test commands / results

```text
$ nft -c -f governance/gate_b_route1/quant-gate-b-egress.nft
(exit 0 — syntax valid)

$ systemd-analyze verify --recursive-errors=no governance/gate_b_route1/quant-gate-b-egress-guard.service
(exit 0 — no errors)

$ cp governance/gate_b_route1/var-lib-quant-p0.synthetic.mount.unit '/tmp/var-lib-quant\x2dp0.mount'
$ systemd-analyze verify --recursive-errors=no '/tmp/var-lib-quant\x2dp0.mount'
(exit 0 — no errors; verified under the exact escaped unit name it will be installed as)

$ python3 - <<'PY'
# loaded GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json, re-serialized with
# json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=True)
# and asserted byte-identical to the file on disk (CANONICAL_JSON_OK)
# recomputed manifest_digest over the object with that field removed and
# asserted equal to the embedded value (MANIFEST_SELF_DIGEST_OK)
# recomputed sha256 of each of A/B/C on disk and asserted equal to
# pack_artifacts.*.sha256 in the manifest (ARTIFACT_DIGESTS_MATCH_MANIFEST)
PY
CANONICAL_JSON_OK=true
MANIFEST_SELF_DIGEST_OK=true
ARTIFACT_DIGESTS_MATCH_MANIFEST=true
run_id == gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
candidate_sha == 4d06bdbf8ed008af5c9d4ab9469e61f34c3ba072
ALLOW_REAL_SEC_NETWORK == False

$ grep -q "table inet quant_gate_b" quant-gate-b-egress.nft && echo table:OK
$ grep -q "hook output" quant-gate-b-egress.nft && echo hook_output:OK
$ grep -qE "tcp dport 443 drop" quant-gate-b-egress.nft && echo tcp_443_drop:OK
table:OK
hook_output:OK
tcp_443_drop:OK
(the only occurrences of the substring "sec" in the .nft file are inside two
explanatory comments stating the absence of a SEC allow exception; no actual
allow/accept rule referencing port 443 or SEC exists in the ruleset)

$ grep -q "/etc/quant/gate-b/quant-gate-b-egress.nft" quant-gate-b-egress-guard.service && echo guard_nft_path:OK
guard_nft_path:OK

$ grep -q "What=/mnt/quant-data/gate-b-synthetic/gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811/state" var-lib-quant-p0.synthetic.mount.unit && echo mount_what:OK
$ grep -q "Where=/var/lib/quant-p0" var-lib-quant-p0.synthetic.mount.unit && echo mount_where:OK
$ grep -q "Requires=quant-gate-b-egress-guard.service" var-lib-quant-p0.synthetic.mount.unit && echo mount_requires_guard:OK
mount_what:OK
mount_where:OK
mount_requires_guard:OK

$ git status --short
(only governance/gate_b_route1/* and this handoff are new/changed — no src/, no
quant-sec-capture.service, no other production/config file touched)
```

## 6. Remaining TARGET_HOST_ONLY checks (explicitly deferred, per mission section 8)

- actual nft kernel-level packet-drop behavior for outbound TCP/443 (not provable from
  repository CI — this pack proves the ruleset compiles and contains exactly the intended
  rule; the Operator relay must prove the live kernel enforces it);
- live `FragmentPath` and byte-exact match of the currently loaded
  `var-lib-quant\x2dp0.mount` unit against `fb37ed643fcb237fcb0c3ec54ee9ceada1e376ee88cc16f39cff47ef68a19875`
  immediately before mutation;
- live resolution of the exact escaped systemd unit backing `/mnt/quant-data` — this pack
  assumes the conventional name `mnt-quant\x2ddata.mount` in `Requires=`/`After=`; the
  Operator relay MUST re-resolve this live (e.g. `findmnt -no UNIT /mnt/quant-data` or
  equivalent) and fail closed if it differs from what is installed;
- live boot ID / NTP synchronization / service-stopped freshness at the exact moment of
  activation consumption;
- actual post-switch mount topology (`findmnt`) proving `/var/lib/quant-p0` resolves to the
  synthetic reservoir and `/opt/quant/var` resolves through it, and that the preserved
  qualifying backing remains distinct;
- absence of `table inet quant_gate_b` after rollback (host-side `nft list tables`
  observation).

## 7. Explicit statement: no activation sealed or consumed

This mission did not call `Registry.reserve()`, `Registry.seal_activation()`, or
`Registry.consume_activation()`. The reserved run `gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811`
(attempt 1) remains exactly as it was: reserved, unsealed, unconsumed. No target host was
touched, connected to, or mutated by this session. No frozen V4 production byte, no
`quant-sec-capture.service` byte, and no Product/application code was created or modified.

## 8. Final disposition

`GATE_B_ROUTE1_CONCRETE_MUTATION_PACK = READY_FOR_BLUE_SEAL_INTEGRATION`

Blue may now bind these three artifact digests and this manifest's
`manifest_digest` (`sha256:e80e020fe2469bad6eb4bc79d4392e9123a8f136bdbe652a826a593849492f3e`)
into the broader activation envelope for the already-reserved run, in place of the
feasibility-reference placeholders that `handoff/BLUE_GATE_B_ACTIVATION_SEAL_CORRECTION_2026-09-21.md`
identified as insufficient. Only after that binding, and only after live target-host
freshness re-verification at consumption time, may the Operator execute the mutation
sequence in `GATE_B_ROUTE1_MUTATION_PACK_2026-09-21.json`.

Safety state unchanged:

```text
GATE_B_RUN_RESERVED = TRUE
GATE_B_RUN_ID = gate-b-31f4fa2e-e697-4c3a-b00e-98626f867811
ACTIVATION_SEALED = FALSE
ACTIVATION_CONSUMED = FALSE
GATE_B_MUTATION_AUTHORIZED = FALSE
GATE_B = NOT_STARTED
t0 = NOT_DECLARED
REAL_CAPITAL_AUTHORIZED = FALSE
```

Returning control to Blue.
