# CP065 — Resume excluding the network task; audit readiness provenance

Owner steering: skip the network/production access task and continue independent
whole-North-Star work. Preserve CP064's proposal, do not retry its stale draft,
probe blocked endpoints or modify production. Four authority membranes stay closed.

Reacquired clean Builder 6c013d75d0210e6fdde9796ab0365ce1df838685, native Oracle
8a506fa340457b8b880b4dcc8d1573b7378e6559 and unchanged North Star blob a328b4e6.
Oracle delta remains wake receipts only; no scientific state overwritten.

## Reproduced gaps before implementation

Use only the existing synthetic readiness fixtures, no source acquisition or
outcomes. economic_test_readiness accepts READY when route availability is
10:15 or 10:59, snapshot claims availability 09:00, data cutoff is 10:00 and
freeze is 11:00. Route qualification checks freeze, while Validator checks only
the separately supplied snapshot clock. Both clocks must clear the data cutoff;
never replace the snapshot's claim silently with a different time.

The direct independent readiness Validator also accepts a hash-rebound bundle
with two source snapshots but one PIT row: evidence is nonempty but not joined
per snapshot. A PIT row must refer to its exact snapshot; missing, extra or
mismatched rows cannot prove all source inputs qualified.

The same independent Validator fills absent/empty/false validator_id with a
synthetic default, and accepts numeric actor identity. These must be explicit
literal non-null identifiers. Wrapper-required identities do not protect direct
Validator callers. Different valid actor names establish only the existing
metadata independence ceiling, not process/cognitive independence.

## Search history / reuse decision

Source-clock CP026 and native claim-admission CP040 already enforce explicit
clock/actor fields at their own boundaries; they do not enforce the join found
here. validation_readiness last changed at CP021, and its snapshot provenance
predicate checks only nonempty lists. Reuse current route qualification,
Validator checks/reason codes, freeze/replay and readiness composition. No new
validation engine, task store, historical result reinterpretation or registry.

Carry each snapshot hash and qualified-route availability into PIT metadata.
Require exact source-reference/PIT multiset coverage (duplicate content addresses
may represent declared aliases, never independent trials), and both supplied
clocks no later than data cutoff. Preserve explicit offset semantics and raw
input values; no timestamp rewrite. Require explicit producer/validator IDs and
retain distinctness. Existing direct fixture must now supply the hash binding;
previous persisted receipts are not rewritten or claimed invalid retroactively.
Adversarial tests must independently rebind hashes, so unrelated freeze checks
cannot masquerade as proof of the new source guard.

Next: implement this single provenance-admission package, run affected and broader
qualification, checkpoint, then reassess other independently executable depth.
