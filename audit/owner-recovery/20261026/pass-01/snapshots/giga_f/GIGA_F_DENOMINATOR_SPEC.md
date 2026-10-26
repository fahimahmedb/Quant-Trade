# GIGA F denominator specification

Canonical implementation: `research/research_os/idea_feed/registry.py` and
`research/research_os/idea_feed/contracts.py`.
Durable path: `research/research_os/artifacts/idea-feed/journal.json` on the
canonical state ref, not a local cache or a second database.

Each event contains sequence, previous hash, timestamp, immutable idempotency key,
payload and event hash. A journal head binds its full ordered prefix. The existing
Git state store checks this prefix before atomically publishing under the exact
observed HEAD lease. Rewriting attribution, dropping events or substituting a
partial/malformed journal is rejected. Concurrent writers cannot both publish
from the same HEAD; the loser reconstructs fresh state. Git retains historical
versions. This does not claim resistance to an administrator rewriting Git history.

A seed identity hashes its complete validated contract, including source version,
birth cohort and prior exposure. JSON object key order does not change identity.
Repeated exact delivery is idempotent. New observations of an existing question
are retained as duplicate enrolments, with their own provenance and the original
root. Parametric variants share the root; their identities and parameters remain
visible. Reworded questions with the same economic identity require review.
Structural transfers retain their match/lineage but enroll a distinct root.
Known differences in actor/mechanism/constraint/transfer/rule structure can be
economically distinct even with similar text. Embeddings are not a novelty judge.

Root counts belong to root birth source/cohort, never to every later variant's
cohort. There is no root-identity input field that can turn a tweak into a new root.
Lineage, matching seed, variant identity and variant enrolment count are projected
from append-only birth events. Root denominator includes pending, parked and
blocked work, not just proposals or promoted work.

Supported state vocabulary:
`SEED_REGISTERED`, `DUPLICATE`, `VARIANT`, `BLOCKED_DATA`, `BLOCKED_AUTHORITY`,
`PARKED_LOW_POWER`, `PARKED_TRIGGER`, `KILLED_NO_EFFECT`, `KILLED_COSTS`,
`KILLED_CAPACITY`, `KILLED_LEAKAGE`, `PROMOTED`, `PENDING_CONFIRMATION`.
Birth classification cannot be overwritten. Parked/killed work needs an explicit
reopening reason. KILL/PROMOTE requires a canonical validated C0 adjudication and
exact prior Discovery Candidate binding; source code cannot synthesize verdicts.
No favorable or negative outcomes are manufactured in this mission.

`metrics()` returns SOURCE_YIELD_BY_COHORT: generated seeds, birth roots, enrolled
variants, tested variants, duplicates, mechanisms, actual technical Discovery
Candidate receipts, blocked/killed/parked/promoted/pending states and reopening
reasons. Experiments and tested variants remain zero: none ran. OOS/prospective/
economic pass, time-to-discovery and research cost remain UNKNOWN where evidence
is unavailable. Source task budgets are charged durably on completed source work;
failed/timeout/retried requests remain in existing canonical task receipts.
KILLED/TOTAL is never reported as a false-positive rate.

Scalability limit: the initial implementation replays a single growing journal
and publishes its full JSON representation. It favors transparent atomicity over
large-scale throughput; future partitioning must preserve this history and exact
identity/denominator semantics.
