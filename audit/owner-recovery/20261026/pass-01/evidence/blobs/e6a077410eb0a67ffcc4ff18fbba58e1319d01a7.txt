# BLUE TARGET-HOST REAL DEFECT — EFFECTIVE UNIT DIGEST INSTABILITY — 2026-09-20

Authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.
Frozen candidate under test: `blue/p0-gate-a-v3-frozen-2026-09-20@2da079d8ad75c69eb3fc2990c512735cb4bdc02b`.

Status:
`TARGET_HOST_ENTRANCE = FAIL / NO_T0`

## 1. Executive disposition

A real target-host execution against the exact frozen Gate A v3 candidate exposed a deterministic repository defect in the effective systemd unit fingerprint path.

The historical Gate A v3 repository-only disposition remains recorded as PASS for the evidence domain it actually covered. It is not silently rewritten.

However:

`GATE_A_V3_TARGET_HOST_ELIGIBILITY = REJECTED_BY_NEW_REAL_DEFECT`

`CORRECTIVE_GATE_A_V4_REQUIRED = TRUE`

`t0 = NOT_DECLARED`

`P0_CONTINUOUS_SERVICE_STATE = OPEN / NOT_YET_PROVEN_CONTINUOUS`

`REAL_CAPITAL_AUTHORIZED = FALSE`

`PRODUCT_INTEGRATION = PAUSED`

No further start/restart/rematerialization/reauthorization of the frozen v3 candidate is authorized for qualification.

## 2. Target-host evidence binding

Restricted target-host evidence root used by the operator:

`/var/lib/quant-p0-qualification/entrance-20260920T184233Z/`

Hash-addressable defect artifact:

`TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_INSTABILITY_20260920T195825Z.json`

Artifact SHA-256:

`sha256:cb402bb3151a59708c6e3b6406323fe8671680b0e2785c9bb92ff47064639442`

Observed frozen materialized effective unit digest:

`sha256:33d166b68a337947f7737ae659b386df88545867012ce88d0b30bcdbcf070b3d`

Observed effective unit digest after systemd execution metadata changed:

`sha256:c6394ef740c3f66c35e2920ebd4f21d27ff1417d11be5ab93b457f0f7e355c22`

Artifact verdict:

`DIGEST_STABLE = False`

`CLASSIFICATION = REAL_DEFECT`

`TARGET_HOST_ENTRANCE = FAIL_NO_T0`

The restricted artifact itself is not committed to the repository. Only its binding metadata and verdict are recorded here.

## 3. FACT

The loaded fragment at target-host diagnosis was:

`/etc/systemd/system/quant-sec-capture.service`

Its bytes matched the frozen repository unit exactly.

There were no loaded drop-ins.

The following effective frozen semantics matched expectation:

- `Restart=on-failure`
- `RestartUSec=15s`
- `StartLimitIntervalUSec=10min`
- `StartLimitBurst=5`
- `KillMode=control-group`
- `KillSignal=15`
- `TimeoutStopUSec=30s`
- `WorkingDirectory=/opt/quant`
- qualifying supervisor `ExecStart`
- expected `EnvironmentFiles=/etc/quant/sec-capture.env`

The frozen validator `_effective_systemd_definition()` passed against the post-attempt loaded unit and emitted the new digest `sha256:c6394e...`.

The previously materialized manifest remained bound to `sha256:33d166...`.

The one-use deployment authority remained present and unconsumed.

No deployment-authority ledger row existed.

No `supervisor_state.json`, `supervisor_events.jsonl`, `lifecycle.jsonl` or integrity latch existed after the failed qualification attempt.

Therefore no `CHILD_LAUNCH_AUTHORIZED` event occurred for the failed entrance.

## 4. REAL DEFECT

Frozen implementation:

`deploy/quant_sec_supervisor.py::_effective_systemd_definition`

The function requests `ExecStart` through `systemctl show`, stores the complete returned property string in the canonical `parsed` map, serializes that map, and hashes it into `QUANT_SEC_EFFECTIVE_UNIT_DIGEST`.

On the real target systemd, the returned `ExecStart` property contains both the static command definition and transient execution metadata, including observed fields such as:

- `start_time`
- `stop_time`
- `pid`
- `code`
- `status`

Those fields change when the service executes even though the unit file and acquisition semantics are unchanged.

The effective unit digest can therefore change as a side effect of attempting to run the service.

