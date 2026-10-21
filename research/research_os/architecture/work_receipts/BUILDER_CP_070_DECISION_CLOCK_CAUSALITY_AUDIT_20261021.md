# CP070 — A frozen, reproducible decision can still use later information

Reacquired Builder 26e471d2877e5d04330fa9795484d63a6179e7e6, qualified
source 77c8ffbefb237b282c44e8ba5e3d8158bc590a22. Fresh native Oracle
adc3a43d1416826f15219026eb1737f8d4ab84e0 has no changes outside worker wake
receipts since integrated d2e58a7. No scientific state is replaced. Owner's
skipped network/production task remains excluded; all four authorities stay FALSE.

## Reproduce before code

Use the existing synthetic `test_economic_readiness_integration.fixture()` and
loaded synthetic `legacy()` corpus. Set only frozen protocol clock.decision_time
to 2026-10-15T08:00:00Z, then call the real `economic_test_readiness` compositor.
The package hash is 455498b462ff4e1d2727923a0d892ec2df11c0fb30b2677d049a73f7f8abacb9.

Both source snapshot and route become available at 09:00Z, data cutoff is 10:00Z,
freeze is 11:00Z. Result is READY_FOR_AUTHORIZED_ECONOMIC_TEST with no blockers;
every independent Validator check, including clock, PIT, frozen input binding,
protocol freeze and reproducibility, is PASS. No outcome was accessed. This is a
newly proposed, internally hash-consistent frozen package, not an attempt to
modify a previously retained freeze.

The clock predicate compares cutoff and decision separately to freeze, but does
not compare cutoff to decision. Thus CP066's source <= cutoff and CP068's frozen
input binding do not establish source <= decision. Hash agreement cannot repair
causal ordering. North Star's source PIT, valid clock and causal timing rules
require the missing comparison before READY admission.

## History / disposition

The shared Validator already owns CLOCK_DEFINITION_INVALID. History at 724e4c0
introduced this readiness path; CP021 (89c013b), CP066 (49e5f5c) and CP068
(77c8ffb) strengthened declarations, source coverage and freeze joins. None closes
this ordering relation. Reuse the existing clock gate, not a new registry,
time service, scheduler or dataset loader. The historical Factory outcome
firewall handles column/content access and is not a replacement for this clock
comparison; its prior SOURCE_IMPORT_REQUIRED disposition remains unchanged.

Next: require cutoff <= decision <= freeze, preserving equality and actual
timezone-aware instant comparison. Test complete composition and direct frozen
Validator input, ensuring all other checks stay PASS on the falsifying case.
Also verify offsets, microsecond boundaries and persisted frozen replay. Do not
invent rules about future execution timestamps or open any economic authority.
