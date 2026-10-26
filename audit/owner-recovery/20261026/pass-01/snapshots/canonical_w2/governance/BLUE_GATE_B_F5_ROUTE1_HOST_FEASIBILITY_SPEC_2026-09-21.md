# BLUE — GATE B F5 ROUTE-1 HOST FEASIBILITY SPEC — 2026-09-21

## 0. Purpose

Determine whether Gate-B lifecycle/sanitization finding F5 can be closed WITHOUT
changing frozen V4, using sealed target-host infrastructure only.

This is READ-ONLY FEASIBILITY inspection.

No mutation is authorized.

## 1. Exact question

Can the exact frozen V4 service:
- keep identical loaded unit / ExecStart / WorkingDirectory / code/interpreter;
- write all destructive-campaign state only to a dedicated synthetic reservoir;
- have real SEC egress made externally impossible;
- preserve the future qualifying reservoir untouched;
- preserve lifecycle/evidence provenance;
- stop before switching reservoir bindings;
- then rebind the preserved future reservoir for later t0/Gate C;

without a production code/config semantic change?

## 2. Inspect read-only

At minimum determine availability/current state of:
- nftables/iptables/firewall tooling;
- systemd/network namespace or host firewall mechanisms usable without unit/drop-in
  semantic change;
- mount topology and whether an external bind/source swap can preserve exact
  service-visible path;
- existing mount units/fstab dependencies;
- filesystem identities for candidate synthetic and preserved state locations;
- whether service requester/network path can be externally blocked and independently
  evidenced;
- whether service view can use exact frozen V4 while state reservoir is externally
  selected;
- whether required operations can be represented in a sealed mutation allowlist.

Do not test the mutation. Do not create reservoirs. Do not add firewall rules.

## 3. Required conclusion

Exactly one:

`F5_ROUTE1_FEASIBILITY = PROVABLY_FEASIBLE_FOR_SEALED_ACTIVATION`

with exact future operations/evidence requirements,

or

`F5_ROUTE1_FEASIBILITY = NOT_PROVEN`

with the exact missing host capability/proof and whether Route 2 production
testability work is required.

No Gate-B PASS follows.
