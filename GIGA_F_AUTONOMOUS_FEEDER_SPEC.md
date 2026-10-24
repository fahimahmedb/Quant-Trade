# GIGA F autonomous feeder specification

Implementation: `research/research_os/idea_feed/feeder.py`.
Configuration: `research/research_os/runtime/IDEA_FEED_POLICY.json`.
Binding: existing `oracle_worker.py`, `worker_stages.py`, `github_state.py` and
`runtime/WORKFLOW_LANES.json`. No alternate scheduler exists.

FrontierHealth observes eligible unprocessed seeds, discovery/candidate/experiment
backlogs, source/mechanism diversity, oldest question age, blocked and duplicate
fractions, declared research capacity, independent validation capacity and active
source requests. It returns REPLENISH, HOLD, BACKPRESSURE or BLOCK, with observations,
thresholds and reasons. Capacity values are configured declarations, not measured
scientific power or production quotas.

REPLENISH is possible while downstream tasks exist. An empty queue alone does not
establish health or success. Too many unprocessed seeds, saturated downstream
backlogs, excessive duplicate fraction, absent independent capacity or exhausted
compute budget produces NOOP_BACKPRESSURE. Missing sources or a frontier dominated
by blocked work requires repair and reports BLOCK. Active source work causes HOLD.

Budgets include per-source/cohort allocation, maximum seeds per request and maximum
cohort compute units. Compute units here bound reserved question-generation work,
not measured CPU or economic tests. Sources are explored by least completed budget
usage and stable source identity; future productivity is UNKNOWN. No optimizer
allocates according to historical outcome fields. Every source gets the configured
minimum exploration opportunity before repeated work; retries are the original
canonical task, not new roots or new tasks. A source version/descriptor is admitted
at most once per cohort; new versions or cohorts are explicit future source work.

Admission derives one existing SOURCE_QUALIFICATION task with content/version/policy
pins. The source_qualification capability already exists in evidence_data. Existing
Oracle owns priority selection, current-blob checks, lease generations, retry-after,
three-attempt retry ceiling, receipts, events and whole-ref CAS. The feeder neither
launches workers nor executes a producer in an admission wake.

`source_ingestion` rechecks the pinned source and health, registers every question
and variant, adds exposures and completion accounting, then commits atomically.
`policy_intake` is a later wake and requires that durable source completion. It
uses the unchanged Multi-Source A/B/C/barrier/Proposal Ledger contracts. Separate
qualified Research Intelligence is still required by existing Discovery.

A timeout/model unavailable exception follows ordinary BackendUnavailable retries.
Malformed/stale source or policy fails closed. Crash before publication exposes no
partial journal, event or receipt; lease expiry permits recovery. Lost publication
acknowledgement is recovered from durable stage completion. Source retries and
concurrent ingress cannot replace prior denominator history.

The committed policy is disabled and fixture-only. Enable an isolated copy with
`scripts/demo_giga_f_idea_feed.py`; live configuration/activation continues through
the existing canonical release process. All five mission authority flags stay FALSE.
