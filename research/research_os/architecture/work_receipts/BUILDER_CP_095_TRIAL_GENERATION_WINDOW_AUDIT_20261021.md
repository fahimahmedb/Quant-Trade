# CP095 — Trial generation time not bound to its research window

Audited executable: 34c680316c62cab414b9c3c9b485574267236c8e, documentation
head b238a9fec4d8e54db55efc5a1275f1c76e19cfbc. Before-code evidence.

## Reacquire and history

North Star remains controlling (blob a328b4e); CP085 remains the breadth baseline.
Normal Git reads/fetch work in this session. Builder matches remote. Oracle
eeaa996b2734c2dae07a9f0edaef542fb0104ddd differs from integrated d2e58a7
only in worker wake receipts; no source/scientific delta to integrate. Blue
9026e4d and Site source d14b96c remain unchanged. No production probe.

Searched all-branch commit subjects for trial time/window and epoch window;
searched core, stage executor, tests and previous receipts for research_window
and generated_at. Existing native execution admission uses start <= now < end.
Core hashes generated_at without parsing it. Native trial integrity rebuilds the
trial/hash/counts but also does not bind generation time to the epoch window.
The pure adapter binds epoch IDs but omits this temporal admission. The V2 spec
explicitly distinguishes generation time from knowledge cutoff and export time.
CP071 causal economic clock and CP075/090 subject lineage do not establish this.

## Actual reproducible mismatch

Using the existing JSON pure fixture, changing only trial.generated_at to each of
2026-10-19T00:00:00Z (before start), 2026-10-27T01:00:00Z (exclusive end),
and not-a-timestamp returns READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY each time.
Using tests.test_research_os_native_trial_lineage.fixture and rehash(trial),
_assert_native_trial_lineage also accepts before-start, native exclusive-end
2026-12-31T00:00:00Z, and not-a-timestamp. IDs, proposals, source bindings and
all counts otherwise remain unchanged. These are synthetic metadata mutations;
no outcome values, market observations or actual model calls were involved.
Native acceptance here is a lineage-helper result, not proof of later economic
PASS or export. Executing a challenge now inside the window cannot prove that
the referenced generation occurred inside it.

## Reuse / build / no-build

Reuse existing timezone-aware parser and the established half-open research
window rule. One shared pure trial/epoch temporal guard should run in composed
qualification before export and native challenge before retrieval/base execution.
Fail closed on missing/malformed/naive generation time and malformed window;
retain the original literal timestamps and hashes for valid input. No wall-clock
lookup, no export-time inference, no new scheduler, no historical trial rewrite.
Boundary/offset tests must exercise both consumers and preserve the current
valid fixture receipt. Existing native execution and export cutoff checks remain.
Four authorities remain literally FALSE. No experiment, prospective capture,
active/sealed outcome read, canonical Oracle write, deployment or network change.