That digest participates in the acquisition-critical fingerprint.

A pre-start materialization can consequently become stale solely because the service was invoked, which can make a valid pre-created deployment authority fail fingerprint validation.

This violates the required invariant that unchanged acquisition semantics preserve the acquisition-critical fingerprint.

Classification:

`REAL_DEFECT`

This is not classified `TARGET_HOST_ONLY`: the real host supplied a normal systemd serialization that exposed deterministic repository behavior.

## 5. Earlier failed-start evidence

An earlier target-host attempt before final materialization produced `FINGERPRINT_NOT_MATERIALIZED` and systemd restart bursts.

After explicit materialization and one-use authority creation, a later systemd start produced repeated `[supervisor] BLOCKED RuntimeError` outcomes.

The later forensic discriminant showed that the authority remained fresh/present and had never been consumed, while the loaded-unit semantic validator itself passed.

The changing effective digest explains this state without requiring a unit-byte drift, drop-in, second writer, or consumed/replayed deployment authority.

## 6. Blue decision

Blue stops qualification of `2da079d8ad75c69eb3fc2990c512735cb4bdc02b`.

Do not:

- restart or start the qualifying service for this candidate;
- reset failed state merely to obtain a clean-looking run;
- recreate deployment authority;
- rematerialize the candidate and treat that as a correction;
- delete the failed-start evidence;
- transfer any target-host success claim to a later SHA;
- resume Product integration.

Preserve:

- the frozen v3 candidate;
- its historical Builder and Astra evidence;
- the target-host entrance evidence;
- the failed systemd journal sequence;
- the restricted hash-addressable defect artifact.

## 7. Builder corrective specification

Builder must implement a minimal correction from the exact frozen implementation baseline unless Blue explicitly approves a broader base.

The effective systemd digest must bind configuration semantics, not mutable execution observations.

At minimum:

1. Parse/canonicalize `ExecStart` into stable configuration-only semantics.
2. Bind the executable path and argument vector used for the qualifying supervisor.
3. Preserve rejection of semantic `ExecStart` drift.
4. Exclude transient execution observations such as timestamps, PID, exit code and status from the canonical digest.
5. Preserve fragment byte equality enforcement.
6. Preserve no-drop-in enforcement.
7. Preserve checks for WorkingDirectory, restart policy, timing, kill policy, timeout and environment file.
8. Preserve fail-closed behavior on unavailable/unparseable effective definitions.
9. Do not weaken acquisition-critical fingerprint coverage to make the test pass.

Required discriminating tests:

- same semantic unit + different `ExecStart` runtime timestamps/PIDs/statuses => identical effective unit digest;
- same semantic unit before and after a service invocation => identical effective unit digest;
- changed executable or argv => rejected and/or different bound digest as specified;
- changed qualifying flag => rejected;
- changed restart/timing/kill/workdir/environment-file semantics => rejected;
- drop-in appears => rejected;
- loaded fragment differs from repository => rejected;
- materialize -> authorize -> service invocation does not invalidate the materialized acquisition fingerprint merely because systemd execution metadata changed.

Builder must include the exact regression fixture reproducing the target-host form of `ExecStart`.

## 8. Required delivery sequence

General governance flow remains:

`finding → Blue decision → specification → Builder → independent review → Blue decision`

Proposed Builder mission name:

`builder/p0-effective-unit-digest-stability-v4-2026-09-20`

Expected implementation baseline:

`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Builder must stop after durable handoff and exact-head CI evidence.

Blue must independently inspect the delta and freeze a new candidate only after the correction is scoped and proved.

Astra/Red Team must independently reproduce the original defect and show that the new candidate discriminates:

- transient systemd execution metadata: NON-SEMANTIC / STABLE;
- actual unit semantic drift: BLOCKED OR FINGERPRINT-CHANGING.

Only after independent review and a new Blue disposition may target-host qualification restart with a fresh release/materialization/deployment authority sequence.

## 9. Proof-domain discipline

The old Gate A v3 repository PASS remains historical evidence at its exact audited SHA.

It does not prove the corrected SHA.

The target-host failure does not prove that every other Gate A v3 property is false.

The future fix must not inherit v3 CI, Astra PASS, fingerprint materialization, deployment authority or target-host evidence by implication.

No t0, P14D proof, Gate B, Product integration, scientific/economic readiness or real-capital authority follows from this finding or its correction.

