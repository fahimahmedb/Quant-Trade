# BLUE — GATE B F5 ROUTE-1 HOST EVIDENCE CLOSURE — 2026-09-21

## 0. Purpose

Close the exact evidence gaps left by:
`operator/gate-b-f5-route1-host-feasibility-2026-09-21@a5493f052c458e1bbf76e00cbc4943dca8632e71`.

Prior disposition:
`F5_ROUTE1_FEASIBILITY = NOT_PROVEN`.

This is NOT a conclusion that Route 1 is impossible.

## 1. Missing proofs to close

### N1 — external network impossibility

Read-only determine whether the target host has an authoritative mechanism that
could, under a later sealed activation, make ALL frozen-V4 real SEC HTTPS egress
impossible without changing:
- loaded unit bytes;
- ExecStart;
- WorkingDirectory;
- frozen V4 code;
- interpreter binding.

Evidence must identify:
- authoritative firewall mechanism(s) present;
- IPv4 and IPv6 coverage;
- relevant output/egress path;
- whether service traffic can bypass the mechanism;
- whether a future rule can be scoped and later rolled back under a finite allowlist;
- exact pre/post evidence commands.

No rule may be installed now.

### N2 — synthetic state reservoir binding

Read-only determine whether the current service-visible writable state path can,
under a later sealed activation, be rebound to a unique synthetic reservoir while:
- exact service-visible path remains unchanged;
- preserved future qualifying reservoir is not writable by the campaign;
- exact frozen release/service binding remains unchanged;
- service can be proven stopped before each reservoir switch;
- mount source/destination can be bound by opaque filesystem identity;
- rollback/rebind to future qualifying reservoir is auditable.

Evidence must include current mount/fstab/systemd-mount topology and filesystem
identities sufficient to decide feasibility.

No mount/reservoir operation may occur now.

## 2. Required final classification

Exactly one:

`F5_ROUTE1_HOST_EVIDENCE = PASS_ROUTE1_FEASIBLE`

only if both N1 and N2 are positively established as future-sealable host
capabilities,

or

`F5_ROUTE1_HOST_EVIDENCE = BLOCKED_ROUTE1_NOT_PROVEN`

with the exact missing/negative capability.

If a hard negative proves Route 1 impossible without service-semantic change, say:

`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = TRUE`

Otherwise:
`ROUTE2_PRODUCTION_TESTABILITY_WORK_REQUIRED = NOT_YET_PROVEN_REQUIRED`.

## 3. Safety

READ ONLY.

Forbidden:
- firewall mutation;
- mount mutation;
- reservoir creation/deletion;
- systemctl lifecycle mutation;
- unit/drop-in edits;
- release materialization;
- network requests;
- P0 state mutation.

Raw host evidence is RESTRICTED.
Public handoff contains only safe summaries and opaque digests.

No Gate-B PASS/t0 follows from this mission.
