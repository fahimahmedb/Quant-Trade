# BUILDER MISSION — P0 EFFECTIVE UNIT DIGEST STABILITY V4 — 2026-09-20

Role: Builder.
Decision authority: Blue / Mission Control.
Architectural authority: `QUANT_NORTH_STAR.md`.

## 0. Exact implementation baseline

Branch:
`builder/p0-effective-unit-digest-stability-v4-2026-09-20`

Branch was created exactly from:
`2da079d8ad75c69eb3fc2990c512735cb4bdc02b`

Do not rebase onto Blue master or Product branches.

Read the current Blue specification from:
`blue/master-v2-2026-09-20:handoff/BLUE_TARGET_HOST_REAL_DEFECT_EFFECTIVE_UNIT_DIGEST_2026-09-20.md`

Current Blue checkpoint:
resolve the live HEAD of `blue/master-v2-2026-09-20`; at dispatch time the relevant checkpoint commit was
`13a0bfa56e42b075acfc3cc8ad60d8fb18c34cae`.

## 1. Confirmed defect

Target-host execution against the frozen v3 candidate showed:

- loaded systemd fragment byte-matched the frozen repository unit;
- no drop-ins were loaded;
- frozen semantic systemd checks passed;
- materialized effective-unit digest:
  `sha256:33d166b68a337947f7737ae659b386df88545867012ce88d0b30bcdbcf070b3d`;
- after service execution metadata changed, effective-unit digest:
  `sha256:c6394ef740c3f66c35e2920ebd4f21d27ff1417d11be5ab93b457f0f7e355c22`;
- one-use deployment authority remained present and unconsumed;
- no CHILD_LAUNCH_AUTHORIZED event was written;
- classification: `REAL_DEFECT`;
- target-host entrance: `FAIL / NO_T0`.

Restricted defect artifact binding:
`sha256:cb402bb3151a59708c6e3b6406323fe8671680b0e2785c9bb92ff47064639442`.

The defect mechanism is in:
`deploy/quant_sec_supervisor.py::_effective_systemd_definition`.

The code hashes the raw `systemctl show ExecStart` serialization. On the real systemd target that serialization contains transient runtime observations such as start/stop timestamps, PID, code and status. Those values can change after invocation without any unit semantic change, moving the acquisition-critical effective-unit digest.

## 2. Mission

Implement the smallest correct fix that makes the effective systemd digest stable under non-semantic runtime metadata changes while preserving fail-closed detection of actual configuration drift.

Do not widen scope.

Do not change target-host governance, t0 state, P14D state, Product integration or capital authorization.

## 3. Required properties

The corrected implementation must:

1. canonicalize `ExecStart` as stable configuration semantics rather than raw runtime serialization;
2. bind the executable path and argv actually configured for the qualifying supervisor;
3. exclude transient execution observations such as `start_time`, `stop_time`, `pid`, `code`, and `status`;
4. preserve fragment-byte equality enforcement;
5. preserve rejection of unbound drop-ins;
6. preserve WorkingDirectory verification;
7. preserve restart policy, restart delay, burst window, burst limit, kill mode, kill signal and stop-timeout checks;
8. preserve environment-file verification;
9. preserve qualifying-flag verification;
10. fail closed on unavailable or unparseable effective systemd configuration;
11. keep the effective-unit digest acquisition-critical;
12. avoid weakening fingerprint coverage merely to obtain a stable digest.

Prefer parsing/normalizing the structured `ExecStart` value to configuration-only fields. Do not solve this by omitting `ExecStart` from the digest.

## 4. Mandatory regression tests

Add discriminating tests proving:

- identical executable/argv but different PID/timestamps/exit code/status => identical effective-unit digest;
- same semantic unit before versus after a prior invocation => identical effective-unit digest;
- executable-path drift => rejected or changes the accepted digest according to the frozen contract;
- argv drift => rejected or changes the accepted digest;
- removal/change of `--qualifying` => rejected;
- restart/timing/kill/workdir/environment-file semantic drift => rejected;
- non-empty DropInPaths => rejected;
- loaded fragment byte mismatch => rejected;
- unparseable structured ExecStart => fail closed;
- materialize -> authorize -> later qualifying start is not invalidated solely because systemd execution observations changed.

Include a regression fixture representing the real target-host `ExecStart` form:

`{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I /opt/quant/deploy/quant_sec_supervisor.py --root /opt/quant --qualifying ; ignore_errors=no ; start_time=[...] ; stop_time=[...] ; pid=... ; code=exited ; status=... }`

## 5. Independent reproduction requirement

Before claiming the fix is complete, reproduce the old failure against the unmodified baseline or a focused test fixture:

`same semantic unit + changed runtime metadata -> digest changes`

Then show the corrected implementation flips only that discriminant:

`same semantic unit + changed runtime metadata -> digest stable`

and still catches:

`semantic unit drift -> blocked or fingerprint-changing`.

Do not use the corrected implementation as the only proof that the original defect existed.

## 6. Delivery discipline

- Keep commits scoped.
- Do not modify Blue governance files on this Builder branch except the Builder handoff/checkpoint for this mission.
- Run the relevant focused tests first, then the full repository CI-equivalent suite required by the existing Gate A v3 discipline.
- Push a durable Builder checkpoint if the mission spans multiple commits.
- Finish with a durable Builder handoff containing:
  - exact delivery SHA;
  - parent/baseline relation to `2da079d8...`;
  - changed paths;
  - old-defect reproduction;
  - new discriminant results;
  - exact local test commands/results;
  - exact GitHub Actions run ids/status once available;
  - residual risks/UNKNOWNs;
  - statement that Builder does not certify its own correction independently.

Do not freeze the candidate yourself.
Do not declare Gate A v4 PASS.
Do not declare target-host readiness.
Do not declare t0.

After delivery, stop and hand control back to Blue for reception and independent Astra/Red Team review.
